"""M7.1 - ConfiguracaoAlerta Service"""
from app.models.configuracao_alerta import ConfiguracaoAlerta
from app.database import db
from app.utils.db_utils import safe_commit, safe_delete_commit
from app.utils.tenant import filter_by_assessora
from sqlalchemy import desc

class ConfiguracaoAlertaService:
    @staticmethod
    def list_by_usuario(usuario_id, ativo_id=None):
        query = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id)
        query = filter_by_assessora(query, ConfiguracaoAlerta)
        if ativo_id:
            query = query.filter_by(ativo_id=ativo_id)
        return [a.to_dict() for a in query.order_by(desc(ConfiguracaoAlerta.timestamp_criacao)).all()]

    @staticmethod
    def create(usuario_id, data):
        alerta = ConfiguracaoAlerta(usuario_id=usuario_id, **data)
        db.session.add(alerta)
        safe_commit()
        db.session.refresh(alerta)
        return alerta.to_dict()

    @staticmethod
    def update(usuario_id, alerta_id, data):
        query = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id, id=alerta_id)
        query = filter_by_assessora(query, ConfiguracaoAlerta)
        alerta = query.first_or_404()
        for key, value in data.items():
            setattr(alerta, key, value)
        safe_commit()
        return alerta.to_dict()

    @staticmethod
    def delete(usuario_id, alerta_id):
        query = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id, id=alerta_id)
        query = filter_by_assessora(query, ConfiguracaoAlerta)
        alerta = query.first_or_404()
        safe_delete_commit(alerta)
