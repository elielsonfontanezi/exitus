# -*- coding: utf-8 -*-
"""
Exitus - Provento Service
Service layer para gerenciamento de proventos
"""

from app.database import db
from app.models import Provento, Ativo, Posicao
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class ProventoService:
    """Service para operações de proventos"""

    @staticmethod
    def get_all(page=1, per_page=50, filters=None):
        """
        Lista proventos com filtros opcionais
        
        Args:
            page (int): Página atual
            per_page (int): Registros por página
            filters (dict): Filtros opcionais
        
        Returns:
            Pagination: Objeto de paginação
        """
        try:
            query = Provento.query.options(joinedload(Provento.ativo))
            
            if filters:
                if filters.get('ativo_id'):
                    query = query.filter_by(ativo_id=filters['ativo_id'])
                if filters.get('tipo_provento'):
                    query = query.filter_by(tipo_provento=filters['tipo_provento'])
                if filters.get('data_com_inicio'):
                    query = query.filter(Provento.data_com >= filters['data_com_inicio'])
                if filters.get('data_com_fim'):
                    query = query.filter(Provento.data_com <= filters['data_com_fim'])
                if filters.get('data_pagamento_inicio'):
                    query = query.filter(Provento.data_pagamento >= filters['data_pagamento_inicio'])
                if filters.get('data_pagamento_fim'):
                    query = query.filter(Provento.data_pagamento <= filters['data_pagamento_fim'])
            
            query = query.order_by(Provento.data_com.desc())
            return query.paginate(page=page, per_page=per_page, error_out=False)
            
        except Exception as e:
            logger.error(f"Erro ao listar proventos: {e}")
            raise


    @staticmethod
    def get_by_id(provento_id):
        """Busca provento por ID"""
        return Provento.query.options(joinedload(Provento.ativo)).get(provento_id)


    @staticmethod
    def create(data):
        """
        Cria novo provento (ADMIN)
        
        Args:
            data (dict): Dados do provento
        
        Returns:
            Provento: Provento criado
        """
        try:
            ativo = Ativo.query.get(data['ativo_id'])
            if not ativo:
                raise ValueError("Ativo não encontrado")
            
            # Calcular valores se não fornecidos
            if 'valor_por_acao' in data and 'quantidade_ativos' in data:
                valor_bruto = Decimal(str(data['valor_por_acao'])) * Decimal(str(data['quantidade_ativos']))
                data['valor_bruto'] = valor_bruto
            
            if 'valor_bruto' in data and 'imposto_retido' in data:
                valor_liquido = Decimal(str(data['valor_bruto'])) - Decimal(str(data['imposto_retido']))
                data['valor_liquido'] = valor_liquido
            
            provento = Provento(**data)
            db.session.add(provento)
            db.session.commit()
            
            logger.info(f"Provento criado: {provento.id} - {ativo.ticker}")
            return provento
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar provento: {e}")
            raise


    @staticmethod
    def update(provento_id, data):
        """
        Atualiza provento (ADMIN)
        
        Args:
            provento_id (UUID): ID do provento
            data (dict): Dados a atualizar
        
        Returns:
            Provento: Provento atualizado
        """
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
            
            # Recalcular valores se necessário
            if 'valor_por_acao' in data or 'quantidade_ativos' in data:
                provento.valor_bruto = provento.valor_por_acao * provento.quantidade_ativos
            
            if 'valor_bruto' in data or 'imposto_retido' in data:
                provento.valor_liquido = provento.valor_bruto - provento.imposto_retido
            
            db.session.commit()
            logger.info(f"Provento atualizado: {provento.id}")
            return provento
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar provento: {e}")
            raise


    @staticmethod
    def delete(provento_id):
        """
        Deleta provento (ADMIN)
        
        Args:
            provento_id (UUID): ID do provento
        
        Returns:
            bool: True se deletado
        """
        try:
            provento = Provento.query.get(provento_id)
            if not provento:
                raise ValueError("Provento não encontrado")
            
            db.session.delete(provento)
            db.session.commit()
            logger.info(f"Provento deletado: {provento_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar provento: {e}")
            raise


    @staticmethod
    def get_por_ativo(ativo_id, page=1, per_page=50):
        """Lista proventos de um ativo específico"""
        try:
            query = Provento.query.filter_by(ativo_id=ativo_id).options(
                joinedload(Provento.ativo)
            ).order_by(Provento.data_com.desc())
            
            return query.paginate(page=page, per_page=per_page, error_out=False)
            
        except Exception as e:
            logger.error(f"Erro ao listar proventos por ativo: {e}")
            raise


    @staticmethod
    def get_recebidos_usuario(usuario_id, data_inicio=None, data_fim=None):
        """
        Calcula proventos recebidos pelo usuário em um período
        
        Args:
            usuario_id (UUID): ID do usuário
            data_inicio (date): Data inicial (opcional)
            data_fim (date): Data final (opcional)
        
        Returns:
            list: Lista de proventos recebidos com valores
        """
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
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
                    valor_liquido_recebido = valor_bruto_recebido * (prov.valor_liquido / prov.valor_bruto) if prov.valor_bruto > 0 else Decimal('0')
                    
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
            
        except Exception as e:
            logger.error(f"Erro ao calcular proventos recebidos: {e}")
            raise


    @staticmethod
    def calcular_total_recebido(usuario_id, ativo_id=None):
        """
        Calcula total de proventos recebidos
        
        Args:
            usuario_id (UUID): ID do usuário
            ativo_id (UUID, optional): Filtrar por ativo
        
        Returns:
            dict: Total de proventos por tipo
        """
        try:
            proventos = ProventoService.get_recebidos_usuario(usuario_id)
            
            if ativo_id:
                proventos = [p for p in proventos if p.get('ativo', {}).get('id') == str(ativo_id)]
            
            total_por_tipo = {}
            total_geral_bruto = Decimal('0')
            total_geral_liquido = Decimal('0')
            
            for p in proventos:
                tipo = p['tipo_provento']
                valor_bruto = Decimal(str(p['valor_bruto_recebido']))
                valor_liquido = Decimal(str(p['valor_liquido_recebido']))
                
                if tipo not in total_por_tipo:
                    total_por_tipo[tipo] = {
                        'quantidade': 0,
                        'valor_bruto': Decimal('0'),
                        'valor_liquido': Decimal('0')
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
                    }
                    for tipo, dados in total_por_tipo.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular total de proventos: {e}")
            raise
