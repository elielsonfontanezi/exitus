# -*- coding: utf-8 -*-
"""
Exitus - Model LogAuditoria
Entidade para logs de auditoria e compliance
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class LogAuditoria(db.Model):
    """
    Model para logs de auditoria
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário que realizou a ação
        acao (str): Tipo de ação (LOGIN, CREATE, UPDATE, DELETE, etc.)
        entidade (str): Nome da entidade afetada
        entidade_id (UUID): ID do registro afetado
        dados_antes (dict): Estado anterior do registro (JSON)
        dados_depois (dict): Estado posterior do registro (JSON)
        ip_address (str): Endereço IP de origem
        user_agent (str): Navegador/cliente usado
        timestamp (datetime): Data/hora da ação
        sucesso (bool): Se ação foi bem-sucedida
        mensagem (str): Mensagem de erro ou detalhes adicionais
    
    Relationships:
        usuario: Usuário que realizou a ação
    """
    
    __tablename__ = 'log_auditoria'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do log"
    )
    
    # Foreign key
    usuario_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="ID do usuário (NULL para ações anônimas)"
    )
    
    # Dados da ação
    acao = db.Column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de ação (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW, EXPORT, etc.)"
    )
    
    entidade = db.Column(
        String(100),
        nullable=True,
        index=True,
        comment="Nome da entidade afetada (Usuario, Transacao, Posicao, etc.)"
    )
    
    entidade_id = db.Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID do registro afetado"
    )
    
    # Estados anterior e posterior (para UPDATE)
    dados_antes = db.Column(
        JSON,
        nullable=True,
        comment="Estado anterior do registro (JSON)"
    )
    
    dados_depois = db.Column(
        JSON,
        nullable=True,
        comment="Estado posterior do registro (JSON)"
    )
    
    # Dados de contexto
    ip_address = db.Column(
        String(45),  # IPv6 pode ter até 45 caracteres
        nullable=True,
        index=True,
        comment="Endereço IP de origem"
    )
    
    user_agent = db.Column(
        String(500),
        nullable=True,
        comment="User-Agent (navegador/cliente)"
    )
    
    timestamp = db.Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Data/hora da ação"
    )
    
    # Resultado
    sucesso = db.Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica se ação foi bem-sucedida"
    )
    
    mensagem = db.Column(
        Text,
        nullable=True,
        comment="Mensagem de erro ou detalhes adicionais"
    )
    
    # Relacionamentos
    usuario = relationship('Usuario', backref='logs_auditoria', lazy='joined')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "length(acao) >= 3",
            name="log_acao_min_length"
        ),
        {'comment': 'Tabela de logs de auditoria para compliance'}
    )
    
    def is_sucesso(self):
        """Verifica se ação foi bem-sucedida"""
        return self.sucesso
    
    def is_falha(self):
        """Verifica se ação falhou"""
        return not self.sucesso
    
    def is_login(self):
        """Verifica se é log de login"""
        return self.acao == 'LOGIN'
    
    def is_logout(self):
        """Verifica se é log de logout"""
        return self.acao == 'LOGOUT'
    
    def is_create(self):
        """Verifica se é criação de registro"""
        return self.acao == 'CREATE'
    
    def is_update(self):
        """Verifica se é atualização de registro"""
        return self.acao == 'UPDATE'
    
    def is_delete(self):
        """Verifica se é exclusão de registro"""
        return self.acao == 'DELETE'
    
    def is_export(self):
        """Verifica se é exportação de dados"""
        return self.acao == 'EXPORT'
    
    def get_alteracoes(self):
        """
        Extrai as alterações realizadas (campos modificados)
        
        Returns:
            dict: Dicionário com campos alterados e seus valores antes/depois
        """
        if not self.is_update() or not self.dados_antes or not self.dados_depois:
            return {}
        
        alteracoes = {}
        for campo, valor_depois in self.dados_depois.items():
            valor_antes = self.dados_antes.get(campo)
            if valor_antes != valor_depois:
                alteracoes[campo] = {
                    'antes': valor_antes,
                    'depois': valor_depois
                }
        
        return alteracoes
    
    def to_dict(self, include_dados=False):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Args:
            include_dados (bool): Se deve incluir dados_antes e dados_depois
        
        Returns:
            dict: Dicionário com dados do log
        """
        data = {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id) if self.usuario_id else None,
            'acao': self.acao,
            'entidade': self.entidade,
            'entidade_id': str(self.entidade_id) if self.entidade_id else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sucesso': self.sucesso,
            'mensagem': self.mensagem
        }
        
        if include_dados:
            data['dados_antes'] = self.dados_antes
            data['dados_depois'] = self.dados_depois
            data['alteracoes'] = self.get_alteracoes()
        
        return data
    
    def __repr__(self):
        """Representação string do objeto"""
        status = "✓" if self.sucesso else "✗"
        usuario = self.usuario.username if self.usuario else "ANON"
        return f"<LogAuditoria {status} {usuario} {self.acao} {self.entidade or ''}>"
