import psycopg2
from psycopg2.extras import DictCursor

from db.settings import dbconn

connection = psycopg2.connect(**dbconn, cursor_factory = DictCursor)

"""
Of course, I should have caught exceptions with closing connection.
But stateless python scripts anyway end up and do it by themselves.
"""