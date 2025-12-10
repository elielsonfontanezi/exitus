"""M7.1 - ConfiguracaoAlerta Service"""
from app.models.configuracao_alerta import ConfiguracaoAlerta
from sqlalchemy import desc

class ConfiguracaoAlertaService:
    @staticmethod
    def list_by_usuario(usuario_id, ativo_id=None):
        query = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id)
        if ativo_id:
            query = query.filter_by(ativo_id=ativo_id)
        return [a.to_dict() for a in query.order_by(desc(ConfiguracaoAlerta.timestamp_criacao)).all()]

    @staticmethod
    def create(usuario_id, data):
        alerta = ConfiguracaoAlerta(usuario_id=usuario_id, **data)
        db.session.add(alerta)
        db.session.commit()
        db.session.refresh(alerta)
        return alerta.to_dict()

    @staticmethod
    def update(usuario_id, alerta_id, data):
        alerta = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id, id=alerta_id).first_or_404()
        for key, value in data.items():
            setattr(alerta, key, value)
        db.session.commit()
        return alerta.to_dict()

    @staticmethod
    def delete(usuario_id, alerta_id):
        alerta = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id, id=alerta_id).first_or_404()
        db.session.delete(alerta)
        db.session.commit()
