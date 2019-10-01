"""
Configuration file for RKNDB API
"""

class redisconf:
    conn = {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'socket_connect_timeout': 2,
        'encoding': 'utf8',
        'decode_responses': 'utf8',
        'password': 'bir6aepheo8eilohBo6NaarooTh6eeghooch3xaeCeecohnoo8gain9avu0phaiw'
    }
    #cache = {'api.restrictions'}
    cache = {}
    ex = 1200
