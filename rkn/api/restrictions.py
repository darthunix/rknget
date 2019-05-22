from db.blockdata import BlockData
import re
import ipaddress
from functools import reduce, lru_cache

"""
This module only operates with Resources data
I had to switch returned datasets to list to make those json serialisable
"""


def _getBlockedDataList(connstr, entityname):
    """
    Function for debug purposes
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return: entities set
    """
    return list(BlockData(connstr).getBlockedResourcesSet(entityname))


def getBlockedHTTP(connstr):
    """
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return URLs strings list
    """
    return list(BlockData(connstr).getBlockedResourcesSet('http'))


def getBlockedHTTPS(connstr):
    """
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return URLs strings list
    """
    return list(BlockData(connstr).getBlockedResourcesSet('https'))


def getBlockedIPsFromSubnets(connstr):
    """
    Explodes restricted ip subnets into IP list.
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return: IP list.
    """
    ipsubs = {ipaddress.ip_network(addr)
              for addr in BlockData(connstr).getBlockedResourcesSet('ipsubnet')}

    return [str(host) for ipsub in ipsubs for host in ipsub.hosts()]


def getBlockedIPList(connstr, collapse=True, ipv6=False):
    """
    Complementary function for getting only IP list
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :param collapse: merge and minimize IPs and networks
    :param ipv6: use ipv6 entities
    :return: The total and the list of ip subnets, using /32 for ips.
    """
    bldt = BlockData(connstr)
    if ipv6:
        ips = [ipaddress.ip_network(addr) for addr in bldt.getBlockedResourcesSet('ipv6')]
        ipsubs = [ipaddress.ip_network(addr) for addr in bldt.getBlockedResourcesSet('ipv6subnet')]
    else:
        ips = [ipaddress.ip_network(addr) for addr in bldt.getBlockedResourcesSet('ip')]
        ipsubs = [ipaddress.ip_network(addr) for addr in bldt.getBlockedResourcesSet('ipsubnet')]
    ipsall = ips + ipsubs
    if collapse:
        return list(ipaddress.collapse_addresses(ipsall))
    return list(ipsall)


def getBlockedIPs(connstr, collapse=True, ipv6=False):
    """
    Merges IPs into IP subnets containing first ones.
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :param collapse: merge and minimize IPs and networks
    :param ipv6: use ipv6 entities
    :return: The total and the list of ip subnets, using /32 for ips; IPs count
    """
    ipsall = getBlockedIPList(connstr, collapse, ipv6)
    ipNum = sum(map(lambda x: x.num_addresses, ipsall))
    return [list(map(str, ipsall)), ipNum]


def getBlockedDomains(connstr, collapse=True):
    """
    We don't need to block domains if the same wildcard domain is blocked
    We don't need to block 3-level wildcard if 2-level wildcard is blocked
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :param collapse: merge domains if wildcard analogue exists
    :return: 2 sets: domains and wildcard domains
    """
    bldt = BlockData(connstr)
    domains = bldt.getBlockedResourcesSet('domain')
    wdomains = bldt.getBlockedResourcesSet('domain-mask')
    if not collapse:
        return [list(domains), list(wdomains)]
    # Dedupe wdomains
    wds = wdomains.copy()
    for wd in wds:
        regex = re.compile('''^.+\.''' + wd + '''$''')
        for wdom in wds:
            if regex.fullmatch(wdom):
                # Using discard to ignore redelete.
                wdomains.discard(wdom)

    # Dedupe domains with wdomains
    for wd in wdomains.copy():
        regex = re.compile('''^(.*[^.]\.)?''' + wd + '''$''')
        for dom in domains.copy():
            if regex.fullmatch(dom):
                # Using discard to ignore redelete.
                domains.discard(dom)

    return [list(domains), list(wdomains)]


def mergednsmap(iswc, dnslst):
    merger = lambda lst: ".".join(lst[:-2].__reversed__()) if lst[-1] == iswc else None
    return set(map(merger,dnslst)) - {None}


def dnslistmerged(dnslist):
    domains = set()
    wdomains = set()
    for d in dnslist:
        if d[-1]:
            wdomains.add(".".join(d[:-2].__reversed__()))
        else:
            domains.add(".".join(d[:-2].__reversed__()))
    return [list(domains), list(wdomains)]


@lru_cache(maxsize=512)
def mapdnstree(dnstree):
     return [
        [k,v] for k,v in dnstree.items()
        if type(v) != dict
            ] + \
     reduce(lambda x,y: x+y,
            map(lambda x: [[x[0]]+i for i in x[1]],
                [[k,mapdnstree(v)] for k,v in dnstree.items()
                 if type(v) == dict]
                ),
            []
            )


def mkdnstree(domains, wdomains):
    dnstree = {"": {}}
    for d in domains:
        dnstree_ptr = dnstree.setdefault("")
        for i in d.split('.').__reversed__():
            dnstree_ptr = dnstree_ptr.setdefault(i, {})
        dnstree_ptr[""] = False

    for w in wdomains:
        dnstree_ptr = dnstree.setdefault("")
        for i in w.split('.').__reversed__():
            dnstree_ptr = dnstree_ptr.setdefault(i, {})
        dnstree_ptr.clear()
        dnstree_ptr[""] = True
    return dnstree


def getBlockedDomainsNew(connstr, collapse=True):
    """
    We don't need to block domains if the same wildcard domain is blocked
    We don't need to block 3-level wildcard if 2-level wildcard is blocked
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :param collapse: merge domains if wildcard analogue exists
    :return: 2 sets: domains and wildcard domains
    """
    bldt = BlockData(connstr)
    domains = bldt.getBlockedResourcesSet('domain')
    wdomains = bldt.getBlockedResourcesSet('domain-mask')
    if not collapse:
        return [list(domains), list(wdomains)]
    # Building domains tree

    dnstree = mkdnstree(domains,wdomains)
    dnsmap = mapdnstree(dnstree)
    return dnslistmerged(dnsmap)