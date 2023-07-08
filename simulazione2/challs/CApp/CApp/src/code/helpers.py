from flask import g
from .exceptions import *


def do_query(query, params, commit=False):
    cursor = g.mysql.connection.cursor()
    cursor.execute(query, params)

    if commit:
        g.mysql.connection.commit()
    result = cursor.fetchall()
    insertObject = []
    try:
        columnNames = [column[0] for column in cursor.description]

        for record in result:
            insertObject.append( dict( zip( columnNames , record ) ) )
    except TypeError:
        return None
    finally:
        cursor.close()
    return insertObject