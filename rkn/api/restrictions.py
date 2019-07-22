from db.blockdata import BlockData
import re
import ipaddress
from functools import reduce

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
    :return: The total and the list of ip subnets, using /32 for ips
    """
    ipsall = getBlockedIPList(connstr, collapse, ipv6)
    return list(map(str, ipsall))


def mergednsmap(iswc, dnslst):
    """
    Not used to avoid 2 function calls, and array walking twice
    :param iswc: Is wildcards needed, True/False
    :param dnslst: the list of domains-as-suffix-list
    :return: the set of domains
    """
    merger = lambda lst: ".".join(lst[:-2].__reversed__()) if lst[-1] == iswc else None
    return set(map(merger,dnslst)) - {None}


def dnslistmerged(dnslist, wc_asterize=False):
    """
    Makes textual domain from suffixes list for each in he given list
    :param dnslist: the list of domains-as-suffix-list
    :param wc_asterize: appending *. to each wildcard domain
    :return: two sets, domains and wdomains
    """
    domains = set()
    wdomains = set()
    # Setting wildcard asterisk prefix if required
    wc_sign = ''
    if wc_asterize:
        wc_sign = '*.'

    for d in dnslist:
        if d[-1]:
            wdomains.add(wc_sign + ".".join(d[:-2].__reversed__()))
        else:
            domains.add(".".join(d[:-2].__reversed__()))
    return domains, wdomains


def mapdnstree(dnstree):
    """
    Restores each domain in the given DNSD tree as a list of suffixes.
    Each entry of the returned list is finished with "" as a terminator
    and boolean indicator of wildcardness:
    [['com','domain','sub','',False], ...]
    :param dnstree: DNS tree
    :return: domain entries as suffixes list
    """
    return [
        [k,v] for k,v in dnstree.items()
        if type(v) != dict
            ] + \
        reduce(lambda x,y: x+y,
           map(lambda x: [[x[0]]+i for i in x[1]],
               [[k,mapdnstree(v)] for k,v in dnstree.items()
                if type(v) == dict]
               ),
           [])


def mkdnstree(domains, wdomains):
    """
    Makes DNS tree starting from 0LD as empty string.
    Each leaf ends up with auxiliary {'': bool} attribute
    to differ an entry from its subdomain and to distinguish
    wildcard domains which excludes entire subtree itself.
    :param domains: domains iterable
    :param wdomains: wdomains iterable
    :return:
    """
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


def getBlockedDomains(connstr, collapse=True, wc_asterize=False):
    """
    Brand new procedure. Uses domain tree to cleanup excess domains.
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :param collapse: merge domains if wildcard analogue exists
    :param wc_asterize: merge domains if wildcard analogue exists
    :return: 2 sets: domains and wildcard domains
    """
    bldt = BlockData(connstr)
    domains = bldt.getBlockedResourcesSet('domain')
    wdomains = bldt.getBlockedResourcesSet('domain-mask')
    if not collapse:
        if wc_asterize:
            wdomains = map(lambda s: '*.'+s, wdomains)
        return [list(domains),
                list(wdomains)]
    # Building domains tree
    dnstree = mkdnstree(domains,wdomains)
    # Coalescing the tree to a list of domain-as-lists
    # Starting with TLD, not 0LD
    dnsmap = mapdnstree(dnstree[""])
    # Making text domains and wdomains again
    return list( map(list,dnslistmerged(dnsmap, wc_asterize)) )
