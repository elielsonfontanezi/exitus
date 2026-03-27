# -*- coding: utf-8 -*-
"""
Exitus - Plano Venda Service
Lógica de negócio para planos de venda programada
"""

import logging
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from app.database import db
from app.models.plano_venda import PlanoVenda, StatusPlanoVenda, TipoGatilho
from app.models.ativo import Ativo
from app.models.posicao import Posicao
from app.services.cache_service import cache
from app.utils.tenant import filter_by_assessora, get_current_assessora_id

logger = logging.getLogger(__name__)


class PlanoVendaService:
    """Service para gerenciamento de planos de venda"""
    
    @staticmethod
    def create(data: Dict, usuario_id: UUID) -> PlanoVenda:
        """Cria um novo plano de venda"""
        try:
            # Validar se usuário tem posição suficiente no ativo
            ativo_id = UUID(data['ativo_id'])
            posicao = Posicao.query.filter_by(
                usuario_id=usuario_id, 
                ativo_id=ativo_id
            ).first()
            
            if not posicao or posicao.quantidade < Decimal(str(data.get('quantidade_total', 0))):
                raise ValueError("Quantidade insuficiente na posição para criar plano de venda")
            
            # Obter assessora_id do JWT ou dos dados
            assessora_id = data.get('assessora_id') or get_current_assessora_id()
            
            # Criar plano
            plano = PlanoVenda(
                usuario_id=usuario_id,
                nome=data['nome'],
                descricao=data.get('descricao'),
                ativo_id=ativo_id,
                quantidade_total=Decimal(str(data['quantidade_total'])),
                quantidade_vendida=Decimal('0'),
                preco_minimo=Decimal(str(data['preco_minimo'])) if data.get('preco_minimo') else None,
                preco_alvo=Decimal(str(data['preco_alvo'])) if data.get('preco_alvo') else None,
                tipo_gatilho=TipoGatilho(data['tipo_gatilho']),
                gatilho_valor=Decimal(str(data['gatilho_valor'])) if data.get('gatilho_valor') else None,
                data_limite=datetime.strptime(data['data_limite'], '%Y-%m-%d').date() if data.get('data_limite') else None,
                parcelas_total=data.get('parcelas_total'),
                parcelas_executadas=0,
                valor_parcela_fixo=Decimal(str(data['valor_parcela_fixo'])) if data.get('valor_parcela_fixo') else None,
                status=StatusPlanoVenda.ATIVO,
                data_inicio=date.today(),
                assessora_id=assessora_id
            )
            
            db.session.add(plano)
            db.session.commit()
            
            # Limpar cache do usuário
            cache.clear_pattern(f"plano_venda:{usuario_id}:*")
            
            logger.info(f"Plano de venda criado: {plano.id} - {plano.nome}")
            return plano
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro ao criar plano de venda: {e}")
            raise e
    
    @staticmethod
    def get_by_id(plano_id: UUID, usuario_id: UUID) -> Optional[PlanoVenda]:
        """Busca plano por ID garantindo ownership"""
        cache_key = f"plano_venda:{usuario_id}:{plano_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        plano = PlanoVenda.query.filter_by(
            id=plano_id, 
            usuario_id=usuario_id
        ).first()
        
        if plano:
            cache.set(cache_key, plano, ttl=300)
        
        return plano
    
    @staticmethod
    def get_all(usuario_id: UUID, page: int = 1, per_page: int = 20, status: Optional[str] = None) -> Dict:
        """Lista planos do usuário com paginação e filtros"""
        cache_key = f"plano_venda:{usuario_id}:list:{page}:{per_page}:{status or 'all'}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        query = PlanoVenda.query.filter_by(usuario_id=usuario_id)
        
        if status:
            query = query.filter_by(status=StatusPlanoVenda(status))
        
        # Ordenar por status (ativos primeiro) e data de criação
        query = query.order_by(
            PlanoVenda.status.asc(),
            PlanoVenda.created_at.desc()
        )
        
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        result = {
            'planos': paginated.items,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
        
        cache.set(cache_key, result, ttl=180)
        return result
    
    @staticmethod
    def update(plano_id: UUID, data: Dict, usuario_id: UUID) -> Optional[PlanoVenda]:
        """Atualiza plano existente"""
        plano = PlanoVendaService.get_by_id(plano_id, usuario_id)
        if not plano:
            return None
        
        try:
            # Não permitir editar se já tiver vendas executadas
            if plano.quantidade_vendida > 0:
                raise ValueError("Não é possível editar plano com vendas já executadas")
            
            # Atualizar campos permitidos
            updatable_fields = [
                'nome', 'descricao', 'preco_minimo', 'preco_alvo',
                'tipo_gatilho', 'gatilho_valor', 'data_limite',
                'parcelas_total', 'valor_parcela_fixo'
            ]
            
            for field in updatable_fields:
                if field in data and data[field] is not None:
                    if field in ['preco_minimo', 'preco_alvo', 'gatilho_valor', 'valor_parcela_fixo']:
                        setattr(plano, field, Decimal(str(data[field])))
                    elif field == 'tipo_gatilho':
                        setattr(plano, field, TipoGatilho(data[field]))
                    elif field == 'data_limite':
                        setattr(plano, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                    else:
                        setattr(plano, field, data[field])
            
            plano.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Limpar caches
            cache.clear_pattern(f"plano_venda:{usuario_id}:*")
            
            logger.info(f"Plano de venda atualizado: {plano.id}")
            return plano
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar plano de venda: {e}")
            raise e
    
    @staticmethod
    def delete(plano_id: UUID, usuario_id: UUID) -> bool:
        """Remove (soft delete) um plano"""
        plano = PlanoVendaService.get_by_id(plano_id, usuario_id)
        if not plano:
            return False
        
        try:
            # Não permitir deletar se já tiver vendas
            if plano.quantidade_vendida > 0:
                plano.cancelar()
            else:
                plano.status = StatusPlanoVenda.CANCELADO
            
            plano.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Limpar caches
            cache.clear_pattern(f"plano_venda:{usuario_id}:*")
            
            logger.info(f"Plano de venda cancelado: {plano.id}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro ao cancelar plano de venda: {e}")
            raise e
    
    @staticmethod
    def pausar(plano_id: UUID, usuario_id: UUID) -> bool:
        """Pausa um plano ativo"""
        plano = PlanoVendaService.get_by_id(plano_id, usuario_id)
        if not plano or not plano.esta_ativo():
            return False
        
        plano.pausar()
        db.session.commit()
        
        # Limpar caches
        cache.clear_pattern(f"plano_venda:{usuario_id}:*")
        
        logger.info(f"Plano de venda pausado: {plano.id}")
        return True
    
    @staticmethod
    def reativar(plano_id: UUID, usuario_id: UUID) -> bool:
        """Reativa um plano pausado"""
        plano = PlanoVendaService.get_by_id(plano_id, usuario_id)
        if not plano or plano.status != StatusPlanoVenda.PAUSADO:
            return False
        
        plano.reativar()
        db.session.commit()
        
        # Limpar caches
        cache.clear_pattern(f"plano_venda:{usuario_id}:*")
        
        logger.info(f"Plano de venda reativado: {plano.id}")
        return True
    
    @staticmethod
    def verificar_gatilhos(usuario_id: UUID) -> List[Dict]:
        """Verifica todos os planos ativos e identifica os que devem disparar"""
        planos_ativos = PlanoVenda.query.filter_by(
            usuario_id=usuario_id,
            status=StatusPlanoVenda.ATIVO
        ).all()
        
        disparos = []
        
        for plano in planos_ativos:
            if not plano.pode_executar_venda():
                continue
            
            # Obter preço atual do ativo
            ativo = plano.ativo
            if not ativo or not ativo.preco_atual:
                continue
            
            preco_atual = Decimal(str(ativo.preco_atual))
            deve_disparar = False
            motivo = ""
            
            # Verificar gatilhos
            if plano.deve_disparar_por_preco(preco_atual):
                deve_disparar = True
                motivo = f"Preço alvo atingido: R$ {preco_atual:.2f}"
            
            elif plano.tipo_gatilho == TipoGatilho.PERCENTUAL_LUCRO:
                # Obter preço médio da posição
                posicao = Posicao.query.filter_by(
                    usuario_id=usuario_id,
                    ativo_id=plano.ativo_id
                ).first()
                
                if posicao and posicao.preco_medio:
                    if plano.deve_disparar_por_percentual(preco_atual, posicao.preco_medio):
                        deve_disparar = True
                        lucro = ((preco_atual - posicao.preco_medio) / posicao.preco_medio) * 100
                        motivo = f"Lucro alvo atingido: {lucro:.1f}%"
            
            elif plano.deve_disparar_por_data():
                deve_disparar = True
                motivo = f"Data limite atingida: {plano.data_limite}"
            
            elif plano.tipo_gatilho in [TipoGatilho.PARCELAS_SEMANAIS, TipoGatilho.PARCELAS_MENSAIS]:
                # Lógica de parcelas seria implementada com agendamento
                # Por enquanto, apenas verifica se restam parcelas
                if plano.parcelas_restantes and plano.parcelas_restantes > 0:
                    deve_disparar = True
                    motivo = f"Parcela {plano.parcelas_executadas + 1}/{plano.parcelas_total}"
            
            if deve_disparar:
                quantidade = plano.calcular_quantidade_parcela() or plano.quantidade_restante
                
                disparos.append({
                    'plano_id': str(plano.id),
                    'plano_nome': plano.nome,
                    'ativo_ticker': ativo.ticker,
                    'quantidade': float(quantidade),
                    'preco_atual': float(preco_atual),
                    'motivo': motivo,
                    'tipo_gatilho': plano.tipo_gatilho.value
                })
        
        return disparos
    
    @staticmethod
    def get_dashboard(usuario_id: UUID) -> Dict:
        """Retorna dados para dashboard de planos de venda"""
        cache_key = f"plano_venda_dashboard:{usuario_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        planos = PlanoVenda.query.filter_by(usuario_id=usuario_id).all()
        
        total_planos = len(planos)
        planos_ativos = len([p for p in planos if p.esta_ativo()])
        planos_concluidos = len([p for p in planos if p.esta_concluido()])
        
        # Calcular valores
        quantidade_total_vender = sum(float(p.quantidade_total) for p in planos)
        quantidade_total_vendida = sum(float(p.quantidade_vendida) for p in planos)
        
        # Próximos gatilhos
        proximos_gatilhos = []
        for plano in planos:
            if plano.esta_ativo() and plano.data_limite:
                proximos_gatilhos.append({
                    'plano_nome': plano.nome,
                    'data_limite': plano.data_limite.isoformat(),
                    'dias_restantes': (plano.data_limite - date.today()).days
                })
        
        proximos_gatilhos.sort(key=lambda x: x['dias_restantes'])
        proximos_gatilhos = proximos_gatilhos[:5]
        
        result = {
            'resumo': {
                'total_planos': total_planos,
                'planos_ativos': planos_ativos,
                'planos_concluidos': planos_concluidos,
                'quantidade_total_vender': quantidade_total_vender,
                'quantidade_total_vendida': quantidade_total_vendida,
                'progresso_geral': (quantidade_total_vendida / quantidade_total_vender * 100) if quantidade_total_vender > 0 else 0
            },
            'proximos_gatilhos': proximos_gatilhos,
            'ultimas_atualizacoes': [
                {
                    'plano_nome': p.nome,
                    'status': p.status.value,
                    'updated_at': p.updated_at.isoformat()
                }
                for p in sorted(planos, key=lambda x: x.updated_at, reverse=True)[:5]
            ]
        }
        
        cache.set(cache_key, result, ttl=300)
        return result
    
    @staticmethod
    def get_estatisticas(usuario_id: UUID) -> Dict:
        """Retorna estatísticas detalhadas dos planos de venda"""
        planos = PlanoVenda.query.filter_by(usuario_id=usuario_id).all()
        
        if not planos:
            return {
                'total_planos': 0,
                'por_status': {},
                'por_gatilho': {},
                'por_ativo': {},
                'volume_total': 0,
                'volume_vendido': 0
            }
        
        # Agrupar por status
        por_status = {}
        for status in StatusPlanoVenda:
            por_status[status.value] = len([p for p in planos if p.status == status])
        
        # Agrupar por gatilho
        por_gatilho = {}
        for gatilho in TipoGatilho:
            por_gatilho[gatilho.value] = len([p for p in planos if p.tipo_gatilho == gatilho])
        
        # Agrupar por ativo
        por_ativo = {}
        for plano in planos:
            ticker = plano.ativo.ticker if plano.ativo else 'N/A'
            por_ativo[ticker] = por_ativo.get(ticker, 0) + 1
        
        # Volume
        volume_total = sum(float(p.quantidade_total) for p in planos)
        volume_vendido = sum(float(p.quantidade_vendida) for p in planos)
        
        return {
            'total_planos': len(planos),
            'por_status': por_status,
            'por_gatilho': por_gatilho,
            'por_ativo': dict(sorted(por_ativo.items(), key=lambda x: x[1], reverse=True)[:10]),
            'volume_total': volume_total,
            'volume_vendido': volume_vendido,
            'taxa_conclusao': (volume_vendido / volume_total * 100) if volume_total > 0 else 0
        }
