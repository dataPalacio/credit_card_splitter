import sys
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.database import Database
from core.calculator import ExpenseDivider

def safe_db_operation(operation):
    try:
        return operation()
    except sqlite3.Error as e:
        st.error(f"Erro no banco de dados: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None

st.set_page_config(page_title="Divisor de Fatura", layout="wide")
st.title("💳 Divisor de Fatura de Cartão de Crédito")

# --- Instanciar banco
db = Database()

# --- Dados do banco
compras = safe_db_operation(lambda: db.execute_dataframe("SELECT * FROM compras"))
pessoas = safe_db_operation(lambda: db.execute_dataframe("SELECT * FROM pessoas"))
cartoes = safe_db_operation(lambda: db.execute_dataframe("SELECT * FROM cartoes"))

if compras is None:
    compras = pd.DataFrame()
if pessoas is None:
    pessoas = pd.DataFrame(columns=["nome", "limite"])
if cartoes is None:
    cartoes = pd.DataFrame(columns=["nome"])

# --- Filtro por mês
st.sidebar.header("📅 Filtrar por mês")
if not compras.empty:
    compras['ano_mes'] = pd.to_datetime(compras['data']).dt.strftime('%Y-%m')
    meses_disponiveis = compras['ano_mes'].unique().tolist()
    mes_selecionado = st.sidebar.selectbox("Mês", sorted(meses_disponiveis, reverse=True))
    compras_filtradas = compras[compras['ano_mes'] == mes_selecionado]
else:
    st.warning("Nenhuma compra encontrada no banco de dados.")
    compras_filtradas = pd.DataFrame()

# --- Mostrar compras filtradas
if not compras_filtradas.empty:
    st.subheader(f"📋 Compras em {mes_selecionado}")
    st.dataframe(compras_filtradas.drop(columns=["ano_mes"]), use_container_width=True)
else:
    st.info("Nenhuma compra registrada para o mês selecionado.")

# --- Botão para excluir compra
st.subheader("🗑️ Excluir Compras")
if not compras_filtradas.empty:
    compras_filtradas["opcao"] = compras_filtradas.apply(
        lambda row: f"{row['id']} - {row['descricao']} (R$ {row['valor']:.2f})", axis=1
    )
    selecao = st.selectbox("Selecione a compra para excluir", compras_filtradas["opcao"])
    id_excluir = int(selecao.split(" - ")[0])

    if st.button("❌ Confirmar Exclusão"):
        db.execute_query("DELETE FROM compras WHERE id = ?", (id_excluir,))
        st.success(f"Compra com ID {id_excluir} excluída com sucesso.")
        st.rerun()
else:
    st.info("Nenhuma compra para excluir.")

# --- Atualizar/adicionar limite de cada pessoa
st.sidebar.header("💰 Limites de Gastos")
limites = {}
for _, row in pessoas.iterrows():
    novo_limite = st.sidebar.number_input(
        f"Limite de {row['nome']}", value=float(row["limite"]), step=50.0
    )
    limites[row["nome"]] = novo_limite
    db.execute_query("UPDATE pessoas SET limite = ? WHERE nome = ?", (novo_limite, row["nome"]))

# --- Divisão automática
if not compras_filtradas.empty and st.sidebar.button("📊 Calcular Divisão"):
    gastos = compras_filtradas.to_dict(orient="records")
    try:
        resultado = ExpenseDivider().calcular_divisao(gastos, limites)
        st.subheader("📈 Divisão das Despesas")
        st.table(
            pd.DataFrame.from_dict(resultado, orient='index', columns=['Total a Pagar'])
            .reset_index().rename(columns={"index": "Pessoa"})
        )
    except Exception as e:
        st.error(f"Erro ao calcular divisão: {e}")

# --- Gráfico de gastos por pessoa
if not compras_filtradas.empty:
    st.subheader("📊 Gráfico de Gastos por Pessoa")
    gastos_por_pessoa = compras_filtradas.groupby("responsavel")["valor"].sum()
    fig, ax = plt.subplots()
    gastos_por_pessoa.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_ylabel("Total Gasto (R$)")
    ax.set_title("Gastos por Pessoa")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig)

# --- Adicionar nova compra
st.sidebar.header("➕ Nova Compra")
with st.sidebar.form("nova_compra"):
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", step=10.0)
    data = st.date_input("Data da compra")
    responsavel = st.selectbox("Responsável", pessoas["nome"]) if not pessoas.empty else ""
    cartao = st.selectbox("Cartão", cartoes["nome"]) if not cartoes.empty else ""
    categoria = st.text_input("Categoria", value="Outros")
    parcelas = st.number_input("Parcelas", min_value=1, max_value=12, value=1)
    parcela_atual = st.number_input("Parcela Atual", min_value=1, max_value=12, value=1)
    submitted = st.form_submit_button("Adicionar")

    if submitted:
        db.execute_query("""
            INSERT INTO compras (descricao, valor, data, responsavel, cartao, categoria, parcelas, parcela_atual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            descricao, valor, data.strftime("%Y-%m-%d"),
            responsavel, cartao, categoria, parcelas, parcela_atual
        ))
        st.success("Compra adicionada com sucesso!")
        st.rerun()
