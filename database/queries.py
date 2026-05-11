import os
from database.db import get_connection, release_connection


class DatabaseManager:
    def __init__(self):
        self._init_schema()

    def _init_schema(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(BASE_DIR, "schema.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_script)
            conn.commit()
        finally:
            cursor.close()
            release_connection(conn)

    def execute(self, query, params=None):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()

            if cursor.description:
                return cursor.fetchone()

            return None

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            cursor.close()
            release_connection(conn)

    def fetchall(self, query, params=None):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()

        except Exception as e:
            raise e

        finally:
            cursor.close()
            release_connection(conn)

    def fetchone(self, query, params=None):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()

        except Exception as e:
            raise e

        finally:
            cursor.close()
            release_connection(conn)