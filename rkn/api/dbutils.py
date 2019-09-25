from db import dbops
from api import parseutils

"""
This module provides API for 'rkncli' utility.
Every function should return a string or many.
"""
# Checks
checks = {
    'ip': parseutils.checkIp,
    'ipsubnet': parseutils.checkIpsub,
    'ipv6': parseutils.checkIpv6,
    'ipv6subnet': parseutils.checkIpv6sub,
    'domain': parseutils.isdomain,
    'domain-mask': parseutils.isdomain
}


def _dbAsText(headers, rows):
    """
    Auxilliary function.
    :param headers: headers list
    :param rows: list of values lists
    :return:
    """
    result = list()
    result.append('\t'.join(headers))
    for row in rows:
        result.append('\t'.join(map(str, row)))
    return '\n'.join(result)


def addCustomResource(entitytype, value, **kwargs):
    """
    Adds custom resource to the database's Resource table.
    :return: row ID or None for erroneous entitytype
    """
    try:
        if not checks[entitytype](value):
            return 'Value error'
    except KeyError:
        # No checks for this entity type
        return 'Entitytype error'
    try:
        return(
            dbops.addCustomResource(
                entitytype=entitytype,
                value=value,
            )
        )
    except KeyError:
        return "Entity type error"


def delCustomResource(entitytype, value, **kwargs):
    """
    Deletes custom resource to the database's Resource table.
    :return: True if deleted, False otherwise
    """
    try:
        return(
            dbops.delCustomResource(
                entitytype=entitytype,
                value=value,
            )
        )
    except KeyError:
        return "Entity type error"


def findResource(value, entitytype=None, **kwargs):
    """
    Adds custom resource to the database's Resource table.
    :return: row ID or None for erroneous entitytype
    """
    if kwargs.get('args') is None:
        kwargs['args'] = []
    if entitytype == 'all':
        entitytype = None
    return _dbAsText(*dbops.findResource(value, entitytype, None, *kwargs['args']))


def getContent(outer_id, **kwargs):

    headers, rows = dbops.getContent(outer_id)
    result = _dbAsText(headers, rows)
    if kwargs.get('args') is not None \
            and 'full' in kwargs.get('args') \
            and len(rows) > 0:
        content_id = rows[0][headers.index('id')]
        result = result + '\nRESOURCES\n'
        result = result + _dbAsText(*dbops.getResourceByContentID(content_id))

    return result


def showDumpStats(**kwargs):
    return _dbAsText(*dbops.getBlockCounters())


def showDumpInfo(**kwargs):
    return _dbAsText(*dbops.getLastDumpInfo())
    #return '\n'.join(str(k).ljust(16) + '\t' + str(v)
    #                 for k, v in dbops.getLastDumpInfo().items())


def delContent(outer_id, **kwargs):
    """
    Deletes custom resource to the database's Resource table.
    :return: True if deleted, False otherwise
    """
    return dbops.delContent(outer_id)


def unlockJobs(procname=None, **kwargs):
    """
    Sets exit_code and result of the all log entires with empty exit_code.
    :param procname: specify procname to unlock
    :return: Affected entries count.
    """
    if procname == 'all':
        procname = None

    return dbops.unlockJobs(procname)


def getActiveJobs(procname=None, **kwargs):
    if procname == 'all':
        procname = None
    return _dbAsText(*dbops.getActiveJobs(procname))


def getLastJobs(procname=None, **kwargs):

    if kwargs.get('args') is None:
        count = 10
    elif len(kwargs['args']) == 0:
        count = 10
    else:
        count = kwargs['args'][0]

    if procname == 'all':
        procname = None

    return _dbAsText(*dbops.getLastJobs(procname, count))


def getDecsnInfo(de_id, **kwargs):
    return _dbAsText(*dbops.getDecisionByID(de_id))


def getDecisionByID(outer_id, **kwargs):
    return _dbAsText(*dbops.getDecisionByOuterID(outer_id))
