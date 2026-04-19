import os
import logging
from database.db import get_connection, release_connection

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        logger.info("Initializing DatabaseManager")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(BASE_DIR, "schema.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        logger.debug("Schema SQL loaded")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_script)
            conn.commit()
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise
        finally:
            release_connection(conn)
    
    def execute(self, query, params=None):
        logger.debug(f"Executing query: {query[:100]}..." if len(query) > 100 else f"Executing query: {query}")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())

            result = None

            if cursor.description:
                result = cursor.fetchone()

            conn.commit()
            logger.debug("Query executed successfully")
            return result

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            release_connection(conn)

    def fetchall(self, query, params=None):
        logger.debug(f"Fetching all results: {query[:100]}..." if len(query) > 100 else f"Fetching all results: {query}")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            logger.debug(f"Fetched {len(results)} rows")
            return results
        except Exception as e:
            logger.error(f"Fetch operation failed: {e}")
            raise
        finally:
            cursor.close()
            release_connection(conn)