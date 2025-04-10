from typing import List, Dict
from collections import defaultdict

class ExpenseDivider:
    """
    Classe responsável por calcular a divisão proporcional dos gastos entre pessoas
    com base nos limites definidos.
    """

    def calcular_divisao(self, gastos: List[Dict], limites: Dict[str, float]) -> dict[str, float]:
        total_limites = sum(limites.values())
        if total_limites == 0:
            raise ValueError("Os limites não podem ser todos zero.")
        
        totais = defaultdict(float)

        for gasto in gastos:
            valor = float(gasto["valor"])
            for pessoa, limite in limites.items():
                proporcao = limite / total_limites
                totais[pessoa] += round(valor * proporcao, 2)

        return dict(totais)
