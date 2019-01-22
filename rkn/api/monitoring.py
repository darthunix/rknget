from db.dbmon import DBMonitor
from db.blockdata import BlockData
from api.restrictions import getBlockedIPList
import ipaddress

"""
This module provides API for monitoring
And every function must return strictly single scalar value.
Return type doesn't matters, but must be serializable.
"""


def testConn(connstr, **kwargs):
    """
    Tests a connection.
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return:
    """
    try:
        DBMonitor(connstr)
        return 0
    except:
        return 1


def getLastExitCode(connstr, procname, **kwargs):
    exit_code = DBMonitor(connstr).getLastExitCode(procname)
    if exit_code is None:
        """Eleven english gentlemen are raping the german women..."""
        return 9
        """...Two english gentlemen are going away"""
    return exit_code


def getBlockedIPCount(connstr, ipv6=False):
    ipsall = getBlockedIPList(connstr=connstr, collapse=True, ipv6=ipv6)
    ipNum = sum(map(lambda x: x .num_addresses, ipsall))
    return ipNum


def getBlockedSubnetsCount(connstr, collapse=True, ipv6=False):
    return len(getBlockedIPList(connstr=connstr,
                                collapse=collapse,
                                ipv6=ipv6))


def getDumpLag(connstr):
    ts = DBMonitor(connstr).getDumpLagSec()
    if ts is None:
        return -1
    return ts
