#!/usr/bin/env python3
import cgi
import sys

import dbconn
import redis


def _getParamsDict():
    fields = cgi.FieldStorage()
    return {key: fields.getvalue(key) for key in fields.keys()}


def printData(data):
    print("Content-Type: text/plain\r\n\r\n")
    print(str(data))


def main():
    fields = _getParamsDict()
    modval = fields.pop('module', None)
    if modval.split('.')[0] != 'api':
        print('Content-Type: text/plain\r\n\r\nNot an API')
        return 1
    metval = fields.pop('method', None)

    module = __import__(modval, fromlist=[metval])
    fields['connstr'] = dbconn.connstr

    # Redis part
    rdb = None
    if modval in dbconn.rdb.cache:
        if dbconn.rdb.conn:
            rdb = redis.Redis(**dbconn.rdb.conn)
            try:
                data = rdb.get(sum(map(hash, fields.items())))
                if data:
                    printData(data)
                    return 0
            except redis.TimeoutError:
                print('Redis timeout', file=sys.stderr)
                rdb = None

    # Shoot your leg through!!!
    data = getattr(module, metval)(**fields)

    # Redis part
    if rdb:
        try:
            rdb.set(sum(map(hash, fields.items())), data, ex=dbconn.rdb.ex)
        except redis.TimeoutError:
            print('Redis timeout', file=sys.stderr)

    printData(data)
    return 0


if __name__ == "__main__":
    result = main()
    exit(code=result)
