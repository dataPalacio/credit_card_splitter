import sqlite3
import pandas as pd
import os

DB_PATH = "db/gastos.db"

def conectar_banco():
    """Cria conexão com o banco SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def calcular_totais():
    """
    Calcula o total de gastos por responsável.
    
    Retorna:
        dict: {'Nome1': total1, 'Nome2': total2, ...}
    """
    with conectar_banco() as conn:
        df = pd.read_sql_query("SELECT responsavel, valor FROM compras", conn)
    
    totais = df.groupby("responsavel")["valor"].sum().to_dict()
    return totais

def calcular_limites_restantes():
    """
    Calcula quanto cada pessoa ainda pode gastar com base no limite informado
    e nos gastos já registrados.
    
    Retorna:
        list[dict]: [{'pessoa': str, 'limite': float, 'gasto_total': float, 'restante': float}, ...]
    """
    with conectar_banco() as conn:
        df_gastos = pd.read_sql_query("SELECT responsavel, valor FROM compras", conn)
        df_limites = pd.read_sql_query("SELECT pessoa, limite FROM limites", conn)

    totais = df_gastos.groupby("responsavel")["valor"].sum().reset_index()
    merged = pd.merge(df_limites, totais, how="left", left_on="pessoa", right_on="responsavel")
    merged["valor"] = merged["valor"].fillna(0)
    merged["restante"] = merged["limite"] - merged["valor"]

    # Renomeando 'valor' para 'gasto_total' para maior clareza
    merged = merged.rename(columns={"valor": "gasto_total"})

    return merged[["pessoa", "limite", "gasto_total", "restante"]].to_dict(orient="records")
