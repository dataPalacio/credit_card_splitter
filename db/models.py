# Modelos para facilitar consultas futuras

class Compra:
    def __init__(self, id, descricao, valor, data, responsavel, cartao, categoria, parcelas, parcela_atual):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.responsavel = responsavel
        self.cartao = cartao
        self.categoria = categoria
        self.parcelas = parcelas
        self.parcela_atual = parcela_atual
