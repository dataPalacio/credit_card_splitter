from db.database import MongoDB

def test_conexao():
    db = MongoDB()
    print("Server info:", db.client.server_info())

if __name__ == "__main__":
    test_conexao()