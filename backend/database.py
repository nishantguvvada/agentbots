from dotenv import load_dotenv
import os
import psycopg2
import asyncpg
from typing import Optional, List

load_dotenv()


DB_DSN = os.getenv('DB_DSN')

def create_notes_table():
    """
    Establishes a 'notes' table if it doesn't exist, with 'id', 'title', and 'text'.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) UNIQUE NOT NULL,
        text TEXT NOT NULL
    );
    """
    try:
        connection = psycopg2.connect(DB_DSN)
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Successfully created or verified the 'notes' table.")
    except psycopg2.Error as e:
        print(f"Error while creating table: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def check_table_exists(table_name: str) -> bool:
    """
    Checks whether a specified table is present in the DB.
    """
    query = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = %s
    );
    """
    try:
        connection = psycopg2.connect(DB_DSN)
        cursor = connection.cursor()
        cursor.execute(query, (table_name,))
        exists = cursor.fetchone()[0]
        return exists
    except psycopg2.Error as e:
        print(f"Error checking table: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

class DatabaseConn:
    def __init__(self):
        """
        Store the DSN (Data Source Name) for connecting.
        """
        self.dsn = DB_DSN

    async def _connect(self):
        """
        Opens an async connection to PostgreSQL.
        """
        return await asyncpg.connect(self.dsn)
    
    async def add_note(self, title: str, description: str) -> bool:
        """
        Inserts a note with the given title and text.
        If a note with the same title exists, it won't overwrite.
        """
        query = """
        INSERT INTO notes (title, text)
        VALUES ($1, $2)
        ON CONFLICT (title) DO NOTHING;
        """
        conn = await self._connect()
        try:
            result = await conn.execute(query, title, description)
            return result == "INSERT 0 1"
        finally:
            await conn.close()

    async def get_note_by_title(self, title: str) -> Optional[dict]:
        """
        Retrieves the note matching the specified title. Returns a dict or None.
        """
        query = "SELECT title, text FROM notes WHERE title = $1;"
        conn = await self._connect()
        try:
            record = await conn.fetchrow(query, title)
            if record:
                return {"title": record["title"], "text": record["text"]}
            return None
        finally:
            await conn.close()

    async def list_all_titles(self) -> List[str]:
        """
        Fetches and returns all note titles.
        """
        query = "SELECT title FROM notes ORDER BY title;"
        conn = await self._connect()
        try:
            results = await conn.fetch(query)
            return [row["title"] for row in results]
        finally:
            await conn.close()
