from __future__ import absolute_import

import psycopg2

CUBE_OID = 16398

def cast_cube(value, cursor):
    """
    """
    if value:
        return map(float, value[1:-1].split(','))

CUBE = psycopg2.extensions.new_type((CUBE_OID,), "CUBE", cast_cube)
psycopg2.extensions.register_type(CUBE)
