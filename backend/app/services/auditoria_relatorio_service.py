# -*- coding: utf-8 -*-
"""
Exitus - AuditoriaRelatorioService
Service para auditoria de relatórios gerados
"""
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.database import db
from app.models import Usuario, AuditoriaRelatorio
from app.models.enums_m7 import TipoRelatorio, FormatoExport

class AuditoriaRelatorioService:
    """Service para auditoria de relatórios"""
    
    @staticmethod
    def registrar_relatorio(
        usuario_id: str,
        tipo_relatorio: TipoRelatorio,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        filtros: Optional[Dict] = None,
        resultado_json: Optional[Dict] = None,
        formato_export: FormatoExport = FormatoExport.VISUALIZACAO
    ) -> AuditoriaRelatorio:
        """Registra um relatório gerado no histórico de auditoria"""
        auditoria = AuditoriaRelatorio(
            usuario_id=usuario_id,
            tipo_relatorio=tipo_relatorio,
            data_inicio=data_inicio,
            data_fim=data_fim,
            filtros=filtros,
            resultado_json=resultado_json,
            formato_export=formato_export
        )
        db.session.add(auditoria)
        db.session.commit()
        return auditoria
    
    @staticmethod
    def marcar_download(relatorio_id: str) -> bool:
        """Marca relatório como baixado"""
        relatorio = db.session.query(AuditoriaRelatorio).filter_by(id=relatorio_id).first()
        if relatorio:
            relatorio.timestamp_download = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def listar_por_usuario(usuario_id: str, limit: int = 50) -> List[Dict]:
        """Lista relatórios de um usuário"""
        relatorios = (db.session.query(AuditoriaRelatorio)
                     .filter_by(usuario_id=usuario_id)
                     .order_by(AuditoriaRelatorio.timestamp_criacao.desc())
                     .limit(limit)
                     .all())
        return [r.to_dict() for r in relatorios]
