# -*- coding: utf-8 -*-
"""Exitus - Corretora Service - Lógica de negócio"""

from decimal import Decimal
from sqlalchemy import or_
from app.database import db
from app.models import Corretora, TipoCorretora

class CorretoraService:
    """Serviço para operações de corretoras"""
    
    @staticmethod
    def get_all(usuario_id, page=1, per_page=20, ativa=None, tipo=None, pais=None, search=None):
        """
        Lista corretoras do usuário com paginação e filtros.
        
        Args:
            usuario_id: ID do usuário proprietário
            page: Número da página
            per_page: Itens por página
            ativa: Filtro por status ativo
            tipo: Filtro por tipo (CORRETORA, EXCHANGE)
            pais: Filtro por país (BR, US, etc)
            search: Busca em nome
        """
        query = Corretora.query.filter_by(usuario_id=usuario_id)
        
        # Filtros
        if ativa is not None:
            query = query.filter_by(ativa=ativa)
        
        if tipo:
            query = query.filter_by(tipo=TipoCorretora[tipo.upper()])
        
        if pais:
            query = query.filter_by(pais=pais.upper())
        
        if search:
            query = query.filter(Corretora.nome.ilike(f'%{search}%'))
        
        # Ordenar por nome
        query = query.order_by(Corretora.nome)
        
        # Paginação
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(corretora_id, usuario_id):
        """Busca corretora por ID (valida propriedade)"""
        return Corretora.query.filter_by(id=corretora_id, usuario_id=usuario_id).first()
    
    @staticmethod
    def create(data, usuario_id):
        """
        Cria nova corretora.
        
        Args:
            data: Dict com nome, tipo, pais, moeda_padrao, etc
            usuario_id: ID do usuário proprietário
        """
        # Verifica se já existe corretora com mesmo nome, país e usuário
        existing = Corretora.query.filter_by(
            usuario_id=usuario_id,
            nome=data['nome'],
            pais=data['pais'].upper()
        ).first()
        
        if existing:
            raise ValueError(f"Já existe uma corretora '{data['nome']}' em {data['pais']}")
        
        corretora = Corretora(
            usuario_id=usuario_id,
            nome=data['nome'],
            tipo=TipoCorretora[data['tipo'].upper()],
            pais=data['pais'].upper(),
            moeda_padrao=data['moeda_padrao'].upper(),
            saldo_atual=Decimal(data.get('saldo_atual', '0.00')),
            ativa=data.get('ativa', True),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(corretora)
        db.session.commit()
        return corretora
    
    @staticmethod
    def update(corretora_id, data, usuario_id):
        """
        Atualiza corretora.
        
        Args:
            corretora_id: ID da corretora
            data: Dict com campos a atualizar
            usuario_id: ID do usuário proprietário
        """
        corretora = Corretora.query.filter_by(id=corretora_id, usuario_id=usuario_id).first()
        if not corretora:
            raise ValueError("Corretora não encontrada")
        
        # Atualizar campos permitidos
        if 'nome' in data:
            # Verifica duplicidade
            existing = Corretora.query.filter_by(
                usuario_id=usuario_id,
                nome=data['nome'],
                pais=corretora.pais
            ).first()
            if existing and existing.id != corretora.id:
                raise ValueError(f"Já existe uma corretora '{data['nome']}' em {corretora.pais}")
            corretora.nome = data['nome']
        
        if 'tipo' in data:
            corretora.tipo = TipoCorretora[data['tipo'].upper()]
        
        if 'pais' in data:
            corretora.pais = data['pais'].upper()
        
        if 'moeda_padrao' in data:
            corretora.moeda_padrao = data['moeda_padrao'].upper()
        
        if 'saldo_atual' in data:
            corretora.saldo_atual = Decimal(str(data['saldo_atual']))
        
        if 'ativa' in data:
            corretora.ativa = data['ativa']
        
        if 'observacoes' in data:
            corretora.observacoes = data['observacoes']
        
        db.session.commit()
        return corretora
    
    @staticmethod
    def delete(corretora_id, usuario_id):
        """Deleta corretora (valida propriedade)"""
        corretora = Corretora.query.filter_by(id=corretora_id, usuario_id=usuario_id).first()
        if not corretora:
            raise ValueError("Corretora não encontrada")
        
        # TODO: Verificar se há posições/transações vinculadas
        # Por enquanto, permite deletar
        
        db.session.delete(corretora)
        db.session.commit()
        return True
    
    @staticmethod
    def get_saldo_total(usuario_id, moeda='BRL'):
        """Calcula saldo total do usuário em determinada moeda"""
        corretoras = Corretora.query.filter_by(
            usuario_id=usuario_id,
            moeda_padrao=moeda.upper(),
            ativa=True
        ).all()
        
        total = sum(c.saldo_atual for c in corretoras)
        return total
