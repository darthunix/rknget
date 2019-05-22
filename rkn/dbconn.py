"""
Configuration file for RKNDB API
"""


def buildConnStr(engine, host, port, dbname, user, password, **kwargs):
    return engine + '://' + \
           user + ':' + password + '@' + \
           host + ':' + str(port) + '/' + dbname


dbconn = {
    "engine": "postgresql",
    "host": "127.0.0.1",
    "port": "5432",
    "dbname": "rkndb",
    "user": "rkn",
    "password": "hry"
}

connstr = buildConnStr(**dbconn)


class rdb:
    conn = {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'socket_connect_timeout': 2,
        'encoding': 'utf8',
        'decode_responses': 'utf8',
        'password': 'bir6aepheo8eilohBo6NaarooTh6eeghooch3xaeCeecohnoo8gain9avu0phaiw'
    }
    cache = {'api.restrictions'}
    ex = 1800
