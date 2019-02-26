#!/usr/bin/env python3
import json
import sys

import dbconn
import redis


def _getParamsDict():
    return json.loads(sys.stdin.read())


def printContent(data):
    print("Content-type:application/json\r\n\r\n")
    print(data)


def formatContent(data):
    return json.dumps(data, default=str)


def main():
    params = _getParamsDict()
    fields = params.copy()
    modval = fields.pop('module', None)
    if modval.split('.')[0] != 'api':
        printContent('Not an API')
        return 1
    metval = fields.pop('method', None)

    # Redis part
    rdb = None
    rdbvaluekey = None
    if modval in dbconn.rdb.cache:
        if dbconn.rdb.conn:
            rdb = redis.Redis(**dbconn.rdb.conn)
            try:
                rdbvaluekey = ''.join(sorted(map(str, list(params.keys()) + list(params.values()))))
                data = rdb.get(rdbvaluekey)
                if data:
                    printContent(data)
                    return 0
            except redis.TimeoutError:
                rdb = None
            except redis.exceptions.ConnectionError:
                rdb = None

    # Shoot your leg through!!!
    module = __import__(modval, fromlist=[metval])
    fields['connstr'] = dbconn.connstr
    data = formatContent(getattr(module, metval)(**fields))

    # Redis part
    if rdb:
        try:
            rdb.set(rdbvaluekey, data, ex=dbconn.rdb.ex)
        except redis.TimeoutError:
            pass
        except redis.exceptions.ConnectionError:
            pass

    printContent(data)
    return 0


if __name__ == "__main__":
    result = main()
    exit(code=result)
