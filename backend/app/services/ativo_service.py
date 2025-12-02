# -*- coding: utf-8 -*-
"""Exitus - Ativo Service - Lógica de negócio"""

from decimal import Decimal
from datetime import date
from sqlalchemy import or_
from app.database import db
from app.models import Ativo, TipoAtivo, ClasseAtivo

class AtivoService:
    """Serviço para operações de ativos"""
    
    @staticmethod
    def get_all(page=1, per_page=20, ativo=None, tipo=None, classe=None, mercado=None, 
                deslistado=None, search=None):
        """
        Lista ativos com paginação e filtros.
        
        Args:
            page: Número da página
            per_page: Itens por página
            ativo: Filtro por status ativo
            tipo: Filtro por tipo (ACAO, FII, etc)
            classe: Filtro por classe (RENDA_VARIAVEL, etc)
            mercado: Filtro por mercado (BR, US, etc)
            deslistado: Filtro por deslistados
            search: Busca em ticker e nome
        """
        query = Ativo.query
        
        # Filtros
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        if tipo:
            query = query.filter_by(tipo=TipoAtivo[tipo.upper()])
        
        if classe:
            query = query.filter_by(classe=ClasseAtivo[classe.upper()])
        
        if mercado:
            query = query.filter_by(mercado=mercado.upper())
        
        if deslistado is not None:
            query = query.filter_by(deslistado=deslistado)
        
        if search:
            query = query.filter(
                or_(
                    Ativo.ticker.ilike(f'%{search}%'),
                    Ativo.nome.ilike(f'%{search}%')
                )
            )
        
        # Ordenar por ticker
        query = query.order_by(Ativo.ticker)
        
        # Paginação
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(ativo_id):
        """Busca ativo por ID"""
        return Ativo.query.get(ativo_id)
    
    @staticmethod
    def get_by_ticker(ticker, mercado):
        """Busca ativo por ticker e mercado"""
        return Ativo.query.filter_by(
            ticker=ticker.upper(),
            mercado=mercado.upper()
        ).first()
    
    @staticmethod
    def create(data):
        """
        Cria novo ativo.
        
        Args:
            data: Dict com ticker, nome, tipo, classe, mercado, moeda, etc
        """
        # Verifica se já existe ativo com mesmo ticker e mercado
        existing = Ativo.query.filter_by(
            ticker=data['ticker'].upper(),
            mercado=data['mercado'].upper()
        ).first()
        
        if existing:
            raise ValueError(f"Ativo {data['ticker']} já existe no mercado {data['mercado']}")
        
        # ⚠️ CORREÇÃO: Usar p_l, p_vp (nomes das colunas no DB)
        ativo = Ativo(
            ticker=data['ticker'].upper(),
            nome=data['nome'],
            tipo=TipoAtivo[data['tipo'].upper()],
            classe=ClasseAtivo[data['classe'].upper()],
            mercado=data['mercado'].upper(),
            moeda=data['moeda'].upper(),
            preco_atual=Decimal(str(data['preco_atual'])) if data.get('preco_atual') else None,
            dividend_yield=Decimal(str(data['dividend_yield'])) if data.get('dividend_yield') else None,
            p_l=Decimal(str(data['pl'])) if data.get('pl') else None,  # ⬅️ CORRIGIDO
            p_vp=Decimal(str(data['pvp'])) if data.get('pvp') else None,  # ⬅️ CORRIGIDO
            roe=Decimal(str(data['roe'])) if data.get('roe') else None,
            ativo=data.get('ativo', True),
            deslistado=data.get('deslistado', False)
        )
        
        db.session.add(ativo)
        db.session.commit()
        return ativo
    
    @staticmethod
    def update(ativo_id, data):
        """
        Atualiza ativo.
        
        Args:
            ativo_id: ID do ativo
            data: Dict com campos a atualizar
        """
        ativo = Ativo.query.get(ativo_id)
        if not ativo:
            raise ValueError("Ativo não encontrado")
        
        # Atualizar campos permitidos
        if 'nome' in data:
            ativo.nome = data['nome']
        
        if 'tipo' in data:
            ativo.tipo = TipoAtivo[data['tipo'].upper()]
        
        if 'classe' in data:
            ativo.classe = ClasseAtivo[data['classe'].upper()]
        
        if 'mercado' in data:
            ativo.mercado = data['mercado'].upper()
        
        if 'moeda' in data:
            ativo.moeda = data['moeda'].upper()
        
        if 'preco_atual' in data:
            ativo.preco_atual = Decimal(str(data['preco_atual'])) if data['preco_atual'] else None
        
        if 'dividend_yield' in data:
            ativo.dividend_yield = Decimal(str(data['dividend_yield'])) if data['dividend_yield'] else None
        
        # ⚠️ CORREÇÃO: Usar p_l, p_vp
        if 'pl' in data:
            ativo.p_l = Decimal(str(data['pl'])) if data['pl'] else None  # ⬅️ CORRIGIDO
        
        if 'pvp' in data:
            ativo.p_vp = Decimal(str(data['pvp'])) if data['pvp'] else None  # ⬅️ CORRIGIDO
        
        if 'roe' in data:
            ativo.roe = Decimal(str(data['roe'])) if data['roe'] else None
        
        if 'ativo' in data:
            ativo.ativo = data['ativo']
        
        if 'deslistado' in data:
            ativo.deslistado = data['deslistado']
            if data['deslistado'] and 'data_deslistagem' in data:
                ativo.data_deslistagem = data['data_deslistagem']
        
        db.session.commit()
        return ativo
    
    @staticmethod
    def delete(ativo_id):
        """Deleta ativo"""
        ativo = Ativo.query.get(ativo_id)
        if not ativo:
            raise ValueError("Ativo não encontrado")
        
        # TODO: Verificar se há posições/transações vinculadas
        # Por enquanto, permite deletar
        
        db.session.delete(ativo)
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_mercado(mercado, page=1, per_page=50):
        """Lista ativos de um mercado específico"""
        return Ativo.query.filter_by(
            mercado=mercado.upper(),
            ativo=True,
            deslistado=False
        ).order_by(Ativo.ticker).paginate(page=page, per_page=per_page, error_out=False)
