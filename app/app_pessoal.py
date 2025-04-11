import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "gastos.db")

# ------------------------
# Banco de Dados
# ------------------------
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
            cartao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            parcelas INTEGER DEFAULT 1,
            parcela_atual INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS limite (
            id INTEGER PRIMARY KEY CHECK (id = 0),
            valor REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_compra(dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO compras (descricao, valor, data, cartao, categoria, parcelas, parcela_atual)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', dados)
    conn.commit()
    conn.close()

def editar_compra(id_compra, novos_dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE compras
        SET descricao = ?, valor = ?, data = ?, cartao = ?, categoria = ?, parcelas = ?, parcela_atual = ?
        WHERE id = ?
    ''', (*novos_dados, id_compra))
    conn.commit()
    conn.close()

def excluir_compra(id_compra):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compras WHERE id = ?", (id_compra,))
    conn.commit()
    conn.close()

def definir_limite(valor):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO limite (id, valor) VALUES (0, ?)", (valor,))
    conn.commit()
    conn.close()

def obter_limite():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM limite WHERE id = 0")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def carregar_dados():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM compras ORDER BY data DESC", conn)
    conn.close()
    return df

# ------------------------
# Interface Streamlit
# ------------------------
st.set_page_config(page_title="💸 Controle de Gastos Pessoais", layout="wide")
st.title("💸 Controle de Gastos Pessoais")

# Criar tabelas somente uma vez
if 'tabelas_criadas' not in st.session_state:
    criar_tabelas()
    st.session_state.tabelas_criadas = True

# Limite mensal
st.sidebar.header("Limite Mensal")
limite_atual = obter_limite()
novo_limite = st.sidebar.number_input("Definir Limite", value=float(limite_atual), step=50.0, format="%.2f")
if st.sidebar.button("Salvar Limite"):
    definir_limite(novo_limite)
    st.sidebar.success("Limite atualizado!")

# Formulário de nova compra
st.subheader("➕ Adicionar Novo Gasto")
with st.form("nova_compra"):
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", step=1.0, format="%.2f")
    data_gasto = st.date_input("Data", value=date.today())
    cartao = st.selectbox("Cartão", ["Crédito", "Débito", "Outro"])
    categoria = st.text_input("Categoria", value="Outros")
    parcelas = st.number_input("Parcelas", min_value=1, value=1)
    parcela_atual = 1
    enviar = st.form_submit_button("Adicionar")

    if enviar:
        if descricao and valor > 0:
            dados = (descricao, valor, str(data_gasto), cartao, categoria, parcelas, parcela_atual)
            adicionar_compra(dados)
            st.success("✅ Gasto adicionado com sucesso!")
            st.rerun()
        else:
            st.warning("⚠️ Preencha todos os campos corretamente.")

# Carregar dados
df = carregar_dados()

# Filtro por mês (opcional)
st.subheader("📋 Meus Gastos")
if not df.empty:
    df["data"] = pd.to_datetime(df["data"], errors='coerce')
    df.dropna(subset=["data"], inplace=True)
    df["ano_mes"] = df["data"].dt.strftime('%Y-%m')

    meses = sorted(df["ano_mes"].unique(), reverse=True)
    aplicar_filtro = st.checkbox("🔎 Filtrar por mês")

    if aplicar_filtro:
        mes_selecionado = st.selectbox("📅 Selecione o mês", meses)
        df_exibido = df[df["ano_mes"] == mes_selecionado]
        st.caption(f"Mostrando dados de: {mes_selecionado}")
    else:
        df_exibido = df

    st.dataframe(df_exibido.drop(columns=["ano_mes"]), use_container_width=True)

    total = df_exibido["valor"].sum()
    st.metric("Total Gasto", f"R$ {total:.2f}")
    st.metric("Limite Restante", f"R$ {obter_limite() - total:.2f}")

    # Editar/Excluir compra
    if not df_exibido.empty:
        st.markdown("### ✏️ Editar ou 🗑️ Excluir Compra")
        df_exibido["opcao"] = df_exibido.apply(lambda row: f"{row['id']} - {row['descricao']} (R$ {row['valor']:.2f})", axis=1)
        selecao = st.selectbox("Selecione uma compra", df_exibido["opcao"])
        id_sel = int(selecao.split(" - ")[0])
        dados = df_exibido[df_exibido["id"] == id_sel].iloc[0]

        with st.form("editar_compra"):
            nova_descricao = st.text_input("Descrição", value=dados["descricao"])
            novo_valor = st.number_input("Valor", value=float(dados["valor"]))
            nova_data = st.date_input("Data", value=dados["data"].date())
            novo_cartao = st.selectbox("Cartão", ["Crédito", "Débito", "Outro"], index=["Crédito", "Débito", "Outro"].index(dados["cartao"]))
            nova_categoria = st.text_input("Categoria", value=dados["categoria"])
            novas_parcelas = st.number_input("Parcelas", min_value=1, value=int(dados["parcelas"]))
            nova_parcela_atual = st.number_input("Parcela Atual", min_value=1, value=int(dados["parcela_atual"]))

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Salvar Alterações"):
                    editar_compra(id_sel, (
                        nova_descricao, novo_valor, str(nova_data),
                        novo_cartao, nova_categoria, novas_parcelas, nova_parcela_atual
                    ))
                    st.success("✅ Compra atualizada com sucesso.")
                    st.rerun()
            with col2:
                if st.form_submit_button("🗑️ Excluir Compra"):
                    excluir_compra(id_sel)
                    st.success("✅ Compra excluída com sucesso.")
                    st.rerun()
else:
    st.info("Nenhum gasto registrado ainda.")
