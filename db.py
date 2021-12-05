# Note: the module name is psycopg, not psycopg3

import mysql.connector


def start_db(host, user, passwd):
    # Connect to an existing database
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=passwd, database='py_twitter')

    return conn

    print(mydb)
