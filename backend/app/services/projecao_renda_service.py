from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from app.database import db
from app.models import ProjecaoRenda


class ProjecaoRendaService:
    @staticmethod
    def obter_ou_criar(
        usuario_id: str,
        mes_ano: str,
        portfolio_id: Optional[str] = None,
    ) -> ProjecaoRenda:
        proj = (
            ProjecaoRenda.query
            .filter_by(usuario_id=usuario_id, mes_ano=mes_ano, portfolio_id=portfolio_id)
            .first()
        )
        if proj:
            return proj

        proj = ProjecaoRenda(
            usuario_id=usuario_id,
            portfolio_id=portfolio_id,
            mes_ano=mes_ano,
            renda_dividendos_projetada=Decimal("0"),
            renda_jcp_projetada=Decimal("0"),
            renda_rendimento_projetada=Decimal("0"),
            renda_total_mes=Decimal("0"),
            renda_anual_projetada=None,
            crescimento_percentual_mes=None,
            crescimento_percentual_ano=None,
            ativos_contribuindo=0,
            timestamp_calculo=datetime.utcnow(),
            metadados={},
        )
        db.session.add(proj)
        db.session.commit()
        return proj

    @staticmethod
    def recalcular_para_usuario(
        usuario_id: str,
        mes_ano: str,
        portfolio_id: Optional[str] = None,
    ) -> ProjecaoRenda:
        """
        TODO: usar histórico real de Provento/Posicao para estimar.
        Por enquanto, mantém valores zerados ou mockados.
        """
        proj = ProjecaoRendaService.obter_ou_criar(
            usuario_id=usuario_id,
            mes_ano=mes_ano,
            portfolio_id=portfolio_id,
        )

        # Aqui entrará a lógica real de projeção no futuro
        proj.timestamp_calculo = datetime.utcnow()
        db.session.commit()
        return proj

    @staticmethod
    def listar_projecoes(
        usuario_id: str,
        portfolio_id: Optional[str] = None,
        limite: int = 12,
    ) -> List[ProjecaoRenda]:
        query = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        return (
            query.order_by(ProjecaoRenda.mes_ano.asc())
            .limit(limite)
            .all()
        )
