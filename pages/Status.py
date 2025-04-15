import streamlit as st
from database import MongoDB

def run():
    st.title("🔍 Status da Conexão com o MongoDB")
    
    db = MongoDB()
    
    with st.expander("Teste de Conexão"):
        try:
            info = db.client.server_info()
            st.success("✅ Conexão ativa com MongoDB Atlas")
            st.json({
                "Versão do MongoDB": info["version"],
                "Banco de dados": db.client.list_database_names(),
                "Coleções": db.db.list_collection_names()
            })
        except Exception as e:
            st.error(f"❌ Falha na conexão: {str(e)}")
    
    with st.expander("Teste CRUD"):
        # Teste de criação
        test_data = {
            "descricao": "TESTE - Conexão",
            "valor": 88.88,
            "categoria": "Teste",
            "data": "2023-01-01",
            "usuario": "usuario_teste"
        }
        
        if st.button("Executar Teste CRUD"):
            with st.spinner("Executando testes..."):
                try:
                    # Create
                    id_inserido = db.inserir_compra(test_data)
                    st.success(f"Insert OK - ID: {id_inserido}")
                    
                    # Read
                    registros = db.listar_compras({"descricao": "TESTE - Conexão"})
                    st.success(f"Read OK - Registros: {len(registros)}")
                    
                    if registros:
                        # Update
                        atualizado = db.atualizar_compra(registros[0]["_id"], {"valor": 99.99})
                        st.success(f"Update OK: {atualizado}")
                        
                        # Delete
                        excluido = db.excluir_compra(registros[0]["_id"])
                        st.success(f"Delete OK: {excluido}")
                except Exception as e:
                    st.error(f"Falha no teste CRUD: {str(e)}")