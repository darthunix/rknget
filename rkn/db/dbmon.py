from db.dbhandler import DatabaseHandler
from db.scheme import *


class DBMonitor(DatabaseHandler):
    """
    Successor class, which provides operations for CLI API (dbutils)
    """

    _resourceQuery = None
    _contentQuery = None

    def __init__(self, connstr):
        super(DBMonitor, self).__init__(connstr)

    def getLastExitCode(self, procname):
        query = self._session.query(Log.exit_code).\
            filter(Log.procname == procname). \
            filter(Log.exit_code != None). \
            order_by(Log.id.desc()).\
            limit(1)
        row = query.first()
        if row is None:
            return None
        return row.exit_code

    def getDumpLagSec(self):
        query = self._session.query(DumpInfo.update_time).\
            filter(DumpInfo.parsed == True). \
            order_by(DumpInfo.id.desc()).\
            limit(1)
        row = query.first()
        if row is None:
            return None
        return (self._now - row.update_time).seconds

