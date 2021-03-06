from db.dbconn import connection
from datetime import datetime
from psycopg2 import sql

from db.dataprocessing import addResource

cursor = connection.cursor()

UNLOCK_EXIT_CODE=255

def _buildFields(*args):
    """
    Builds columns list to obtain in query
    :param args: fields list
    :return: fields Composable
    """
    if not args or len(args) == 0:
        return sql.SQL('*')
    return sql.SQL(',').join(
        [sql.Identifier(f) for f in args]
    )


def _outputQuery(cursor, columns=None):
    """
    Returns columns list and values list's list
    :param cursor: cursor with executed query
    :return:
    """
    if cursor.rowcount == 0:
        return [], []
    if not columns:
        columns = [col.name for col in cursor.description]
    return columns, \
           [[row[c] for c in columns] for row in cursor]


def addCustomResource(entitytype, value, is_banned=False):
    """
    Adds custom resource to the table.
    :return: new or existing resource ID
    """
    now = datetime.now().astimezone()
    cursor.execute(
        '''SELECT resource.id FROM resource
        JOIN entitytype ON resource.entitytype_id = entitytype.id 
        WHERE is_banned IS NOT NULL
        AND entitytype.name = %s
        AND value=%s
        ''', (entitytype, value,)
    )
    # If exists, banning/unbanning with returning IDs
    if cursor.rowcount > 0:
        ids = [c['id'] for c in cursor]
        cursor.execute('''
            UPDATE resource
            SET is_banned = %s, last_change = %s
            WHERE ID=ANY(%s)
            ''', (is_banned, now, ids,)
                       )
        connection.commit()
        return ids
    # If nothing found
    return addResource(
        content_id=None,
        entitytype=entitytype,
        value=value,
        is_banned=is_banned,
        last_change=now,
        atomic=True
    )


def delCustomResource(entitytype, value):
    """
    Deletes custom resource from the table.
    :return: row ID or None
    """
    cursor.execute(
        '''DELETE FROM resource
        WHERE is_banned IS NOT NULL
        AND value = %s
        AND entitytype_id = (SELECT id FROM entitytype WHERE name = %s)
        RETURNING id
        ''', (value,entitytype,)
    )
    connection.commit()

    if cursor.rowcount > 0:
        return cursor.fetchone()['id']
    return None


def findResource(value=None, entitytype=None, content_id=None, *args):

    query = sql.SQL('''SELECT
    resource.id, content.outer_id, content.in_dump, entitytype.name as entitytype,
    blocktype.name as blocktype, resource.is_banned,
    resource.value
    FROM resource
        LEFT JOIN content on resource.content_id = content.id
        JOIN entitytype ON resource.entitytype_id = entitytype.id
        LEFT JOIN blocktype on content.blocktype_id = blocktype.id
        WHERE value LIKE %s
        ''')
    #.format(_buildFields(*args))
    if not value or value == '':
        value = '%'
    else:
        value = '%' + value + '%'

    if entitytype:
        query = query + sql.SQL(' AND entitytype_id = '
                                '(SELECT id FROM entitytype WHERE name = {0})'
                                ).format(sql.Literal(entitytype))
    if content_id:
        query = query + sql.SQL(' AND content.id = {0}'
                                ).format(sql.Literal(content_id))

    cursor.execute(query, (value,))

    return _outputQuery(cursor, args)


def getContent(outer_id):

    cursor.execute(
        '''SELECT content.id, content.outer_id,
        content.include_time, content.in_dump,
        blocktype.name as blocktype,
        di1.parse_time as first_time,
        di2.parse_time as last_time
        FROM content
        JOIN blocktype ON content.blocktype_id = blocktype.id
        JOIN dumpinfo AS di1 ON content.first_dump_id = di1.id
        JOIN dumpinfo AS di2 ON content.last_dump_id = di2.id
        WHERE outer_id = %s
        ''', (outer_id,)
    )

    return _outputQuery(cursor)


def getResourceByContentID(content_id, *args):
        return findResource(content_id=content_id)


def getDumpCounters():

    cursor.execute(
        '''SELECT entitytype.name, count(1) AS sum
        FROM resource 
        JOIN entitytype ON resource.entitytype_id = entitytype.id
        JOIN content ON resource.content_id = content.id
        GROUP BY entitytype.id, content.in_dump
        HAVING in_dump=True'''
    )

    return _outputQuery(cursor)


def getLastDumpInfo():
    """
    The same function as the dataprocessing's one.
    Returns the last dump state. If no entries, empty dict.
    :return: dict column->value or dict().
    """

    cursor.execute(
        '''SELECT * FROM dumpinfo
        ORDER BY id DESC LIMIT 1'''
    )

    return _outputQuery(cursor)


def unlockJobs(procname=None):

    query = sql.SQL('''UPDATE log SET exit_code=%s
        WHERE exit_code is Null'''
    )
    if procname:
        query = query + sql.SQL(' AND procname = {0}'
                                ).format(sql.Literal(procname))

    cursor.execute(query, (UNLOCK_EXIT_CODE,))
    connection.commit()

    return int(cursor.statusmessage.split(' ')[1])


def getActiveJobs(procname=None):

    query = sql.SQL(
        '''SELECT id, start_time, procname
        FROM log WHERE exit_code is Null
        '''
    )
    if procname:
        query = query + sql.SQL(' AND procname = {0}'
                                ).format(sql.Literal(procname))

    query = query + sql.SQL(' ORDER BY id DESC')

    cursor.execute(query)

    return _outputQuery(cursor)


def getLastJobs(procname=None, count=10):

    query = sql.SQL(
        '''SELECT id, exit_code, start_time,
        finish_time, procname FROM log
        '''
    )
    if procname:
        query = query + sql.SQL(' WHERE procname = {0}'
                                ).format(sql.Literal(procname))

    query = query + sql.SQL(' ORDER BY id DESC')
    query = query + sql.SQL(' LIMIT {0}'
                                ).format(sql.Literal(count))
    cursor.execute(query)

    return _outputQuery(cursor)


def getDecisionByID(de_id, *args):

    cursor.execute(
        '''SELECT decision.id, decision_code, decision_date,
        organisation.name
        FROM decision
        JOIN organisation ON decision.org_id = organisation.id
        WHERE decision.id = %s
        ''', (de_id,)
    )

    return _outputQuery(cursor, args)


def getDecisionByOuterID(outer_id, *args):

    cursor.execute(
        '''SELECT decision.id, decision_code, decision_date,
        organisation.name
        FROM decision
        JOIN organisation ON decision.org_id = organisation.id
        JOIN content ON decision.id = content.decision_id
        WHERE outer_id = %s
        ''', (outer_id,)
    )

    return _outputQuery(cursor, args)

