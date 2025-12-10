from decimal import Decimal
from typing import List


class AnaliseService:
    @staticmethod
    def calcular_sharpe(
        retornos: List[Decimal],
        taxa_livre_risco: Decimal,
    ) -> Decimal:
        """
        TODO: implementar de fato com numpy/pandas.
        Placeholder: retorna 0.
        """
        return Decimal("0")

    @staticmethod
    def calcular_sortino(
        retornos: List[Decimal],
        taxa_livre_risco: Decimal,
    ) -> Decimal:
        return Decimal("0")

    @staticmethod
    def calcular_max_drawdown(
        valores: List[Decimal],
    ) -> Decimal:
        return Decimal("0")

    @staticmethod
    def calcular_irr(
        fluxos: List[Decimal],
    ) -> Decimal:
        """
        TODO: implementar Newton-Raphson conforme especificação M7.4.
        """
        return Decimal("0")
