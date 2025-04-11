import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "gastos.db")

# ----------------------------------------
# 🔧 Funções de Banco de Dados
# ----------------------------------------
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
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO compras (descricao, valor, data, responsavel, cartao, categoria, parcelas, parcela_atual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', dados)
        conn.commit()
    finally:
        conn.close()

def editar_compra(id_compra, novos_dados):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE compras
            SET descricao = ?, valor = ?, data = ?, responsavel = ?, cartao = ?, categoria = ?, parcelas = ?, parcela_atual = ?
            WHERE id = ?
        ''', (*novos_dados, id_compra))
        conn.commit()
    finally:
        conn.close()

def excluir_compra(id_compra):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM compras WHERE id = ?", (id_compra,))
        conn.commit()
    finally:
        conn.close()

def definir_limite(pessoa, limite):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO limites (pessoa, limite) VALUES (?, ?)", (pessoa, limite))
        conn.commit()
    finally:
        conn.close()

def obter_limites():
    try:
        conn = conectar_banco()
        df = pd.read_sql_query("SELECT * FROM limites", conn)
        return df
    finally:
        conn.close()

def carregar_dados():
    try:
        conn = conectar_banco()
        df = pd.read_sql_query("SELECT * FROM compras ORDER BY data DESC", conn)
        return df
    finally:
        conn.close()

# ----------------------------------------
# 🖥️ Interface do Streamlit
# ----------------------------------------
st.set_page_config(page_title="Cartão Compartilhado", layout="centered")
st.title("💳 Controle Compartilhado de Cartões")

criar_tabelas()

# ➕ Adicionar Nova Compra
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
        if descricao and valor:
            adicionar_compra((descricao, valor, data.strftime("%Y-%m-%d"), responsavel, cartao, categoria, parcelas, parcela_atual))
            st.success("✅ Compra adicionada com sucesso!")
        else:
            st.warning("⚠️ Preencha todos os campos obrigatórios.")

# ⚙️ Definir ou Editar Limite de Gastos
st.subheader("⚙️ Definir ou Editar Limite de Gastos")
with st.form("form_limite"):
    pessoa = st.selectbox("Pessoa", ["Gustavo", "Esposa"])
    limites_existentes = obter_limites().set_index("pessoa")
    valor_atual = float(limites_existentes.loc[pessoa]["limite"]) if pessoa in limites_existentes.index else 0.0
    limite = st.number_input("Limite de Gastos (R$)", min_value=0.0, step=10.0, value=valor_atual)
    submitted2 = st.form_submit_button("Salvar Limite")

    if submitted2:
        definir_limite(pessoa, limite)
        st.success(f"✅ Limite atualizado para {pessoa}: R$ {limite:.2f}")

# 📋 Compras Registradas com Filtro por Mês
st.subheader("📋 Compras Registradas")
df_compras = carregar_dados()

if not df_compras.empty:
    df_compras["data"] = pd.to_datetime(df_compras["data"], errors='coerce')
    df_compras.dropna(subset=["data"], inplace=True)
    df_compras["ano_mes"] = df_compras["data"].dt.strftime('%Y-%m')
    df_compras["parcelas"] = pd.to_numeric(df_compras["parcelas"], errors="coerce").fillna(1).astype(int)
    df_compras["parcela_atual"] = pd.to_numeric(df_compras["parcela_atual"], errors="coerce").fillna(1).astype(int)

    meses = sorted(df_compras["ano_mes"].unique(), reverse=True)
    mes_selecionado = st.selectbox("📅 Filtrar por Mês", meses)

    df_filtrado = df_compras[df_compras["ano_mes"] == mes_selecionado]
    st.dataframe(df_filtrado.drop(columns=["ano_mes"]), use_container_width=True)

    st.markdown("### ✏️ Editar/Excluir Compra")
    df_filtrado["opcao"] = df_filtrado.apply(
        lambda row: f"{row['id']} - {row['descricao']} (R$ {row['valor']:.2f})", axis=1
    )
    selecao = st.selectbox("Selecione uma compra", df_filtrado["opcao"])
    id_selecionado = int(selecao.split(" - ")[0])
    dados = df_filtrado[df_filtrado["id"] == id_selecionado].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        novo_valor = st.number_input("Novo Valor", value=float(dados["valor"]), key="valor_edit")
    with col2:
        nova_categoria = st.text_input("Nova Categoria", value=dados["categoria"], key="cat_edit")
    with col3:
        novo_responsavel = st.selectbox("Novo Responsável", ["Gustavo", "Esposa"], index=["Gustavo", "Esposa"].index(dados["responsavel"]), key="resp_edit")

    col4, col5, col6 = st.columns(3)
    with col4:
        novas_parcelas = st.number_input("Parcelas", min_value=1, max_value=12, value=int(dados["parcelas"]), key="parc_edit")
    with col5:
        nova_parcela_atual = st.number_input("Parcela Atual", min_value=1, max_value=12, value=int(dados["parcela_atual"]), key="atual_edit")
    with col6:
        if st.button("💾 Salvar Alterações"):
            editar_compra(id_selecionado, (
                dados["descricao"], novo_valor, dados["data"].strftime("%Y-%m-%d"),
                novo_responsavel, dados["cartao"], nova_categoria,
                novas_parcelas, nova_parcela_atual
            ))
            st.success("✅ Compra atualizada com sucesso!")
            st.experimental_rerun()

    if st.button("🗑️ Excluir Compra"):
        excluir_compra(id_selecionado)
        st.success(f"✅ Compra ID {id_selecionado} excluída com sucesso.")
        st.experimental_rerun()
else:
    st.info("Nenhuma compra registrada ainda.")

# 📊 Limites Definidos
st.subheader("📊 Limites Definidos")
df_limites = obter_limites()
st.dataframe(df_limites, use_container_width=True)

# 📈 Resumo por Pessoa
st.subheader("📈 Resumo por Pessoa")
if not df_compras.empty and not df_limites.empty:
    resumo = df_compras.groupby("responsavel")["valor"].sum().reset_index(name="total_gasto")
    resumo = resumo.merge(df_limites, left_on="responsavel", right_on="pessoa", how="left")
    resumo["restante"] = resumo["limite"] - resumo["total_gasto"]

    for _, row in resumo.iterrows():
        st.markdown(f"### 👤 {row['pessoa']}")
        st.markdown(f"- 💸 Total gasto: **R$ {row['total_gasto']:.2f}**")
        st.markdown(f"- 💰 Limite definido: **R$ {row['limite']:.2f}**")
        if row["restante"] >= 0:
            st.success(f"✅ Ainda pode gastar: **R$ {row['restante']:.2f}**")
        else:
            st.error(f"❌ Excedeu o limite em: **R$ {-row['restante']:.2f}**")
else:
    st.info("Adicione compras e limites para visualizar o resumo.")