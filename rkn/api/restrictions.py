from rkn.db.blockdata import BlockData
import re
import ipaddress

"""
This module only operates with Resources data
"""


def _getBlockedDataSet(connstr, entityname):
    """
    Function for debug purposes
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return: entities set
    """
    return BlockData(connstr).getBlockedResourcesSet(entityname)


def getBlockedHTTP(connstr):
    """
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    """
    return BlockData(connstr).getBlockedResourcesSet('http')


def getBlockedHTTPS(connstr):
    """
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    """
    return BlockData(connstr).getBlockedResourcesSet('https')


def getBlockedIPsFromSubnets(connstr):
    """
    Explodes restricted ip subnets into IP list.
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return: IP list.
    """
    ipsubs = {ipaddress.ip_network(addr)
              for addr in BlockData(connstr).getBlockedResourcesSet('ipsubnet')}

    return {str(host) for ipsub in ipsubs for host in ipsub.hosts()}


def getBlockedIPsMerged(connstr):
    """
    Merges IPs into IP subnets containing first ones.
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return: The total and the set of ip subnets, using /32 for ips.
    """
    bldt = BlockData(connstr)
    ips = [ipaddress.ip_network(addr) for addr in bldt.getBlockedResourcesSet('ip')]
    ipsubs = [ipaddress.ip_network(addr) for addr in bldt.getBlockedResourcesSet('ipsubnet')]
    ipsall = ips + ipsubs
    return set(map(str, ipaddress.collapse_addresses(ipsall))),\
           sum(map(lambda x: x.num_addresses, ipsall))


def getBlockedDomainsMerged(connstr):
    """
    We don't need to block domains if the same wildcard domain is blocked
    We don't need to block 3-level wildcard if 2-level wildcard is blocked
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return: 2 sets: domains and wildcard domains
    """
    bldt = BlockData(connstr)
    domains = bldt.getBlockedResourcesSet('domain')
    wdomains = bldt.getBlockedResourcesSet('domain-mask')
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

    return domains, wdomains

if __name__ == '__main__':
    import cgi, json
    from dbconn import connstr

    fields = cgi.FieldStorage()
    print( json.dumps(fields['method'](connstr)) )