import os
from database.db import get_connection, release_connection

class DatabaseManager:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(BASE_DIR, "schema.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_script)
            conn.commit()
        except Exception as e:
            raise
        finally:
            release_connection(conn)
    
    def execute(self, query, params=None):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())

            result = None

            if cursor.description:
                result = cursor.fetchone()

            conn.commit()
            return result

        except Exception as e:
            raise
        finally:
            release_connection(conn)

    def fetchall(self, query, params=None):

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except Exception as e:
            raise
        finally:
            cursor.close()
            release_connection(conn)