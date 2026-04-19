from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="db",
    user="postgres",
    password="root",
    host="localhost",
    port="5433"
)

def get_connection():
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"DB connection failed: {e}")
        raise RuntimeError("Database connection error")

def release_connection(conn):
    if conn is None:
        return

    try:
        connection_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Pool release failed: {e}")
        raise