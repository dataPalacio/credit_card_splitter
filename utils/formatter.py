from datetime import datetime

def formatar_data(data_str):
    return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
