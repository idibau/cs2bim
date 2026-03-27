from typing import Any

from psycopg2 import pool as pg_pool

from config.configuration import config

_pool: pg_pool.SimpleConnectionPool | None = None


def _get_pool() -> pg_pool.SimpleConnectionPool:
    global _pool
    if _pool is None:
        _pool = pg_pool.SimpleConnectionPool(minconn=1, maxconn=5, dbname=config.db.dbname, user=config.db.user,
                                             host=config.db.host, password=config.db.password, port=config.db.port)
    return _pool


class PostgisService:
    """
    Service class for accessing a PostGIS database according to configuration.

    This class provides methods for querying features based on SQL statements
    and bounding boxes from a PostGIS database.
    """

    def fetch_feature_type_elements(self, sql: str, polygon: str) -> list[dict[str, Any]]:
        """
        Executes an SQL query and returns the results as a list of dictionaries.

        Args:
            sql: The SQL query to run. Should contain a placeholder for `polygon`.
            polygon: Polygon geometry as a WKT string, used within the SQL statement.

        Returns:
            A list of dictionaries representing the fetched rows, where the keys are the column names.

        Raises:
            Exception: If the SQL query does not return any column description.
        """
        connection_pool = _get_pool()
        conn = connection_pool.getconn()
        try:
            cur = conn.cursor()
            cur.execute(sql, {"polygon": polygon})
            rows = cur.fetchall()
            if cur.description is None:
                raise Exception("Invalid sql")
            column_names = [desc[0] for desc in cur.description]
            cur.close()
            return [dict(zip(column_names, row)) for row in rows]
        finally:
            connection_pool.putconn(conn)
