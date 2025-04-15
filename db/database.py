import os
from typing import Optional, List, Dict
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import pandas as pd
import certifi
from datetime import datetime
import streamlit as st

class MongoDB:
    """
    Classe utilitária para gerenciar conexão e operações no MongoDB Atlas.
    """
    
    def __init__(self):
        self.client = self._get_client()
        self.db = self.client.get_database("toliso_db")
        self.compras_collection = self.db.get_collection("compras")
        
    @staticmethod
    def _get_client():
        """Cria e retorna uma conexão segura com o MongoDB Atlas"""
        try:
            # Configuração para desenvolvimento local e Streamlit Sharing
            if 'MONGO_URI' in st.secrets:
                uri = st.secrets["MONGO_URI"]
            else:
                uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
                
            return MongoClient(uri, tlsCAFile=certifi.where())
        except Exception as e:
            st.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            raise

    def inserir_compra(self, compra_data: Dict) -> Optional[str]:
        """
        Insere uma nova compra no banco de dados.
        
        Args:
            compra_data: Dicionário com os dados da compra
                Exemplo: {
                    "descricao": "Supermercado",
                    "valor": 150.50,
                    "categoria": "Alimentação",
                    "data": "2023-05-15",
                    "usuario": "user123"
                }
                
        Returns:
            ObjectId da compra inserida ou None em caso de erro
        """
        try:
            # Adiciona timestamp automático
            compra_data["timestamp"] = datetime.utcnow()
            
            result = self.compras_collection.insert_one(compra_data)
            return str(result.inserted_id)
        except PyMongoError as e:
            st.error(f"Erro ao inserir compra: {str(e)}")
            return None

    def listar_compras(self, filtro: Optional[Dict] = None, limite: int = 100) -> List[Dict]:
        """
        Lista compras do banco de dados com opção de filtro.
        
        Args:
            filtro: Dicionário com critérios de filtro (ex: {"usuario": "user123"})
            limite: Número máximo de registros a retornar
            
        Returns:
            Lista de dicionários com as compras
        """
        try:
            cursor = self.compras_collection.find(filtro or {}).sort("timestamp", -1).limit(limite)
            return list(cursor)
        except PyMongoError as e:
            st.error(f"Erro ao listar compras: {str(e)}")
            return []

    def listar_compras_dataframe(self, filtro: Optional[Dict] = None) -> pd.DataFrame:
        """
        Lista compras e retorna como DataFrame pandas.
        
        Args:
            filtro: Dicionário com critérios de filtro
            
        Returns:
            DataFrame com as compras
        """
        try:
            compras = self.listar_compras(filtro)
            df = pd.DataFrame(compras)
            
            if not df.empty:
                if "_id" in df.columns:
                    df["_id"] = df["_id"].astype(str)
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                if "data" in df.columns:
                    df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%y-%m-%d")
                    
            return df
        except Exception as e:
            st.error(f"Erro ao converter para DataFrame: {str(e)}")
            return pd.DataFrame()

    def atualizar_compra(self, compra_id: str, novos_dados: Dict) -> bool:
        """
        Atualiza uma compra existente.
        
        Args:
            compra_id: ID da compra a ser atualizada
            novos_dados: Dicionário com campos a atualizar
            
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            result = self.compras_collection.update_one(
                {"_id": compra_id},
                {"$set": novos_dados}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            st.error(f"Erro ao atualizar compra: {str(e)}")
            return False

    def excluir_compra(self, compra_id: str) -> bool:
        """
        Exclui uma compra do banco de dados.
        
        Args:
            compra_id: ID da compra a ser excluída
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            result = self.compras_collection.delete_one({"_id": compra_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            st.error(f"Erro ao excluir compra: {str(e)}")
            return False

# Função de compatibilidade para manter a interface existente
def listar_compras() -> pd.DataFrame:
    db = MongoDB()
    return db.listar_compras_dataframe()

    # Adicione este código no seu database.py
def testar_conexao():
    try:
        client = MongoDB().client
        info = client.server_info()  # Testa a conexão
        print("✅ Conexão com MongoDB Atlas bem-sucedida!")
        print(f"Versão do servidor: {info['version']}")
        print(f"Banco de dados disponíveis: {client.list_database_names()}")
        return True
    except Exception as e:
        print(f"❌ Falha na conexão: {str(e)}")
        return False

# Execute o teste
if __name__ == "__main__":
    testar_conexao()