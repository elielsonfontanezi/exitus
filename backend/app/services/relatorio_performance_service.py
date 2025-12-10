from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any

from app.database import db
from app.models import RelatorioPerformance


class RelatorioPerformanceService:
    @staticmethod
    def calcular_performance(usuario_id: str,
                             periodo_inicio: str,
                             periodo_fim: str) -> Dict[str, Any]:
        data_inicio = date.fromisoformat(periodo_inicio)
        data_fim = date.fromisoformat(periodo_fim)

        # TODO: substituir por cálculo real (usando Transacao, Posicao, etc.)
        relatorio = RelatorioPerformance(
            usuario_id=usuario_id,
            periodo_inicio=data_inicio,
            periodo_fim=data_fim,
            retorno_bruto_percentual=Decimal("18.50"),
            retorno_liquido_percentual=Decimal("15.20"),
            volatilidade_percentual=Decimal("12.30"),
            indice_sharpe=Decimal("1.45"),
            indice_sortino=Decimal("1.80"),
            max_drawdown_percentual=Decimal("-8.75"),
            taxa_interna_retorno_irr=Decimal("0.16"),
            beta_mercado=Decimal("1.05"),
            alfa_jensen=Decimal("0.02"),
            valor_patrimonial_inicio=Decimal("100000.00"),
            valor_patrimonial_fim=Decimal("118500.00"),
            alocacao_por_classe={},
            alocacao_por_setor={},
            alocacao_por_pais={},
            rentabilidade_por_ativo={},
            timestamp_calculo=datetime.utcnow(),
        )

        db.session.add(relatorio)
        db.session.commit()

        return {
            "id": str(relatorio.id),
            "usuario_id": str(relatorio.usuario_id),
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim,
            "retorno_bruto_percentual": float(relatorio.retorno_bruto_percentual),
            "retorno_liquido_percentual": float(relatorio.retorno_liquido_percentual),
            "status": "criado_com_sucesso",
        }
