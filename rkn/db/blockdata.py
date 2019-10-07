from db.dbconn import connection
from psycopg2 import sql

cursor = connection.cursor()


def getResourcesByBlocktype(entitytype, blocktype):
    """
    Returns blocked data set
    :param entitytype: target entity type
    :param blocktype: content blocktype
    :return: set of strings
    """
    cursor.execute(
        '''SELECT value FROM resource
        JOIN content ON content_id = content.id 
        JOIN blocktype ON blocktype_id = blocktype.id
        JOIN entitytype ON entitytype_id = entitytype.id
        WHERE in_dump is True AND entitytype.name = %s
        AND blocktype.name = %s
        ''',
        (entitytype, blocktype,)
    )
    return {c['value'] for c in cursor}


def getResourcesByEntitytype(entitytype, srcentty):
    """
    Returns blocked data set. Note, it's excessive
    :param entitytype: target entity type
    :param srcentty: source entity type
    :return: set of strings
    """
    # Distinction is implemented by python set
    cursor.execute(
        '''SELECT r1.value FROM resource as r1
        JOIN resource as r2 ON r1.content_id = r2.content_id
        JOIN entitytype as e1 ON r1.entitytype_id = e1.id
        JOIN entitytype as e2 ON r2.entitytype_id = e2.id
        JOIN content ON r1.content_id = content.id
        WHERE e1.name = %s
        AND e2.name = %s
        AND in_dump is True
        ''',
        (entitytype, srcentty,)
    )
    return {c['value'] for c in cursor}


def getCustomResources(entitytype, is_banned=False):
    """
    Returns blocked data set
    :param entitytype: target entity type
    :param is_banned: black/white list switch
    :return: set of strings
    """

    cursor.execute(
        '''SELECT value FROM resource
        JOIN entitytype ON entitytype_id = entitytype.id
        WHERE entitytype.name = %s
        AND is_banned = %s
        ''',
        (entitytype, is_banned)
    )

    return {c['value'] for c in cursor}
