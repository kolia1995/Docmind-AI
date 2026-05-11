from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5332"
)

def get_connection():
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        raise RuntimeError("Database connection error")

def release_connection(conn):
    if conn is None:
        return

    try:
        connection_pool.putconn(conn)
    except Exception as e:
        raise