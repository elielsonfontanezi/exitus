# -*- coding: utf-8 -*-
"""
Exitus - AlertaService (M7.2) - VERSÃO FINAL CORRIGIDA
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import and_

from app.database import db
from app.models.configuracao_alerta import ConfiguracaoAlerta
from app.models.ativo import Ativo
from app.models.posicao import Posicao
from app.models.provento import Provento

class AlertaService:
    @staticmethod
    def listar_alertas(usuario_id: UUID, ativo_id: Optional[UUID] = None, apenas_ativos: bool = True) -> List[Dict]:
        query = ConfiguracaoAlerta.query.filter(ConfiguracaoAlerta.usuario_id == usuario_id)
        
        if ativo_id:
            query = query.filter(ConfiguracaoAlerta.ativo_id == ativo_id)
        
        if apenas_ativos:
            query = query.filter(ConfiguracaoAlerta.ativo)
        
        alertas = query.order_by(ConfiguracaoAlerta.timestamp_criacao.desc()).all()
        return [a.to_dict() for a in alertas]

    @staticmethod
    def obter_alerta(usuario_id: UUID, alerta_id: UUID) -> Dict:
        alerta = ConfiguracaoAlerta.query.filter(
            and_(
                ConfiguracaoAlerta.id == alerta_id,
                ConfiguracaoAlerta.usuario_id == usuario_id
            )
        ).first()
        if not alerta:
            raise ValueError("Alerta não encontrado")
        return alerta.to_dict()

    @staticmethod
    def criar_alerta(usuario_id: UUID, dados: Dict) -> Dict:
        if not dados.get('nome'):
            raise ValueError("Nome obrigatório")
        if not dados.get('tipo_alerta'):
            raise ValueError("Tipo obrigatório")
        if 'condicao_valor' not in dados:
            raise ValueError("Valor obrigatório")
        
        operador = dados.get('condicao_operador', 'MAIOR')
        if operador == 'ENTRE' and not dados.get('condicao_valor2'):
            raise ValueError("ENTRE requer valor2")
        
        alerta = ConfiguracaoAlerta(
            usuario_id=usuario_id,
            nome=dados['nome'],
            tipo_alerta=dados['tipo_alerta'],
            condicao_valor=Decimal(str(dados['condicao_valor'])),
            condicao_operador=operador,
            condicao_valor2=Decimal(str(dados['condicao_valor2'])) if dados.get('condicao_valor2') else None,
            ativo_id=dados.get('ativo_id'),
            portfolio_id=dados.get('portfolio_id'),
            frequencia_notificacao=dados.get('frequencia_notificacao', 'IMEDIATA'),
            canais_entrega=dados.get('canais_entrega', ['email', 'webapp']),
            ativo=True
        )
        db.session.add(alerta)
        db.session.commit()
        db.session.refresh(alerta)
        return alerta.to_dict()

    @staticmethod
    def atualizar_alerta(usuario_id: UUID, alerta_id: UUID, dados: Dict) -> Dict:
        alerta = ConfiguracaoAlerta.query.filter(
            and_(
                ConfiguracaoAlerta.id == alerta_id,
                ConfiguracaoAlerta.usuario_id == usuario_id
            )
        ).first()
        if not alerta:
            raise ValueError("Alerta não encontrado")
        
        for campo, valor in dados.items():
            if campo in ['nome', 'tipo_alerta', 'frequencia_notificacao']:
                setattr(alerta, campo, valor)
            elif campo == 'ativo':
                setattr(alerta, campo, bool(valor))
            elif campo in ['condicao_valor', 'condicao_valor2']:
                setattr(alerta, campo, Decimal(str(valor)) if valor else None)
        
        db.session.commit()
        db.session.refresh(alerta)
        return alerta.to_dict()

    @staticmethod
    def deletar_alerta(usuario_id: UUID, alerta_id: UUID) -> bool:
        alerta = ConfiguracaoAlerta.query.filter(
            and_(
                ConfiguracaoAlerta.id == alerta_id,
                ConfiguracaoAlerta.usuario_id == usuario_id
            )
        ).first()
        if not alerta:
            raise ValueError("Alerta não encontrado")
        db.session.delete(alerta)
        db.session.commit()
        return True

    @staticmethod
    def testar_alerta(usuario_id: UUID, alerta_id: UUID) -> Dict:
        alerta = ConfiguracaoAlerta.query.filter(
            and_(
                ConfiguracaoAlerta.id == alerta_id,
                ConfiguracaoAlerta.usuario_id == usuario_id
            )
        ).first()
        if not alerta:
            raise ValueError("Alerta não encontrado")
        
        valor_atual = AlertaService._obter_valor_atual(alerta)
        if valor_atual is None:
            return {'alerta_id': str(alerta_id), 'status': 'erro', 'mensagem': 'Valor atual indisponível'}
        
        condicao_atingida = AlertaService.validar_condicao(alerta, valor_atual)
        return {
            'alerta_id': str(alerta.id),
            'nome': alerta.nome,
            'tipo': alerta.tipo_alerta,
            'valor_atual': float(valor_atual),
            'threshold': float(alerta.condicao_valor),
            'condicao_atingida': condicao_atingida
        }

    @staticmethod
    def obter_historico_acionamentos(usuario_id: UUID, limite: int = 20) -> List[Dict]:
        alertas = ConfiguracaoAlerta.query.filter(
            and_(
                ConfiguracaoAlerta.usuario_id == usuario_id,
                ConfiguracaoAlerta.timestamp_ultimo_acionamento.isnot(None)
            )
        ).order_by(ConfiguracaoAlerta.timestamp_ultimo_acionamento.desc()).limit(limite).all()
        return [{'id': str(a.id), 'nome': a.nome} for a in alertas]

    @staticmethod
    def validar_condicao(alerta, valor_atual: Decimal) -> bool:
        op = alerta.condicao_operador
        threshold = alerta.condicao_valor
        if op == 'MAIOR': return valor_atual > threshold
        if op == 'MENOR': return valor_atual < threshold
        if op == 'ENTRE' and alerta.condicao_valor2: 
            return threshold <= valor_atual <= alerta.condicao_valor2
        return False

    @staticmethod
    def _obter_valor_atual(alerta) -> Optional[Decimal]:
        if alerta.tipo_alerta in ['QUEDA_PRECO', 'ALTA_PRECO'] and alerta.ativo_id:
            ativo = Ativo.query.get(alerta.ativo_id)
            return ativo.preco_atual if ativo else None
        return Decimal('0')
