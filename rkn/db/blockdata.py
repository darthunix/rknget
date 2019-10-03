from db.dbconn import connection
from psycopg2 import sql

cursor = connection.cursor()


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
