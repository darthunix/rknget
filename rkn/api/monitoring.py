from db import dbmon

import api.restrictions
import api.caching
import ipaddress
from datetime import datetime

"""
This module provides API for monitoring
And every function must return strictly single scalar value.
Return type doesn't matters, but must be serializable.
"""


def testConn(**kwargs):
    """
    Tests a connection.
    :return:
    """
    try:
        dbmon.testDBConn()
        return 0
    except:
        return 1


def getLastExitCode(procname):
    exit_code = dbmon.getLastExitCode(procname)
    if exit_code is None:
        """Eleven english gentlemen are raping the german women..."""
        return 9
        """...Two english gentlemen are going away"""
    return exit_code


def getBlockedIPCount(ipv6=False, **kwargs):
    prefixes = map(ipaddress.ip_network,
                   api.caching.getDataCached(
                       api.restrictions.getBlockedPrefixes,
                       collapse=False,
                       ipv6=ipv6,
                       **kwargs)
                  )
    return sum(map(lambda x: x.num_addresses, prefixes))


def getBlockedSubnetsCount(collapse=False, ipv6=False, **kwargs):
    prefixes = api.caching.getDataCached(
        api.restrictions.getBlockedPrefixes,
        collapse=collapse,
        ipv6=ipv6,
        **kwargs)
    return len(prefixes)


def getBlockedDNSCount(collapse=False, **kwargs):
    domains = api.caching.getDataCached(
        api.restrictions.getBlockedDNS,
        collapse=collapse,
        **kwargs)
    return len(domains)


def getBlockedWildcardDNSCount(collapse=False, **kwargs):
    wdomains = api.caching.getDataCached(
        api.restrictions.getBlockedWildcardDNS,
        collapse=collapse,
        **kwargs)
    return len(wdomains)


def getBlockedURLsCount(**kwargs):
    # It could be done with count() SQL,
    # but cache reuse is preferred.
    wdomains = api.caching.getDataCached(
        api.restrictions.getBlockedURLs,
        cutproto=True,
        **kwargs)
    return len(wdomains)


def getDumpLag():
    """
    :return: Dump lag in seconds
    """
    last = dbmon.getLastDumpTime()
    if last is None:
        return -1
    return round((datetime.now().astimezone() - last).total_seconds())


def getDumpCheckLag():
    """
    :return: Parse lag in seconds
    """
    last = dbmon.getLastCheckTime()
    if last is None:
        return -1
    return round((datetime.now().astimezone() - last).total_seconds())


def getLastDumpTS():
    """
    :return: Dump unix timestamp in seconds
    """
    last = dbmon.getLastDumpTime()
    if last is None:
        return -1
    return round(last.timestamp())