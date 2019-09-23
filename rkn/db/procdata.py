from db.dbconn import connection
from datetime import datetime

cursor = connection.cursor()


def checkRunning(procname):
    cursor.execute('SELECT 1 FROM log WHERE exit_code=Null AND procname = %s LIMIT 1', (procname,))
    return cursor.rowcount


def addLogEntry(procname):
    cursor.execute('INSERT INTO log (start_time,procname) VALUES (%s,%s)', (datetime.now(), 'test'))
    connection.commit()


def finishJob(log_id, exit_code, result=None):
    cursor.execute('UPDATE log SET exit_code=%s, finish_time=%s, result=%s WHERE id=%s',
                   (exit_code, datetime.now().astimezone(), result, log_id,) )
    connection.commit()

