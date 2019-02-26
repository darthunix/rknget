#!/usr/bin/env python3
import json
import sys

import dbconn
import redis


def _getParamsDict():
    return json.loads(sys.stdin.read())


def printData(data):
    print("Content-type:application/json\r\n\r\n")
    print(json.dumps(data, default=str))


def main():
    params = _getParamsDict()
    fields = params.copy()
    modval = fields.pop('module', None)
    if modval.split('.')[0] != 'api':
        print('Content-Type: text/plain\r\n\r\nNot an API')
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
                    printData(data)
                    return 0
            except redis.TimeoutError or redis.exceptions.ConnectionError:
                print('Redis timeout', file=sys.stderr)
                rdb = None

    # Shoot your leg through!!!
    module = __import__(modval, fromlist=[metval])
    fields['connstr'] = dbconn.connstr
    data = getattr(module, metval)(**fields)

    # Redis part
    if rdb:
        try:
            rdb.set(rdbvaluekey, str(data), ex=dbconn.rdb.ex)
        except redis.TimeoutError or redis.exceptions.ConnectionError:
            print('Redis timeout', file=sys.stderr)

    printData(data)
    return 0


if __name__ == "__main__":
    result = main()
    exit(code=result)
