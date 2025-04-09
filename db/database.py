import sqlite3

def init_db():
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY,
            descricao TEXT,
            valor REAL,
            data TEXT,
            responsavel TEXT,
            cartao TEXT,
            categoria TEXT,
            parcelas INTEGER,
            parcela_atual INTEGER
        )
    ''')

    conn.commit()
    conn.close()
