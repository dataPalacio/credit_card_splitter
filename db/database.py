import socket
import dns.resolver
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.get_mongo_uri(), ...)
        # Resto do código

def test_dns_resolution():
    try:
        # Teste manual de DNS
        print("Testando resolução DNS...")
        socket.gethostbyname('cluster0.mongodb.net')
        print("✅ DNS resolvido com sucesso")
        return True
    except socket.gaierror:
        print("❌ Falha na resolução DNS")
        return False

def create_connection():
    try:
        # 1. Primeira tentativa: Conexão SRV padrão
        uri = "mongodb+srv://gfpalacio:Gfelipe11!@cluster0.mongodb.net/yourdbname?retryWrites=true&w=majority"
        client = MongoClient(uri, 
                           connectTimeoutMS=10000,
                           socketTimeoutMS=10000,
                           serverSelectionTimeoutMS=10000)
        client.server_info()  # Testa a conexão
        print("✅ Conexão SRV bem-sucedida!")
        return client
        
    except Exception as srv_error:
        print(f"⚠️ Falha na conexão SRV: {srv_error}")
        
        try:
            # 2. Segunda tentativa: Conexão direta com todos os nós
            uri = "mongodb://<USER>:<PASSWORD>@cluster0-shard-00-00.mongodb.net:27017,cluster0-shard-00-01.mongodb.net:27017,cluster0-shard-00-02.mongodb.net:27017/yourdbname?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
            client = MongoClient(uri,
                               connectTimeoutMS=15000,
                               socketTimeoutMS=15000)
            client.server_info()
            print("✅ Conexão direta bem-sucedida!")
            return client
            
        except Exception as direct_error:
            print(f"❌ Falha na conexão direta: {direct_error}")
            raise ConnectionFailure("Não foi possível estabelecer conexão com nenhum método")

# Teste inicial
if __name__ == "__main__":
    if test_dns_resolution():
        try:
            client = create_connection()
            print("Informações do servidor:", client.server_info())
        except Exception as e:
            print("Falha crítica:", str(e))
    else:
        print("Problema de DNS detectado. Verifique sua conexão com a internet.")