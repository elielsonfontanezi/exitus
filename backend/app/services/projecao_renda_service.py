"""M7.1 - ProjecaoRenda Service COMPLETO"""
from app import db
from app.models.projecao_renda import ProjecaoRenda
from sqlalchemy import desc

class ProjecaoRendaService:
    @staticmethod
    def list_by_usuario(usuario_id, portfolio_id=None, mes_ano=None):
        query = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        if mes_ano:
            query = query.filter_by(mes_ano=mes_ano)
        return [p.to_dict() for p in query.order_by(desc(ProjecaoRenda.created_at)).all()]

    @staticmethod
    def create_or_update(usuario_id, data):
        projecao = ProjecaoRenda(usuario_id=usuario_id, **data)
        db.session.add(projecao)
        db.session.commit()
        db.session.refresh(projecao)
        return projecao.to_dict()

    @staticmethod
    def get_by_mes_ano(usuario_id, mes_ano):
        projecao = ProjecaoRenda.query.filter_by(usuario_id=usuario_id, mes_ano=mes_ano).first()
        return projecao.to_dict() if projecao else {}
