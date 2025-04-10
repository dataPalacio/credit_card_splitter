import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.models import criar_tabelas

def inicializar_banco():
    criar_tabelas()
    print("✅ Banco inicializado com tabelas vazias.")

if __name__ == "__main__":
    inicializar_banco()
