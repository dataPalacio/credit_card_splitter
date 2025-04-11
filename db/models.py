import sqlite3
import os

def criar_tabelas():
    """
    Cria as tabelas 'pessoas', 'cartoes' e 'compras' no banco de dados SQLite.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_dir = os.path.join(base_dir, "db")
    os.makedirs(db_dir, exist_ok=True)
    caminho_db = os.path.join(db_dir, "gastos.db")

    with sqlite3.connect(caminho_db) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                limite REAL DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cartoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                responsavel TEXT NOT NULL,
                cartao TEXT NOT NULL,
                categoria TEXT DEFAULT 'Outros',
                parcelas INTEGER DEFAULT 1,
                parcela_atual INTEGER DEFAULT 1
            )
        ''')

        conn.commit()

    print("✅ Tabelas criadas com sucesso no banco 'gastos.db'.")
