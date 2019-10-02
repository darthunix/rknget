from db.dbconn import connection

cursor = connection.cursor()

def testDBConn():
    cursor.execute('SELECT 1')
    return cursor.fetchone()[0]


def getLastExitCode(procname):
    cursor.execute(
        '''SELECT exit_code FROM log
        WHERE exit_code is not NULL 
        AND procname = %s
        ORDER BY id DESC LIMIT 1''', (procname,))
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()['exit_code']


def getLastDumpTime():
    """
    Returns the last successfull time when dump was parsed.
    :return: datetime value
    """
    cursor.execute('SELECT update_time FROM dumpinfo WHERE parsed = True '
                   'ORDER BY id DESC LIMIT 1')
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()['update_time']


def getLastParsedTime():
    """
    Returns the last successfull time when dump was parsed.
    :return: datetime value
    """
    cursor.execute('SELECT parse_time FROM dumpinfo WHERE parsed = True '
                   'ORDER BY id DESC LIMIT 1')
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()['parse_time']