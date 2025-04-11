import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
import pandas as pd

class Database:
    """
    Classe utilitária para gerenciar conexão e execução de consultas no SQLite.
    """

    def __init__(self, db_name: str = "gastos.db"):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_dir = os.path.join(base_dir, "db")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, db_name)

    @contextmanager
    def get_connection(self):
        """
        Gerenciador de contexto para conexão segura com o banco de dados.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def executar(self, query: str, params: Optional[tuple] = None):
        """
        Executa uma consulta que modifica dados (INSERT, UPDATE, DELETE).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.fetchall()

    def consultar_dataframe(self, query: str) -> pd.DataFrame:
        """
        Executa uma consulta SELECT e retorna um DataFrame.
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

def listar_compras() -> pd.DataFrame:
    db = Database()
    try:
        df = db.consultar_dataframe("SELECT * FROM compras ORDER BY id DESC")

        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%y-%m-%d")

        return df
    except sqlite3.OperationalError as e:
        print(f"⚠️ Erro ao listar compras: {e}")
        return pd.DataFrame()


