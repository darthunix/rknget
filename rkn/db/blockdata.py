from db.dbconn import connection
from datetime import datetime

cursor = connection.cursor()


def getBlockedResourcesSet(entityname):
    """
    :param entityname: resource entitytype
    :return: resources' values set
    """
    cursor.execute(
        '''SELECT value FROM resource
        WHERE is_blocked = TRUE
        AND entitytype_id = (SELECT id FROM entitytype WHERE name = %s) 
        ''', (entityname,)
    )
    return {c['value'] for c in cursor}


def getFairlyBlockedResourcesSet(entityname):
    """
    :param entityname: resource entitytype
    :return: resources' values set
    """

    fairness = {
        'http': 'default', 'https': 'default',
        'domain': 'domain',
        'domain-mask': 'domain-mask',
        'ip': 'ip', 'ipsubnet': 'ip', 'ipv6': 'ip', 'ipv6subnet': 'ip'
    }

    cursor.execute(
        '''SELECT value FROM resource
        WHERE id IN (
            SELECT resource.id FROM resource 
            JOIN content ON resource.content_id = content.id
            JOIN blocktype ON content.blocktype_id = blocktype.id
            JOIN entitytype ON resource.entitytype_id =  entitytype.id
            WHERE resource.is_blocked = True 
            AND entitytype.name = %s
            AND blocktype.name = %s
        )''', (entityname, fairness[entityname],)
    )
    return {c['value'] for c in cursor}


