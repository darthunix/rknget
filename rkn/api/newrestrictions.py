from db import blockdata

import ipaddress
import api.caching

import api.restrutils

"""
This module only operates with Resources data
I had to switch returned datasets to a list type to make those json serialisable
"""


def _makeUniqList(x):
    if not x:
        return []
    elif type(x) is str:
        return [x]
    elif hasattr(x, '__iter__'):
        return list(set(x))
    return [x]


def getBlockedDataSet(entitytypes, blocktypes, srcenttys=None, **kwargs):
    """
    Returns blocked data set
    :param entitytypes: target entity type set
    :param blocktypes: content blocktype set
    :param srcenttys: additional entity type set for excessive blockings
    :return: set of strings
    """
    return blockdata.getBlockedData(
        _makeUniqList(entitytypes),
        _makeUniqList(blocktypes),
        _makeUniqList(srcenttys))


def getBlockedPrefixes(collapse=False, ipv6=False, **kwargs):
    """
    Returns the complete list of prefixes to restrict.
    :param collapse: merge and minimize IPs and networks
    :param ipv6: use ipv6 entities
    :return: The total and the list of ip subnets, using /32 for ips
    """
    blocktype = 'ip'
    if ipv6:
        entitytypes = ['ipv6', 'ipv6subnet']
    else:
        entitytypes = ['ip', 'ipsubnet']
    prefixes = map(ipaddress.ip_network,
                  api.caching.getDataCached(
                      getBlockedDataSet,
                      entitytypes,
                      blocktype,
                      **kwargs)
                  )
    if collapse:
        prefixes = ipaddress.collapse_addresses(prefixes)
    return list(map(str, prefixes))


def getBlockedDomains(collapse=False, wc_asterize=False, **kwargs):
    """
    Brand new procedure. Uses domain tree to cleanup excess domains.
    :param collapse: merge domains if wildcard analogue exists
    :param wc_asterize: merge domains if wildcard analogue exists
    :return: list of 2 lists: domains and wildcard domains
    """
    domains = api.caching.getDataCached(
        getBlockedDataSet,
        'domain',
        'domain',
        **kwargs)
    wdomains = api.caching.getDataCached(
        getBlockedDataSet,
        'domain-mask',
        'domain-mask',
        **kwargs)

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
    return list( map(list, api.restrutils.dnslistmerged(dnsmap, wc_asterize)) )


def getBlockedDNS(collapse=False, **kwargs):
    """
    Returns domains list only.
    :param collapse: merge domains if wildcard analogue exists.
    :return: domains set
    """
    if not collapse:
        return list(api.caching.getDataCached(
            getBlockedDataSet,
            'domain',
            'domain',
            **kwargs))
    # Else
    return api.caching.getDataCached(
        getBlockedDomains,
        collapse=True,
        **kwargs)[0]


def getBlockedWildcardDNS(collapse=False, wc_asterize=False, **kwargs):
    """
    Returns wildcard domains list only.
    :param collapse: merge domains if wildcard analogue exists.
    :param wc_asterize: merge domains if wildcard analogue exists
    :return: wildcard domains set
    """
    if not collapse:
        wdomains = api.caching.getDataCached(
            getBlockedDataSet,
            'domain-mask',
            'domain-mask',
            **kwargs)
        if wc_asterize:
            wdomains = map(lambda s: '*.'+s, wdomains)
        return list(wdomains)
    # Else
    return api.caching.getDataCached(
        getBlockedDomains,
        collapse=True,
        wc_asterize=True,
        **kwargs)[1]


def getBlockedIP(ipv6=False, as_prefixes=False, **kwargs):
    """
    Returns the list of /32 prefixes to restrict.
    :param ipv6: use ipv6 entities
    :param as_prefixes: return a prefix form (ip.ad.ddr.ess/32)
    :return: Only IP list
    """
    blocktype = 'ip'
    if ipv6:
        entitytypes = ['ipv6']
    else:
        entitytypes = ['ip']
    if as_prefixes:
        func = ipaddress.ip_network
    else:
        func = ipaddress.ip_address
    prefixes = map(func,
                  api.caching.getDataCached(
                      getBlockedDataSet,
                      entitytypes,
                      blocktype,
                      **kwargs)
                  )
    return list(map(str, prefixes))


def getBlockedIPSubnets(ipv6=False, **kwargs):
    """
    Returns the list of prefixes to restrict.
    :param ipv6: use ipv6 entities
    :return: Only IP subnets list
    """
    blocktype = 'ip'
    if ipv6:
        entitytypes = ['ipv6subnet']
    else:
        entitytypes = ['ipsubnet']
    prefixes = map(ipaddress.ip_network,
                  api.caching.getDataCached(
                      getBlockedDataSet,
                      entitytypes,
                      blocktype,
                      **kwargs)
                  )
    return list(map(str, prefixes))


def getBlockedHTTP(proto=False, **kwargs):
    """
    :return URLs strings list
    """
    urlset = api.caching.getDataCached(
        getBlockedDataSet,
        'default',
        'http',
        **kwargs)
    if not proto:
        return list(urlset)
    else:
        return [api.restrutils.strcut(u,'http://') for u in urlset]


def getBlockedHTTPS(proto=False, **kwargs):
    """
    :return SSL URLs strings list
    """
    urlset = api.caching.getDataCached(
        getBlockedDataSet,
        'https',
        'default',
        **kwargs)
    if not proto:
        return list(urlset)
    else:
        return [api.restrutils.strcut(u,'https://') for u in urlset]


def getBlockedURLs(proto=False, **kwargs):
    """
    :param proto: Cuts protocol, so that merges the same
    :return: All URLs, either http or https
    """
    # It may be sometimes longer, but more universal
    return(list(set.union(
        set(api.caching.getDataCached(
            getBlockedHTTP,
            proto=proto,
            **kwargs)),
        set(api.caching.getDataCached(
            getBlockedHTTPS,
            proto=proto,
            ** kwargs))
    )))


