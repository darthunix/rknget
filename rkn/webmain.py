#!/usr/bin/env python3
import sys

import dbconn
import redis


class WebMainApi:
    """
    The class for printing CGI data, but hasn't had its procedures implemented.
    """

    def _getParamsDict(self):
        pass

    def _printContent(self, data):
        pass

    def _formatContent(self, data):
        pass

    def main(self):
        params = self._getParamsDict()
        fields = params.copy()
        modval = fields.pop('module', None)
        if modval.split('.')[0] != 'api':
            self._printContent('Not an API')
            return 1
        metval = fields.pop('method', None)
        # Redis part
        rdb = None
        rdbvaluekey = None
        if modval in dbconn.rdb.cache:
            if dbconn.rdb.conn:
                rdb = redis.Redis(**dbconn.rdb.conn)
                try:
                    # To distinguish different API's results
                    # Got already formatted result, not source or pickled
                    rdbvaluekey = __name__ + ''.join(sorted(map(str, list(params.keys()) + list(params.values()))))
                    data = rdb.get(rdbvaluekey)
                    if data:
                        self._printContent(data)
                        return 0
                except redis.TimeoutError:
                    rdb = None
                except redis.exceptions.ConnectionError:
                    rdb = None

        # Shoot your leg through!!!
        module = __import__(modval, fromlist=[metval])
        fields['connstr'] = dbconn.connstr
        data = self._formatContent(getattr(module, metval)(**fields))

        # Redis part
        if rdb:
            try:
                rdb.set(rdbvaluekey, data, ex=dbconn.rdb.ex)
            except redis.TimeoutError:
                pass
            except redis.exceptions.ConnectionError:
                pass

        self._printContent(data)
        return 0
