import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
import pandas as pd

class Database:
    def __init__(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.db_path = os.path.join(base_dir, "data", "database.db")

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.fetchall()

    def execute_dataframe(self, query: str) -> pd.DataFrame:
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

def listar_compras() -> pd.DataFrame:
    db = Database()
    try:
        return db.execute_dataframe("SELECT * FROM compras")
    except sqlite3.OperationalError:
        return pd.DataFrame()
