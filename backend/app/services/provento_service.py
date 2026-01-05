# -*- coding: utf-8 -*-
"""
Exitus - Provento Service V3 (FIX M3 FINAL)
"""

import logging
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import joinedload
from sqlalchemy import extract

from app.database import db
from app.models import Provento, Ativo, Posicao
from app.services.posicao_service import PosicaoService

logger = logging.getLogger(__name__)


class ProventoService:
    
    @staticmethod
    def get_all(usuario_id: UUID, page=1, per_page=50, filters=None):
        """
        Lista proventos do USUÁRIO via posições (FIX M3 FINAL).
        
        Args:
            usuario_id: UUID do usuário
            page: Página atual
            per_page: Itens por página
            filters: Dict com ativo_id, tipo_provento, ano
        
        Returns:
            Pagination: Objeto de paginação SQLAlchemy
        """
        try:
            # 1. Buscar posições do usuário para obter ativos
            posicoes_paginadas = PosicaoService.get_all(usuario_id, page=1, per_page=1000)
            ativos_ids = [p.ativo_id for p in posicoes_paginadas.items]
            
            if not ativos_ids:
                # Retorna paginação vazia
                return db.session.query(Provento).filter(Provento.id == None).paginate(
                    page=page, per_page=per_page, error_out=False
                )
            
            # 2. Query proventos dos ativos do usuário
            query = Provento.query.filter(Provento.ativo_id.in_(ativos_ids))
            
            # 3. Aplicar filtros
            if filters:
                if filters.get('ativo_id'):
                    query = query.filter_by(ativo_id=filters['ativo_id'])
                
                if filters.get('tipo_provento'):
                    query = query.filter_by(tipo_provento=filters['tipo_provento'])
                
                # ✅ NOVO: Filtro por ANO
                if filters.get('ano'):
                    query = query.filter(
                        extract('year', Provento.data_pagamento) == filters['ano']
                    )
            
            # 4. Eager loading e ordenação
            query = query.options(joinedload(Provento.ativo)).order_by(Provento.data_com.desc())
            
            # 5. Paginar
            return query.paginate(page=page, per_page=per_page, error_out=False)
        
        except Exception as e:
            logger.error(f"Erro proventos usuario {usuario_id}: {e}")
            raise
    
    @staticmethod
    def get_by_id(provento_id):
        """Busca provento por ID"""
        return Provento.query.options(joinedload(Provento.ativo)).get(provento_id)
    
    
    @staticmethod
    def create(data):
        """Cria novo provento"""
        try:
            # Validar ativo
            ativo = Ativo.query.get(data['ativo_id'])
            if not ativo:
                raise ValueError("Ativo não encontrado")
            
            # ✅ GARANTIR que tipo_provento está em UPPERCASE
            if 'tipo_provento' in data:
                data['tipo_provento'] = data['tipo_provento'].upper()
            
            # Converter string para Enum
            from app.models import TipoProvento
            tipo_enum = TipoProvento[data['tipo_provento']]
            
            provento = Provento(
                ativo_id=data['ativo_id'],
                tipo_provento=tipo_enum,  # ✅ Usar enum, não string
                valor_por_acao=data['valor_por_acao'],
                quantidade_ativos=data['quantidade_ativos'],
                valor_bruto=data['valor_bruto'],
                imposto_retido=data.get('imposto_retido', 0),
                valor_liquido=data['valor_liquido'],
                data_com=data['data_com'],
                data_pagamento=data['data_pagamento'],
                observacoes=data.get('observacoes')
            )
            
            db.session.add(provento)
            db.session.commit()
            db.session.refresh(provento)
            
            # ✅ EAGER LOAD ativo para retornar completo
            provento = Provento.query.options(
                joinedload(Provento.ativo)
            ).get(provento.id)
            
            return provento
            
        except KeyError as e:
            raise ValueError(f"Tipo de provento inválido: {data.get('tipo_provento')}")
        except Exception as e:
            db.session.rollback()
            raise
   
    
    @staticmethod
    def update(provento_id, data):
        """Atualiza provento"""
        try:
            provento = Provento.query.get(provento_id)
            if not provento:
                raise ValueError("Provento não encontrado")
            
            campos_permitidos = [
                'tipo_provento', 'valor_por_acao', 'quantidade_ativos',
                'valor_bruto', 'imposto_retido', 'valor_liquido',
                'data_com', 'data_pagamento', 'observacoes'
            ]
            
            for campo in campos_permitidos:
                if campo in data:
                    setattr(provento, campo, data[campo])
            
            db.session.commit()
            return provento
        except Exception as e:
            db.session.rollback()
            raise
    
    
    @staticmethod
    def delete(provento_id):
        """Deleta provento"""
        try:
            provento = Provento.query.get(provento_id)
            if not provento:
                raise ValueError("Provento não encontrado")
            
            db.session.delete(provento)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise
    
    
    @staticmethod
    def get_por_ativo(usuario_id, ativo_id):
        """Consolida posições de um ativo em todas as corretoras"""
        try:
            posicoes = Posicao.query.filter_by(
                usuario_id=usuario_id,
                ativo_id=ativo_id
            ).options(
                joinedload(Posicao.ativo),
                joinedload(Posicao.corretora)
            ).all()
            
            if not posicoes:
                return None
            
            quantidade_total = sum(p.quantidade for p in posicoes)
            custo_total = sum(p.custo_total for p in posicoes)
            valor_atual_total = sum(p.valor_atual or Decimal(0) for p in posicoes)
            preco_medio = custo_total / quantidade_total if quantidade_total > 0 else Decimal(0)
            
            return {
                'ativo': posicoes[0].ativo.to_dict(),
                'quantidade_total': float(quantidade_total),
                'preco_medio': float(preco_medio),
                'custo_total': float(custo_total),
                'valor_atual': float(valor_atual_total),
                'lucro_prejuizo': float(valor_atual_total - custo_total),
                'corretoras': [
                    {
                        'corretora': p.corretora.nome,
                        'quantidade': float(p.quantidade),
                        'custo_total': float(p.custo_total)
                    } for p in posicoes
                ]
            }
        except Exception as e:
            logger.error(f"Erro ao consolidar posição: {e}")
            raise
    
    
    @staticmethod
    def get_recebidos_usuario(usuario_id, data_inicio=None, data_fim=None):
        """Retorna proventos recebidos do usuário"""
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(joinedload(Posicao.ativo)).all()
        
        if not posicoes:
            return []
        
        ativos_ids = [p.ativo_id for p in posicoes]
        
        query = Provento.query.filter(Provento.ativo_id.in_(ativos_ids))
        
        if data_inicio:
            query = query.filter(Provento.data_pagamento >= data_inicio)
        
        if data_fim:
            query = query.filter(Provento.data_pagamento <= data_fim)
        
        query = query.options(joinedload(Provento.ativo)).order_by(Provento.data_pagamento.desc())
        
        proventos = query.all()
        proventos_recebidos = []
        
        for prov in proventos:
            posicao = next((p for p in posicoes if p.ativo_id == prov.ativo_id), None)
            
            if posicao:
                quantidade_recebida = posicao.quantidade
                valor_bruto_recebido = prov.valor_por_acao * quantidade_recebida
                valor_liquido_recebido = valor_bruto_recebido * (prov.valor_liquido / prov.valor_bruto) if prov.valor_bruto > 0 else Decimal(0)
                
                proventos_recebidos.append({
                    'provento_id': str(prov.id),
                    'ativo': {
                        'ticker': prov.ativo.ticker,
                        'nome': prov.ativo.nome
                    },
                    'tipo_provento': prov.tipo_provento.value,
                    'data_com': prov.data_com.isoformat(),
                    'data_pagamento': prov.data_pagamento.isoformat(),
                    'valor_por_acao': float(prov.valor_por_acao),
                    'quantidade_recebida': float(quantidade_recebida),
                    'valor_bruto_recebido': float(valor_bruto_recebido),
                    'valor_liquido_recebido': float(valor_liquido_recebido)
                })
        
        return proventos_recebidos
    
    
    @staticmethod
    def calcular_total_recebido(usuario_id, ativo_id=None):
        """Calcula total recebido de proventos"""
        proventos = ProventoService.get_recebidos_usuario(usuario_id)
        
        if ativo_id:
            proventos = [p for p in proventos if p.get('ativo', {}).get('id') == str(ativo_id)]
        
        total_por_tipo = {}
        total_geral_bruto = Decimal(0)
        total_geral_liquido = Decimal(0)
        
        for p in proventos:
            tipo = p['tipo_provento']
            valor_bruto = Decimal(str(p['valor_bruto_recebido']))
            valor_liquido = Decimal(str(p['valor_liquido_recebido']))
            
            if tipo not in total_por_tipo:
                total_por_tipo[tipo] = {
                    'quantidade': 0,
                    'valor_bruto': Decimal(0),
                    'valor_liquido': Decimal(0)
                }
            
            total_por_tipo[tipo]['quantidade'] += 1
            total_por_tipo[tipo]['valor_bruto'] += valor_bruto
            total_por_tipo[tipo]['valor_liquido'] += valor_liquido
            
            total_geral_bruto += valor_bruto
            total_geral_liquido += valor_liquido
        
        return {
            'total_geral_bruto': float(total_geral_bruto),
            'total_geral_liquido': float(total_geral_liquido),
            'por_tipo': {
                tipo: {
                    'quantidade': dados['quantidade'],
                    'valor_bruto': float(dados['valor_bruto']),
                    'valor_liquido': float(dados['valor_liquido'])
                } for tipo, dados in total_por_tipo.items()
            }
        }

    @staticmethod
    def get_by_id(provento_id):
        """Busca provento por ID"""
        # ✅ ADICIONAR: joinedload para carregar ativo
        return Provento.query.options(
            joinedload(Provento.ativo)
        ).get(provento_id)
