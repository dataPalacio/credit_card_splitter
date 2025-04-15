import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
import os
import shutil
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "gastos.db")
BACKUP_DIR = os.path.join(BASE_DIR, "..", "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# ----------------------------------------
# 🔄 Backup Automático
# ----------------------------------------
def backup_banco():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"gastos_{timestamp}.db")
    shutil.copy(DB_PATH, backup_path)

# ----------------------------------------
# 🔧 Funções Auxiliares
# ----------------------------------------
def atualizar_pagina():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("Atualize a página manualmente")

def conexao_segura(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_PATH)
        try:
            return func(conn, *args, **kwargs)
        except sqlite3.Error as e:
            st.error(f"Erro: {e}")
            return None
        finally:
            conn.close()
    return wrapper

@conexao_segura
def criar_tabelas(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            nome TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cartoes (
            nome TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            nome TEXT PRIMARY KEY
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
            categoria TEXT NOT NULL,
            parcelas INTEGER DEFAULT 1,
            parcela_atual INTEGER DEFAULT 1,
            FOREIGN KEY (responsavel) REFERENCES pessoas(nome),
            FOREIGN KEY (cartao) REFERENCES cartoes(nome),
            FOREIGN KEY (categoria) REFERENCES categorias(nome)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS limites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa TEXT UNIQUE,
            limite REAL NOT NULL,
            FOREIGN KEY (pessoa) REFERENCES pessoas(nome)
        )
    ''')
    conn.commit()

@conexao_segura
def adicionar_compra(conn, dados):
    descricao, valor, data, responsavel, cartao, categoria, parcelas, parcela_atual = dados
    if not descricao or valor <= 0 or parcela_atual > parcelas:
        st.warning("⚠️ Dados inválidos. Verifique os campos antes de adicionar.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO compras (descricao, valor, data, responsavel, cartao, categoria, parcelas, parcela_atual)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', dados)
    conn.commit()

@conexao_segura
def editar_compra(conn, id_compra, novos_dados):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE compras
        SET descricao = ?, valor = ?, data = ?, responsavel = ?, cartao = ?, categoria = ?, parcelas = ?, parcela_atual = ?
        WHERE id = ?
    ''', (*novos_dados, id_compra))
    conn.commit()

@conexao_segura
def excluir_compra(conn, id_compra):
    backup_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compras WHERE id = ?", (id_compra,))
    conn.commit()

@conexao_segura
def definir_limite(conn, pessoa, limite):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO limites (pessoa, limite) VALUES (?, ?)", (pessoa, limite))
    conn.commit()

@conexao_segura
def obter_limites(conn):
    return pd.read_sql_query("SELECT * FROM limites", conn)

@conexao_segura
def carregar_dados(conn):
    return pd.read_sql_query("SELECT * FROM compras ORDER BY data DESC, valor DESC", conn)

# ----------------------------------------
# 🖥️ Interface do Streamlit
# ----------------------------------------
st.set_page_config(page_title="Cartão Compartilhado", layout="wide")
st.title("💳 Controle Compartilhado de Cartões")

criar_tabelas()

st.subheader("➕ Adicionar Nova Compra")
with st.form("form_compra"):
    col1, col2, col3 = st.columns(3)
    with col1:
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
        data = st.date_input("Data", value=date.today())
    with col2:
        responsavel = st.selectbox("Responsável", ["Gustavo", "Esposa"])
        cartao = st.selectbox("Cartão", ["Inter", "Itau", "Nubank"])
    with col3:
        categoria = st.text_input("Categoria", value="Outros")
        parcelas = st.number_input("Parcelas", min_value=1, max_value=12, value=1)
        parcela_atual = st.number_input("Parcela Atual", min_value=1, max_value=parcelas, value=1)

    if st.form_submit_button("Adicionar"):
        adicionar_compra((
            descricao, valor, data.strftime("%Y-%m-%d"), responsavel,
            cartao, categoria, parcelas, parcela_atual
        ))
        st.toast("Compra registrada com sucesso!", icon="✅")
        atualizar_pagina()

st.subheader("⚙️ Definir ou Editar Limite de Gastos")
with st.form("form_limite"):
    pessoa = st.selectbox("Pessoa", ["Gustavo", "Esposa"])
    limites_existentes = obter_limites().set_index("pessoa")
    valor_atual = float(limites_existentes.loc[pessoa]["limite"]) if pessoa in limites_existentes.index else 0.0
    limite = st.number_input("Limite de Gastos (R$)", min_value=0.0, step=10.0, value=valor_atual)
    if st.form_submit_button("Salvar Limite"):
        definir_limite(pessoa, limite)
        st.toast(f"Limite atualizado para {pessoa}: R$ {limite:.2f}", icon="💾")
        atualizar_pagina()

st.subheader("📋 Compras Registradas")
df_compras = carregar_dados()

if not df_compras.empty:
    df_compras["data"] = pd.to_datetime(df_compras["data"], errors='coerce')
    df_compras.dropna(subset=["data"], inplace=True)
    df_compras["ano_mes"] = df_compras["data"].dt.strftime('%Y-%m')

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
        novo_valor = st.number_input("Novo Valor", value=float(dados["valor"]))
    with col2:
        nova_categoria = st.text_input("Nova Categoria", value=dados["categoria"])
    with col3:
        novo_responsavel = st.selectbox("Novo Responsável", ["Gustavo", "Esposa"], index=["Gustavo", "Esposa"].index(dados["responsavel"]))

    col4, col5 = st.columns(2)
    with col4:
        novas_parcelas = st.number_input("Parcelas", min_value=1, max_value=12, value=int(dados["parcelas"]))
    with col5:
        nova_parcela_atual = st.number_input("Parcela Atual", min_value=1, max_value=novas_parcelas, value=int(dados["parcela_atual"]))

    if st.button("💾 Salvar Alterações"):
        editar_compra(id_selecionado, (
            dados["descricao"], novo_valor, dados["data"].strftime("%Y-%m-%d"),
            novo_responsavel, dados["cartao"], nova_categoria,
            novas_parcelas, nova_parcela_atual
        ))
        st.toast("Compra atualizada com sucesso!", icon="📝")
        atualizar_pagina()

    if st.checkbox("Confirmar exclusão"):
        if st.button("🗑️ Excluir Compra"):
            excluir_compra(id_selecionado)
            st.toast("Compra excluída com sucesso!", icon="🗑️")
            atualizar_pagina()
else:
    st.info("Nenhuma compra registrada ainda.")

st.subheader("📊 Limites Definidos")
df_limites = obter_limites()
st.dataframe(df_limites, use_container_width=True)

st.subheader("📈 Resumo por Pessoa")
if not df_compras.empty and not df_limites.empty:
    resumo = df_compras.groupby("responsavel")["valor"].sum().reset_index(name="total_gasto")
    resumo = resumo.merge(df_limites, left_on="responsavel", right_on="pessoa", how="left")
    resumo["restante"] = resumo["limite"] - resumo["total_gasto"]

    for _, row in resumo.iterrows():
        st.markdown(f"### 👤 {row['pessoa']}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Gasto", f"R$ {row['total_gasto']:.2f}")
        with col2:
            st.metric("Limite Definido", f"R$ {row['limite']:.2f}")

        if row["restante"] >= 0:
            st.success(f"✅ Ainda pode gastar: R$ {row['restante']:.2f}")
        else:
            st.error(f"❌ Excedeu o limite em: R$ {-row['restante']:.2f}")
else:
    st.info("Adicione compras e limites para visualizar o resumo.")

st.divider()
if st.button("⟳ Atualizar Página Manualmente"):
    atualizar_pagina()
