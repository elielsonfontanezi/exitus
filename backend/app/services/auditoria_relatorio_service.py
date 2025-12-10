"""M7.1 - AuditoriaRelatorio Service Completo"""
from app.models.auditoria_relatorio import AuditoriaRelatorio
from sqlalchemy import desc
from flask import current_app

class AuditoriaRelatorioService:
    @staticmethod
    def list_by_usuario(usuario_id, page=1, per_page=10):
        """Lista relatórios paginados por usuário"""
        query = AuditoriaRelatorio.query.filter_by(usuario_id=usuario_id)\
            .order_by(desc(AuditoriaRelatorio.timestamp_criacao))
        relatorios = query.paginate(page=page, per_page=per_page, error_out=False)
        return [r.to_dict() for r in relatorios.items]

    @staticmethod
    def create(usuario_id, data):
        """Cria novo relatório de auditoria"""
        relatorio = AuditoriaRelatorio(
            usuario_id=usuario_id,
            tipo_relatorio=data.get('tipo_relatorio', 'geral'),
            data_inicio=data.get('data_inicio'),
            data_fim=data.get('data_fim'),
            filtros=data.get('filtros', {}),
            formato_export='visualizacao'
        )
        current_app.db.session.add(relatorio)
        current_app.db.session.commit()
        current_app.db.session.refresh(relatorio)
        return relatorio.to_dict()
