# db/config.py
class Config:
    """
    Configurações de conexão com o MongoDB para diferentes ambientes
    """
    
    # Configuração principal (MongoDB Atlas)
    MONGO_URI = "mongodb+srv://gfpalacio:Gfelipe11!@cluster0.mongodb.net/yourdbname?retryWrites=true&w=majority&appName=CreditCardSplitter"
    
    # Fallback direto (sem SRV)
    MONGO_URI_FALLBACK = "mongodb://gfpalacio:Gfelipe11!@cluster0-shard-00-00.mongodb.net:27017,cluster0-shard-00-01.mongodb.net:27017,cluster0-shard-00-02.mongodb.net:27017/yourdbname?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
    
    # Desenvolvimento local com Docker
    LOCAL_MONGO = "mongodb://localhost:27017/credit_card_splitter"
    
    @classmethod
    def get_mongo_uri(cls, use_local=False):
        """Retorna a URI apropriada para o ambiente"""
        if use_local:
            return cls.LOCAL_MONGO
        try:
            # Testa a conexão principal primeiro
            from pymongo import MongoClient
            client = MongoClient(cls.MONGO_URI, serverSelectionTimeoutMS=5000)
            client.server_info()
            return cls.MONGO_URI
        except:
            try:
                # Testa fallback se principal falhar
                client = MongoClient(cls.MONGO_URI_FALLBACK, serverSelectionTimeoutMS=5000)
                client.server_info()
                return cls.MONGO_URI_FALLBACK
            except:
                return cls.LOCAL_MONGO