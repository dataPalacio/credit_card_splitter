
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "db/gastos.db"

def conectar_banco():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            cartao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            parcelas INTEGER DEFAULT 1,
            parcela_atual INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS limites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa TEXT UNIQUE,
            limite REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_compra(dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO compras (descricao, valor, data, responsavel, cartao, categoria, parcelas, parcela_atual)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', dados)
    conn.commit()
    conn.close()

def definir_limite(pessoa, limite):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO limites (pessoa, limite) VALUES (?, ?)", (pessoa, limite))
    conn.commit()
    conn.close()

def obter_limites():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM limites", conn)
    conn.close()
    return df

def carregar_dados():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM compras ORDER BY data DESC", conn)
    conn.close()
    return df

st.set_page_config(page_title="Cartão Compartilhado", layout="centered")
st.title("💳 Controle Compartilhado de Cartões")

criar_tabelas()

# Formulário para adicionar compra
st.subheader("➕ Adicionar Nova Compra")
with st.form("form_compra"):
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
    data = st.date_input("Data", value=date.today())
    responsavel = st.selectbox("Responsável", ["Gustavo", "Esposa"])
    cartao = st.selectbox("Cartão", ["Inter", "Itau", "Nubank"])
    categoria = st.text_input("Categoria", value="Outros")
    parcelas = st.number_input("Parcelas", min_value=1, max_value=12, value=1)
    parcela_atual = st.number_input("Parcela Atual", min_value=1, max_value=12, value=1)
    submitted = st.form_submit_button("Adicionar")

    if submitted:
        adicionar_compra((descricao, valor, data.strftime("%Y-%m-%d"), responsavel, cartao, categoria, parcelas, parcela_atual))
        st.success("✅ Compra adicionada com sucesso!")

# Formulário para definir limites
st.subheader("⚙️ Definir Limite de Gastos")
with st.form("form_limite"):
    pessoa = st.selectbox("Pessoa", ["Gustavo", "Esposa"])
    limite = st.number_input("Limite de Gastos (R$)", min_value=0.0, step=10.0)
    submitted2 = st.form_submit_button("Salvar Limite")

    if submitted2:
        definir_limite(pessoa, limite)
        st.success(f"✅ Limite salvo para {pessoa}: R$ {limite:.2f}")

# Mostrar compras e limites
st.subheader("📋 Compras Registradas")
df_compras = carregar_dados()
st.dataframe(df_compras, use_container_width=True)

st.subheader("📊 Limites Definidos")
df_limites = obter_limites()
st.dataframe(df_limites, use_container_width=True)
