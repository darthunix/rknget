from db.dbconn import connection
from psycopg2 import sql

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


# Further stateless blocklists formed

def getBlockedData(entitytypes, blocktypes, srcenttys=None):
    """
    Returns blocked data set
    :param entitytypes: target entity type set
    :param blocktypes: content blocktype set
    :param srcenttys: additional entity type set for excessive blockings
    :return: set of strings
    """

    query = sql.SQL(
        '''SELECT value FROM resource
        JOIN content ON content_id = content.id 
        JOIN blocktype ON blocktype_id = blocktype.id
        JOIN entitytype ON entitytype_id = entitytype.id
        WHERE in_dump = True AND entitytype.name = ANY(%s)
        AND (
            blocktype.name = ANY(%s) 
        '''
    )
    if not srcenttys or len(srcenttys) == 0:
        query = query + sql.SQL(')')
    else:
        query = query + sql.SQL('''
            OR content_id IN (
                SELECT content_id FROM resource
                JOIN entitytype ON entitytype_id = entitytype.id
                WHERE entitytype.name = ANY(ARRAY[{0}])
            )
            )''').format(
            sql.SQL(',').join(
                [sql.Literal(e) for e in srcenttys]
            )
        )

    cursor.execute(query,
                   (entitytypes, blocktypes)
    )
    return {c['value'] for c in cursor}
