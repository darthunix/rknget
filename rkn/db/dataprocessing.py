from db.dbconn import connection
from datetime import datetime

cursor = connection.cursor()
connection.autocommit = False


def commitChanges():
    # Force committing after long transaction
    connection.commit()


def addDumpInfoRecord(updateTime, updateTimeUrgently, **kwargs):
    """
    The arguments were named corresponding with
    <reg> tag attributes to simplify kwargs passthrough
    """
    cursor.execute(
        '''INSERT INTO dumpinfo 
        (update_time, update_time_urgently, parse_time, parsed)
        VALUES (%s, %s, %s, %s) RETURNING id''',
        (updateTime, updateTimeUrgently, datetime.now().astimezone(), False)
    )
    connection.commit()

    return cursor.fetchone()['id']


def setDumpParsed(dump_id):

    cursor.execute(
        '''UPDATE dumpinfo SET parsed = True
        WHERE id = %s''',
        (dump_id,)
    )
    connection.commit()

    return True


def addDecision(date, number, org, atomic=False):
    """
    The arguments were named corresponding with
    <decision> tag attributes to simplify kwargs passthrough
    :return: decision ID
    """
    cursor.execute(
        '''SELECT id FROM decision
        WHERE decision_code = %s''',
        (number,)
    )
    # Decision exists in the database
    if cursor.rowcount > 0:
        return cursor.fetchone()['id']

    # Adding organisation to the table if missing
    cursor.execute(
        '''SELECT id FROM organisation
        WHERE name = %s''',
        (org,)
    )
    if cursor.rowcount == 0:
        cursor.execute(
            '''INSERT INTO organisation (name)
            VALUES (%s) RETURNING id''',
            (org,),
        )
    org_id = cursor.fetchone()['id']

    # Adding missing decision to the table
    cursor.execute(
        '''INSERT INTO DECISION
        (decision_code, decision_date, org_id)
        VALUES (%s, %s, %s) RETURNING id''',
        (number, date, org_id,)
    )
    if atomic:
        connection.commit()

    return cursor.fetchone()['id']


def addContent(dump_id, decision_id, id, includeTime, hash,
               entryType, blockType='default', ts=None, atomic=False, **kwargs):
    """
    Not atomic
    The arguments were named corresponding with
    <content> tag attributes to simplify kwargs passthrough
    """
    # Checking whether content is in the table but disabled
    # Cascade purging must place to be
    cursor.execute(
        '''DELETE FROM content
        WHERE outer_id = %s
        AND in_dump is False
        ''',
        (id,)
    )

    cursor.execute(
        '''INSERT INTO content
        VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, 
        (SELECT id FROM blocktype WHERE name = %s), 
        %s, %s, %s)
        RETURNING id
        ''', (id, includeTime, hash, ts, True, decision_id,
              blockType,
              entryType, dump_id, dump_id)
    )

    if atomic:
        connection.commit()

    return cursor.fetchone()['id']


def delContent(outer_id):
    """
    Deletes content and all its resources
    :param outer_id: from dump
    :return: content_id, or None if nothing deleted
    """
    cursor.execute(
        '''DELETE FROM content
        WHERE outer_id = %s
        RETURNING id
        ''',
        (outer_id,)
    )
    connection.commit()
    if cursor.rowcount > 0:
        return cursor.fetchone()['id']
    else:
        return None


def getOuterIDHashes():

    cursor.execute(
        '''SELECT outer_id, hash
        FROM content
        WHERE in_dump = True
        '''
    )
    return {c['outer_id']:c['hash'] for c in cursor}


def updateContentPresence(dump_id, disabledIDList=[]):
    """
    Sets in_dump to false for removed IDs from the set
    Sets the latest dump_id label from alive records
    :param dump_id: dump id
    :param disabledIDList: IDs list
    :return: True
    """
    cursor.execute(
        '''UPDATE content SET in_dump = True
        WHERE outer_id = ANY(%s)''',
        (disabledIDList,)
    )

    cursor.execute(
        '''UPDATE content SET last_dump_id = %s
        WHERE in_dump = True''',
        (dump_id,)
    )
    connection.commit()
    return True

def addResource(content_id, entitytype, value, is_custom=False, last_change=None, atomic=False):
    """
    Not atomic
    Adds resource to the table
    :return: new resource ID
    """

    cursor.execute(
        '''INSERT INTO resource
        (content_id, last_change, entitytype_id, value, is_custom)
        VALUES (%s, %s,
        (SELECT id FROM entitytype WHERE name = %s), 
        %s, %s)
        RETURNING id
        ''', (content_id, last_change,
              entitytype,
              value, is_custom,)
    )

    if atomic:
        connection.commit()

    return cursor.fetchone()['id']
