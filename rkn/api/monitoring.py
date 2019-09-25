from db import dbmon

from api.restrictions import getBlockedIPList
import ipaddress

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


def getLastExitCode(procname, **kwargs):
    exit_code = dbmon.getLastExitCode(procname)
    if exit_code is None:
        """Eleven english gentlemen are raping the german women..."""
        return 9
        """...Two english gentlemen are going away"""
    return exit_code


def getBlockedIPCount(ipv6=False):
    ipsall = getBlockedIPList(collapse=True, ipv6=ipv6)
    ipNum = sum(map(lambda x: x.num_addresses, ipsall))
    return ipNum


def getBlockedSubnetsCount(collapse=True, ipv6=False):
    return len(getBlockedIPList(collapse=collapse,
                                ipv6=ipv6))


def getDumpLag():
    ts = dbmon.getDumpLagSec()
    if ts is None:
        return -1
    return ts
