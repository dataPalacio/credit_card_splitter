def aplicar_filtros(despesas, cartao=None, pessoa=None, categoria=None):
    return [
        d for d in despesas
        if (not cartao or d['cartao'] == cartao)
        and (not pessoa or d['responsavel'] == pessoa)
        and (not categoria or d['categoria'] == categoria)
    ]
