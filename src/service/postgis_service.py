import psycopg2
from typing import Any

from config.configuration import config


class PostgisService:
    """
    Service class for accessing a PostGIS database according to configuration.

    This class provides methods for querying features based on SQL statements
    and bounding boxes from a PostGIS database.
    """

    def __init__(self):
        self.connection = psycopg2.connect(
            f"dbname = {config.db.dbname} user = {config.db.user} host = {config.db.host} password = {config.db.password} port = {config.db.port}"
        )

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
        cur = self.connection.cursor()
        cur.execute(sql, {"polygon": polygon})
        rows = cur.fetchall()
        if cur.description is not None:
            column_names = [desc[0] for desc in cur.description]
        else:
            raise Exception("Invalid sql")
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        cur.close()
        return result