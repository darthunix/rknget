"""
Describes which API functions can be cached
and which can be called by GET HTTP method.
Used in webmain.py
"""
class apiconf:
    cacheable = {
        'api.restrictions'
    }
    getable = {
        'api.restrictions',
        'api.monitoring'
    }