import sqlite3
import os

def criar_tabelas():
    caminho_db = os.path.join("data", "database.db")
    conn = sqlite3.connect(caminho_db)
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
    conn.close()
