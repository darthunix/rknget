from dbconn import connection
from datetime import datetime

cursor = connection.cursor()


def unblockAllResources():
    connection.isolation_level = 'SERIALIZABLE'
    cursor.execute('UPDATE resource SET is_blocked=False')
    connection.commit()


def blockFairly():
    """
    Enables blocking resoures according to its blocktype and presence in the dump
    Any other blocking is excessive a priori
    """
    cursor.execute(
        '''UPDATE resource SET is_blocked=True
        WHERE id IN (
            SELECT resource.id FROM resource 
            JOIN content ON resource.content_id = content.id
            JOIN blocktype ON content.blocktype_id = blocktype.id
            JOIN entitytype ON resource.entitytype_id =  entitytype.id
            WHERE blocktype.name = 'default' AND entitytype.name IN ('http','https')
            OR blocktype.name = 'domain' AND entitytype.name = 'domain'
            OR blocktype.name = 'domain-mask' AND entitytype.name = 'domain-mask'
            OR blocktype.name = 'ip' AND entitytype.name IN ('ip','ipsubnet','ipv6','ipv6subnet')
        )'''
    )
    connection.commit()
    return int(cursor.statusmessage.split(' ')[1])


def blockExcessively(src_entity, dst_entity):
    """
    Blocks dst_entities from src_entities data.
    :param src_entity: usually it's an entity which has already been blocked according to its blocktype
    :param dst_entity: an antity for blocking
    :return: Blocked rows count if implemented
    """
    cursor.execute(
        '''UPDATE resource SET is_blocked=True
        WHERE content_id in (
	        SELECT content.id FROM resource
	        JOIN content ON resource.content_id = content.id
	        JOIN entitytype ON resource.entitytype_id = entitytype.id
	        WHERE entitytype.name = %s
	    )
	    AND entitytype_id in (
	        SELECT id FROM entitytype WHERE name = %s
	    )
        ''', (src_entity, dst_entity,)
    )
    connection.commit()
    return int(cursor.statusmessage.split(' ')[1])


def blockCustom():
    """
    Enables blocking custom resources
    :return: blocked rows count
    """
    cursor.execute(
        '''UPDATE resource SET is_blocked=True WHERE is_custom=True''')
    connection.commit()
    return int(cursor.statusmessage.split(' ')[1])


def unblockSet(resSet):
    """
    Unblocking set of resources.
    :return: blocked rows count
    """
    if len(resSet) == 0:
        return 0
    for res in resSet:
          cursor.execute(
              '''UPDATE resource SET is_blocked=True
              WHERE value like %s''',
              ('%' + res + '%',)
          )
    connection.commit()
    return int(cursor.statusmessage.split(' ')[1])

