from __future__ import absolute_import

import psycopg2

from credoscript.support.vector import Vector

VECTOR3D_OID= 16651
CUBE_OID    = 16578

def cast_vector3d(value, cursor):
    """
    """
    if value:
        coords = map(float, value[1:-1].split(','))
        return Vector(coords)

def cast_cube(value, cursor):
    """
    """
    if value:
        return map(float, value[1:-1].split(','))

VECTOR3D = psycopg2.extensions.new_type((VECTOR3D_OID,), "VECTOR3D", cast_vector3d)
CUBE = psycopg2.extensions.new_type((CUBE_OID,), "CUBE", cast_cube)

psycopg2.extensions.register_type(VECTOR3D)
psycopg2.extensions.register_type(CUBE)
