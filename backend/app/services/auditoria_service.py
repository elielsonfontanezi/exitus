# -*- coding: utf-8 -*-
"""
Exitus - Auditoria Service
Serviço utilitário para registro de logs de auditoria
GAP: EXITUS-AUDITLOG-001
"""

from datetime import datetime
from flask import request, has_request_context
from app.database import db
from app.models.log_auditoria import LogAuditoria
import logging

logger = logging.getLogger(__name__)


class AuditoriaService:
    """
    Serviço para registro centralizado de logs de auditoria.
    
    Princípios:
    - Nunca levanta exceção (falha de log não pode quebrar operação)
    - Captura ip_address e user_agent automaticamente do request
    - Suporta dados_antes/dados_depois para UPDATE
    """
    
    @staticmethod
    def registrar(
        usuario_id,
        acao,
        entidade=None,
        entidade_id=None,
        dados_antes=None,
        dados_depois=None,
        sucesso=True,
        mensagem=None
    ):
        """
        Registra log de auditoria.
        
        Args:
            usuario_id (UUID): ID do usuário que realizou a ação
            acao (str): Tipo de ação (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, EXPORT, etc.)
            entidade (str): Nome da entidade afetada (Transacao, Provento, Ativo, etc.)
            entidade_id (UUID): ID do registro afetado
            dados_antes (dict): Estado anterior do registro (para UPDATE/DELETE)
            dados_depois (dict): Estado posterior do registro (para CREATE/UPDATE)
            sucesso (bool): Se ação foi bem-sucedida
            mensagem (str): Mensagem de erro ou detalhes adicionais
        
        Returns:
            LogAuditoria: Objeto criado ou None se falhou
        """
        try:
            # Capturar contexto HTTP se disponível
            ip_address = None
            user_agent = None
            
            if has_request_context():
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')[:500]  # Limitar tamanho
            
            # Criar log
            log = LogAuditoria(
                usuario_id=usuario_id,
                acao=acao.upper(),
                entidade=entidade,
                entidade_id=entidade_id,
                dados_antes=dados_antes,
                dados_depois=dados_depois,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                sucesso=sucesso,
                mensagem=mensagem
            )
            
            db.session.add(log)
            db.session.commit()
            
            logger.debug(
                f"Auditoria registrada: {acao} {entidade or ''} "
                f"por usuario_id={usuario_id} sucesso={sucesso}"
            )
            
            return log
            
        except Exception as e:
            # Falha de log não pode quebrar operação principal
            logger.error(f"Erro ao registrar auditoria: {e}", exc_info=True)
            try:
                db.session.rollback()
            except:
                pass
            return None
    
    @staticmethod
    def registrar_login(usuario_id, sucesso=True, mensagem=None):
        """Atalho para registrar LOGIN"""
        return AuditoriaService.registrar(
            usuario_id=usuario_id,
            acao='LOGIN',
            sucesso=sucesso,
            mensagem=mensagem
        )
    
    @staticmethod
    def registrar_logout(usuario_id):
        """Atalho para registrar LOGOUT"""
        return AuditoriaService.registrar(
            usuario_id=usuario_id,
            acao='LOGOUT',
            sucesso=True
        )
    
    @staticmethod
    def registrar_create(usuario_id, entidade, entidade_id, dados_depois):
        """Atalho para registrar CREATE"""
        return AuditoriaService.registrar(
            usuario_id=usuario_id,
            acao='CREATE',
            entidade=entidade,
            entidade_id=entidade_id,
            dados_depois=dados_depois,
            sucesso=True
        )
    
    @staticmethod
    def registrar_update(usuario_id, entidade, entidade_id, dados_antes, dados_depois):
        """Atalho para registrar UPDATE"""
        return AuditoriaService.registrar(
            usuario_id=usuario_id,
            acao='UPDATE',
            entidade=entidade,
            entidade_id=entidade_id,
            dados_antes=dados_antes,
            dados_depois=dados_depois,
            sucesso=True
        )
    
    @staticmethod
    def registrar_delete(usuario_id, entidade, entidade_id, dados_antes):
        """Atalho para registrar DELETE"""
        return AuditoriaService.registrar(
            usuario_id=usuario_id,
            acao='DELETE',
            entidade=entidade,
            entidade_id=entidade_id,
            dados_antes=dados_antes,
            sucesso=True
        )
    
    @staticmethod
    def registrar_export(usuario_id, entidade, mensagem=None):
        """Atalho para registrar EXPORT"""
        return AuditoriaService.registrar(
            usuario_id=usuario_id,
            acao='EXPORT',
            entidade=entidade,
            sucesso=True,
            mensagem=mensagem
        )
