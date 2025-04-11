import sys
import os

# Adiciona o diretório raiz ao sys.path para importar módulos internos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.models import criar_tabelas

def inicializar_banco():
    """
    Inicializa o banco de dados criando todas as tabelas necessárias.
    """
    criar_tabelas()
    print("✅ Banco inicializado com tabelas vazias no diretório 'db/'.")

if __name__ == "__main__":
    inicializar_banco()
