from db.database import init_db
from core.calculator import calcular_divisao

if __name__ == "__main__":
    init_db()
    print("Sistema iniciado. Em breve, interface via Streamlit.")
    calcular_divisao()
