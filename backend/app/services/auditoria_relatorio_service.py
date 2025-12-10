from datetime import datetime
from typing import List, Optional, Dict, Any

from app.database import db
from app.models import AuditoriaRelatorio, TipoRelatorio, FormatoExport


class AuditoriaRelatorioService:
    @staticmethod
    def listar_por_usuario(usuario_id: str,
                           tipo_relatorio: Optional[TipoRelatorio] = None,
                           limite: int = 50) -> List[AuditoriaRelatorio]:
        query = AuditoriaRelatorio.query.filter_by(usuario_id=usuario_id)

        if tipo_relatorio:
            query = query.filter_by(tipo_relatorio=tipo_relatorio)

        return query.order_by(AuditoriaRelatorio.timestamp_criacao.desc()) \
                    .limit(limite).all()

    @staticmethod
    def registrar_geracao(usuario_id: str,
                          tipo_relatorio: TipoRelatorio,
                          data_inicio: Optional[datetime.date],
                          data_fim: Optional[datetime.date],
                          filtros: Optional[Dict[str, Any]],
                          resultado_json: Dict[str, Any],
                          formato_export: FormatoExport = FormatoExport.VISUALIZACAO,
                          chave_api_auditoria: Optional[str] = None
                          ) -> AuditoriaRelatorio:
        relatorio = AuditoriaRelatorio(
            usuario_id=usuario_id,
            tipo_relatorio=tipo_relatorio,
            data_inicio=data_inicio,
            data_fim=data_fim,
            filtros=filtros or {},
            resultado_json=resultado_json,
            formato_export=formato_export,
            chave_api_auditoria=chave_api_auditoria,
        )
        db.session.add(relatorio)
        db.session.commit()
        return relatorio

    @staticmethod
    def marcar_download(relatorio_id: str) -> None:
        relatorio = AuditoriaRelatorio.query.get(relatorio_id)
        if not relatorio:
            raise ValueError("Relatório não encontrado")

        if not relatorio.timestamp_download:
            relatorio.timestamp_download = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def buscar_por_id(relatorio_id: str,
                      usuario_id: Optional[str] = None
                      ) -> Optional[AuditoriaRelatorio]:
        query = AuditoriaRelatorio.query.filter_by(id=relatorio_id)
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        return query.first()
