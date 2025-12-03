# -*- coding: utf-8 -*-
"""
Exitus - EventoCorporativo Service
Service layer para gerenciamento de eventos corporativos
"""

from app.database import db
from app.models import EventoCorporativo, Ativo, Posicao
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventoCorporativoService:
    """Service para operações de eventos corporativos"""

    @staticmethod
    def get_all(page=1, per_page=50, filters=None):
        """
        Lista eventos corporativos com filtros
        
        Args:
            page (int): Página atual
            per_page (int): Registros por página
            filters (dict): Filtros opcionais
        
        Returns:
            Pagination: Objeto de paginação
        """
        try:
            query = EventoCorporativo.query.options(joinedload(EventoCorporativo.ativo))
            
            if filters:
                if filters.get('ativo_id'):
                    query = query.filter_by(ativo_id=filters['ativo_id'])
                if filters.get('tipo_evento'):
                    query = query.filter_by(tipo_evento=filters['tipo_evento'])
                if filters.get('data_anuncio_inicio'):
                    query = query.filter(EventoCorporativo.data_anuncio >= filters['data_anuncio_inicio'])
                if filters.get('data_anuncio_fim'):
                    query = query.filter(EventoCorporativo.data_anuncio <= filters['data_anuncio_fim'])
                if filters.get('data_aprovacao_inicio'):
                    query = query.filter(EventoCorporativo.data_aprovacao >= filters['data_aprovacao_inicio'])
                if filters.get('data_aprovacao_fim'):
                    query = query.filter(EventoCorporativo.data_aprovacao <= filters['data_aprovacao_fim'])
            
            query = query.order_by(EventoCorporativo.data_anuncio.desc())
            return query.paginate(page=page, per_page=per_page, error_out=False)
            
        except Exception as e:
            logger.error(f"Erro ao listar eventos: {e}")
            raise


    @staticmethod
    def get_by_id(evento_id):
        """Busca evento por ID"""
        return EventoCorporativo.query.options(joinedload(EventoCorporativo.ativo)).get(evento_id)


    @staticmethod
    def create(data):
        """
        Cria novo evento corporativo (ADMIN)
        
        Args:
            data (dict): Dados do evento
        
        Returns:
            EventoCorporativo: Evento criado
        """
        try:
            ativo = Ativo.query.get(data['ativo_id'])
            if not ativo:
                raise ValueError("Ativo não encontrado")
            
            evento = EventoCorporativo(**data)
            db.session.add(evento)
            db.session.commit()
            
            logger.info(f"Evento criado: {evento.id} - {ativo.ticker} - {evento.tipo_evento.value}")
            return evento
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar evento: {e}")
            raise


    @staticmethod
    def update(evento_id, data):
        """
        Atualiza evento corporativo (ADMIN)
        
        Args:
            evento_id (UUID): ID do evento
            data (dict): Dados a atualizar
        
        Returns:
            EventoCorporativo: Evento atualizado
        """
        try:
            evento = EventoCorporativo.query.get(evento_id)
            if not evento:
                raise ValueError("Evento não encontrado")
            
            campos_permitidos = [
                'tipo_evento', 'descricao', 'data_anuncio', 'data_com',
                'data_aprovacao', 'data_execucao', 'proporcao',
                'preco_subscricao', 'observacoes', 'url_informacao'
            ]
            
            for campo in campos_permitidos:
                if campo in data:
                    setattr(evento, campo, data[campo])
            
            db.session.commit()
            logger.info(f"Evento atualizado: {evento.id}")
            return evento
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar evento: {e}")
            raise


    @staticmethod
    def delete(evento_id):
        """
        Deleta evento corporativo (ADMIN)
        
        Args:
            evento_id (UUID): ID do evento
        
        Returns:
            bool: True se deletado
        """
        try:
            evento = EventoCorporativo.query.get(evento_id)
            if not evento:
                raise ValueError("Evento não encontrado")
            
            db.session.delete(evento)
            db.session.commit()
            logger.info(f"Evento deletado: {evento_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar evento: {e}")
            raise


    @staticmethod
    def get_por_ativo(ativo_id, page=1, per_page=50):
        """Lista eventos de um ativo específico"""
        try:
            query = EventoCorporativo.query.filter_by(ativo_id=ativo_id).options(
                joinedload(EventoCorporativo.ativo)
            ).order_by(EventoCorporativo.data_anuncio.desc())
            
            return query.paginate(page=page, per_page=per_page, error_out=False)
            
        except Exception as e:
            logger.error(f"Erro ao listar eventos por ativo: {e}")
            raise


    @staticmethod
    def get_eventos_usuario(usuario_id, data_inicio=None, data_fim=None):
        """
        Lista eventos que afetam as posições do usuário
        
        Args:
            usuario_id (UUID): ID do usuário
            data_inicio (date): Data inicial (opcional)
            data_fim (date): Data final (opcional)
        
        Returns:
            list: Lista de eventos relevantes
        """
        try:
            # Buscar posições do usuário
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            if not posicoes:
                return []
            
            ativos_ids = [p.ativo_id for p in posicoes]
            
            query = EventoCorporativo.query.filter(EventoCorporativo.ativo_id.in_(ativos_ids))
            
            if data_inicio:
                query = query.filter(EventoCorporativo.data_anuncio >= data_inicio)
            if data_fim:
                query = query.filter(EventoCorporativo.data_anuncio <= data_fim)
            
            query = query.options(joinedload(EventoCorporativo.ativo)).order_by(
                EventoCorporativo.data_anuncio.desc()
            )
            
            eventos = query.all()
            
            eventos_formatados = []
            
            for evento in eventos:
                posicao = next((p for p in posicoes if p.ativo_id == evento.ativo_id), None)
                
                if posicao:
                    eventos_formatados.append({
                        'evento_id': str(evento.id),
                        'ativo': {
                            'ticker': evento.ativo.ticker,
                            'nome': evento.ativo.nome
                        },
                        'tipo_evento': evento.tipo_evento.value,
                        'descricao': evento.descricao,
                        'data_anuncio': evento.data_anuncio.isoformat(),
                        'data_com': evento.data_com.isoformat() if evento.data_com else None,
                        'data_execucao': evento.data_execucao.isoformat() if evento.data_execucao else None,
                        'proporcao': evento.proporcao,
                        'quantidade_afetada': float(posicao.quantidade),
                        'impacto_estimado': EventoCorporativoService._calcular_impacto(evento, posicao)
                    })
            
            return eventos_formatados
            
        except Exception as e:
            logger.error(f"Erro ao buscar eventos do usuário: {e}")
            raise


    @staticmethod
    def _calcular_impacto(evento, posicao):
        """Calcula impacto estimado de um evento em uma posição"""
        try:
            tipo = evento.tipo_evento.value
            
            if tipo == 'desdobramento':
                # Split: quantidade aumenta
                if evento.proporcao:
                    nova_quantidade = posicao.quantidade * Decimal(evento.proporcao)
                    return {
                        'tipo': 'aumento_quantidade',
                        'nova_quantidade': float(nova_quantidade),
                        'diferenca': float(nova_quantidade - posicao.quantidade)
                    }
            
            elif tipo == 'grupamento':
                # Reverse split: quantidade diminui
                if evento.proporcao:
                    nova_quantidade = posicao.quantidade / Decimal(evento.proporcao)
                    return {
                        'tipo': 'reducao_quantidade',
                        'nova_quantidade': float(nova_quantidade),
                        'diferenca': float(posicao.quantidade - nova_quantidade)
                    }
            
            elif tipo == 'bonificacao':
                # Bonificação: novas ações grátis
                if evento.proporcao:
                    novas_acoes = posicao.quantidade * Decimal(evento.proporcao)
                    return {
                        'tipo': 'bonificacao',
                        'novas_acoes': float(novas_acoes),
                        'quantidade_final': float(posicao.quantidade + novas_acoes)
                    }
            
            elif tipo == 'subscricao':
                # Direito de subscrição: possibilidade de compra
                if evento.proporcao and evento.preco_subscricao:
                    direitos = posicao.quantidade * Decimal(evento.proporcao)
                    custo_subscricao = direitos * evento.preco_subscricao
                    return {
                        'tipo': 'direito_subscricao',
                        'quantidade_direitos': float(direitos),
                        'preco_subscricao': float(evento.preco_subscricao),
                        'custo_total': float(custo_subscricao)
                    }
            
            return {'tipo': 'informativo', 'descricao': evento.descricao}
            
        except Exception as e:
            logger.error(f"Erro ao calcular impacto: {e}")
            return {'tipo': 'erro', 'mensagem': 'Não foi possível calcular o impacto'}


    @staticmethod
    def aplicar_evento_split(evento_id, usuario_id):
        """
        Aplica desdobramento/grupamento nas posições do usuário
        
        Args:
            evento_id (UUID): ID do evento
            usuario_id (UUID): ID do usuário
        
        Returns:
            dict: Resultado da aplicação
        """
        try:
            evento = EventoCorporativo.query.get(evento_id)
            if not evento:
                raise ValueError("Evento não encontrado")
            
            if evento.tipo_evento.value not in ['desdobramento', 'grupamento']:
                raise ValueError("Evento não é desdobramento ou grupamento")
            
            if not evento.proporcao:
                raise ValueError("Evento sem proporção definida")
            
            # Buscar posições do ativo do usuário
            posicoes = Posicao.query.filter_by(
                usuario_id=usuario_id,
                ativo_id=evento.ativo_id
            ).all()
            
            if not posicoes:
                return {'posicoes_afetadas': 0, 'mensagem': 'Usuário não possui este ativo'}
            
            posicoes_atualizadas = 0
            
            for posicao in posicoes:
                quantidade_antiga = posicao.quantidade
                
                if evento.tipo_evento.value == 'desdobramento':
                    posicao.quantidade = quantidade_antiga * Decimal(evento.proporcao)
                    posicao.preco_medio = posicao.preco_medio / Decimal(evento.proporcao)
                else:  # grupamento
                    posicao.quantidade = quantidade_antiga / Decimal(evento.proporcao)
                    posicao.preco_medio = posicao.preco_medio * Decimal(evento.proporcao)
                
                posicao.data_ultima_atualizacao = datetime.utcnow()
                posicoes_atualizadas += 1
            
            db.session.commit()
            
            logger.info(f"Evento {evento_id} aplicado a {posicoes_atualizadas} posições do usuário {usuario_id}")
            
            return {
                'posicoes_afetadas': posicoes_atualizadas,
                'tipo_evento': evento.tipo_evento.value,
                'proporcao': evento.proporcao
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao aplicar evento: {e}")
            raise
