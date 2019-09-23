from db.dbconn import connection
from datetime import datetime

cursor = connection.cursor()

def testDBConn():
    cursor.execute('SELECT 1')
    return cursor.fetchone()[0]


def getLastExitCode(procname):
    cursor.execute('SELECT exit_code FROM log WHERE procname = %s LIMIT 1', (procname,))
    if cursor.rowcount == 0:
        return None
    return cursor.fetchone()['exit_code']


def getDumpLagSec():
    cursor.execute('SELECT update_time FROM dumpinfo WHERE parsed = True '
                   'ORDER BY id DESC LIMIT 1')
    if cursor.rowcount == 0:
        return None
    return (datetime.now().astimezone() - cursor.fetchone()['update_time']).seconds
