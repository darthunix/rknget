from db import blockdata

import ipaddress

import api.restrutils

"""
This module only operates with Resources data
I had to switch returned datasets to list to make those json serialisable
"""


def _getBlockedDataList(entityname):
    """
    Function for debug purposes
    :return: entities set
    """
    return list(blockdata.getBlockedResourcesSet(entityname))


def getBlockedHTTP():
    """
    :return URLs strings list
    """
    return list(blockdata.getBlockedResourcesSet('http'))


def getBlockedHTTPS():
    """
    :return URLs strings list
    """
    return list(blockdata.getBlockedResourcesSet('https'))


def getBlockedIPsFromSubnets():
    """
    Explodes restricted ip subnets into IP list.
    :return: IP list.
    """
    ipsubs = {ipaddress.ip_network(addr)
              for addr in blockdata.getBlockedResourcesSet('ipsubnet')}

    return [str(host) for ipsub in ipsubs for host in ipsub.hosts()]


def getBlockedIPList(collapse=True, ipv6=False):
    """
    Function for getting only IP blockings as IPAddress objects.
    :param collapse: merge and minimize IPs and networks
    :param ipv6: use ipv6 entities
    :return: The list of ip subnets, using /32 for ips.
    """
    if ipv6:
        ips = [ipaddress.ip_network(addr) for addr in blockdata.getBlockedResourcesSet('ipv6')]
        ipsubs = [ipaddress.ip_network(addr) for addr in blockdata.getBlockedResourcesSet('ipv6subnet')]
    else:
        ips = [ipaddress.ip_network(addr) for addr in blockdata.getBlockedResourcesSet('ip')]
        ipsubs = [ipaddress.ip_network(addr) for addr in blockdata.getBlockedResourcesSet('ipsubnet')]
    ipsall = ips + ipsubs
    if collapse:
        return list(ipaddress.collapse_addresses(ipsall))
    return list(ipsall)


def getBlockedIPs(collapse=True, ipv6=False):
    """
    Converts objects to text.
    :param collapse: merge and minimize IPs and networks
    :param ipv6: use ipv6 entities
    :return: The total and the list of ip subnets, using /32 for ips
    """
    ipsall = getBlockedIPList(collapse, ipv6)
    return list(map(str, ipsall))


def getBlockedDomains(collapse=True, wc_asterize=False):
    """
    Brand new procedure. Uses domain tree to cleanup excess domains.
    :param collapse: merge domains if wildcard analogue exists
    :param wc_asterize: merge domains if wildcard analogue exists
    :return: 2 sets: domains and wildcard domains
    """
    domains = blockdata.getBlockedResourcesSet('domain')
    wdomains = blockdata.getBlockedResourcesSet('domain-mask')
    if not collapse:
        if wc_asterize:
            wdomains = map(lambda s: '*.'+s, wdomains)
        return [list(domains),
                list(wdomains)]
    # Building domains tree
    dnstree = api.restrutils.mkdnstree(domains,wdomains)
    # Coalescing the tree to a list of domain-as-lists
    # Starting with TLD, not 0LD
    dnsmap = api.restrutils.mapdnstree(dnstree[""])
    # Making text domains and wdomains again
    return list( map(list,api.restrutils.dnslistmerged(dnsmap, wc_asterize)) )


def getBlockedDNS(collapse=True):
    """
    Returns domains list only.
    :param collapse: merge domains if wildcard analogue exists.
    Calls getBlockedDomains, no way else.
    :return: domains set
    """
    if not collapse:
        return list(blockdata.getBlockedResourcesSet('domain'))
    # Else
    return getBlockedDomains(collapse=True)[0]


def getBlockedWildcardDNS(collapse=True, wc_asterize=False):
    """
    Returns wildcard domains list only.
    :param collapse: merge domains if wildcard analogue exists.
    Calls getBlockedDomains, no way else.
    :return: wildcard domains set
    """
    if not collapse:
        wdomains = blockdata.getBlockedResourcesSet('domain-mask')
        if wc_asterize:
            wdomains = map(lambda s: '*.'+s, wdomains)
        return list(wdomains)
    # Else
    return getBlockedDomains(collapse=True, wc_asterize=wc_asterize)[1]


def getFairlyBlockedIPs(collapse=True, ipv6=False):
    """
    Function for getting only IP blockings as IPAddress objects.
    :param collapse: merge and minimize IPs and networks
    :param ipv6: use ipv6 entities
    :return: The list of ip subnets, using /32 for ips.
    """
    if ipv6:
        ips = [ipaddress.ip_network(addr) for addr in blockdata.getFairlyBlockedResourcesSet('ipv6')]
        ipsubs = [ipaddress.ip_network(addr) for addr in blockdata.getFairlyBlockedResourcesSet('ipv6subnet')]
    else:
        ips = [ipaddress.ip_network(addr) for addr in blockdata.getFairlyBlockedResourcesSet('ip')]
        ipsubs = [ipaddress.ip_network(addr) for addr in blockdata.getFairlyBlockedResourcesSet('ipsubnet')]
    ipsall = ips + ipsubs
    if collapse:
        return list(ipaddress.collapse_addresses(ipsall))
    return list(map(str, ipsall))

