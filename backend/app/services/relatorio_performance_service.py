"""M7.1 - RelatorioPerformance Service COMPLETO"""
from app import db
from app.models.relatorio_performance import RelatorioPerformance
from sqlalchemy import desc

class RelatorioPerformanceService:
    @staticmethod
    def list_by_usuario(usuario_id, portfolio_id=None, periodo='12m'):
        query = RelatorioPerformance.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        return [r.to_dict() for r in query.order_by(desc(RelatorioPerformance.created_at)).all()]

    @staticmethod
    def generate(usuario_id, data):
        relatorio = RelatorioPerformance(usuario_id=usuario_id, **data)
        db.session.add(relatorio)
        db.session.commit()
        db.session.refresh(relatorio)
        return relatorio.to_dict()

    @staticmethod
    def get_by_id(usuario_id, relatorio_id):
        relatorio = RelatorioPerformance.query.filter_by(usuario_id=usuario_id, id=relatorio_id).first()
        return relatorio.to_dict() if relatorio else {}
