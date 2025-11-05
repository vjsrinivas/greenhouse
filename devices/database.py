import sqlite3
from typing import *
import os
from loguru import logger
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class LogRecord:
    name: str = field()
    level: str = field(default="INFO")
    message: Optional[str] = field(default="")
    metadata: Optional[str] = field(default="")

@dataclass
class ImageRecord:
    name: str = field()
    path: str = field()
    active: bool = field(default=True)

class SQLiteAPI:
    """A simple SQLite database interface using only native Python modules."""

    def __init__(self, db_path: str = "database.db"):
        """Initialize the connection to the SQLite database."""
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Access rows as dictionaries
        self.cursor = self.connection.cursor()

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        """Execute a query (INSERT, UPDATE, DELETE, etc.)."""
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return all rows."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> Optional[sqlite3.Row]:
        """Execute a SELECT query and return one row."""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def create_table(self, table_name: str, columns: str) -> None:
        """Create a table if it doesn’t exist.

        Example:
            db.create_table("users", "id INTEGER PRIMARY KEY, name TEXT, age INTEGER")
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.execute(query)

    def insert(self, table: str, data: dict) -> None:
        """Insert a record into a table."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(query, values)

    def update(
        self, table: str, data: dict, condition: str, params: Tuple[Any, ...]
    ) -> None:
        """Update records in a table based on a condition."""
        set_clause = ", ".join(f"{col}=?" for col in data.keys())
        values = tuple(data.values()) + params
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.execute(query, values)

    def delete(self, table: str, condition: str, params: Tuple[Any, ...]) -> None:
        """Delete records from a table based on a condition."""
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute(query, params)

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()


class DatabaseHandler:
    def __init__(self, db_file_path: str):
        db_dir = Path(db_file_path).parent
        os.makedirs(db_dir, exist_ok=True)

        db_exists = os.path.exists(db_file_path)
        self.db_file_path = db_file_path
        self.connector = SQLiteAPI(db_file_path)
        if not db_exists:
            self.generate_schema()

    def generate_schema(self) -> None:
        """
        Define and create the schema for the SQLite database.
        Add all CREATE TABLE statements here.
        """
        schema_statements = [
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT DEFAULT 'INFO',
                message TEXT NOT NULL,
                metadata TEXT -- JSON or key-value metadata
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                active BOOLEAN NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
        ]

        for stmt in schema_statements:
            self.connector.execute(stmt)

        logger.info("✅ Database schema generated successfully.")

    def log(self, data: LogRecord):
        query = (
            "INSERT INTO logs (device, level, message, metadata) VALUES (?, ?, ?, ?)"
        )
        params = (data.name, data.level, data.message, data.metadata)
        self.connector.execute(query, params)

    def record_image(self, image_data: ImageRecord):
        query = "INSERT INTO images (image_name, image_path, active) VALUES (?, ?, ?)"
        params = (image_data.name, image_data.path, True)
        self.connector.execute(query, params)

    def record_delete_image(self, image_name:str):
        # Find the image in the table and set the active column to False
        query = """
            SELECT *
            FROM images
            WHERE image_name = ?
        """
        params = (image_name, )
        row = self.connector.fetch_one(query, params=params)
        if row:
            self.connector.execute("""
                UPDATE images
                SET active = 0
                WHERE image_name = ?
            """, (image_name,))
        else:
            raise ValueError(f"Cannot find {image_name} in image table!")

    def heartbeat(self):
        query = "INSERT INTO events DEFAULT VALUES;"
        self.connector.execute(query)


if __name__ == "__main__":
    handler = DatabaseHandler("test.db")
    handler.heartbeat()
    handler.record_image({})
