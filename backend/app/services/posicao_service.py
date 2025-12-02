# -*- coding: utf-8 -*-
"""
Exitus - Posicao Service
Service layer para gerenciamento de posições (holdings)
"""

from app.database import db
from app.models import Posicao, Transacao, Ativo, Corretora
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PosicaoService:
    """Service para operações de posições"""

    @staticmethod
    def get_all(usuario_id, page=1, per_page=50, filters=None):
        """
        Lista todas as posições do usuário com filtros opcionais
        
        Args:
            usuario_id (UUID): ID do usuário
            page (int): Página atual
            per_page (int): Registros por página
            filters (dict): Filtros opcionais
        
        Returns:
            Pagination: Objeto de paginação
        """
        try:
            query = Posicao.query.filter_by(usuario_id=usuario_id)
            query = query.options(
                joinedload(Posicao.ativo),
                joinedload(Posicao.corretora)
            )
            
            if filters:
                if filters.get('ativo_id'):
                    query = query.filter_by(ativo_id=filters['ativo_id'])
                if filters.get('corretora_id'):
                    query = query.filter_by(corretora_id=filters['corretora_id'])
                if filters.get('ticker'):
                    query = query.join(Ativo).filter(
                        Ativo.ticker.ilike(f"%{filters['ticker']}%")
                    )
                if filters.get('lucro_positivo') is not None:
                    if filters['lucro_positivo']:
                        query = query.filter(
                            Posicao.lucro_prejuizo_realizado + 
                            func.coalesce(Posicao.lucro_prejuizo_nao_realizado, 0) > 0
                        )
            
            query = query.order_by(Posicao.custo_total.desc())
            return query.paginate(page=page, per_page=per_page, error_out=False)
            
        except Exception as e:
            logger.error(f"Erro ao listar posições: {e}")
            raise


    @staticmethod
    def get_by_id(posicao_id, usuario_id):
        """Busca posição por ID"""
        return Posicao.query.filter_by(
            id=posicao_id,
            usuario_id=usuario_id
        ).options(
            joinedload(Posicao.ativo),
            joinedload(Posicao.corretora)
        ).first()


    @staticmethod
    def calcular_posicoes(usuario_id):
        """Recalcula todas as posições do usuário a partir das transações"""
        try:
            transacoes = Transacao.query.filter_by(usuario_id=usuario_id).all()
            
            if not transacoes:
                return {"posicoes_criadas": 0, "posicoes_atualizadas": 0, "posicoes_zeradas": 0}
            
            # Agrupar por (ativo_id, corretora_id)
            posicoes_map = {}
            for t in transacoes:
                chave = (str(t.ativo_id), str(t.corretora_id))
                if chave not in posicoes_map:
                    posicoes_map[chave] = {
                        'ativo_id': t.ativo_id,
                        'corretora_id': t.corretora_id,
                        'transacoes': []
                    }
                posicoes_map[chave]['transacoes'].append(t)
            
            criadas = atualizadas = zeradas = 0
            
            for dados in posicoes_map.values():
                resultado = PosicaoService._processar_posicao(
                    usuario_id, dados['ativo_id'], 
                    dados['corretora_id'], dados['transacoes']
                )
                if resultado == 'criada': criadas += 1
                elif resultado == 'atualizada': atualizadas += 1
                elif resultado == 'zerada': zeradas += 1
            
            db.session.commit()
            
            return {
                "posicoes_criadas": criadas,
                "posicoes_atualizadas": atualizadas,
                "posicoes_zeradas": zeradas
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao calcular posições: {e}")
            raise


    @staticmethod
    def _processar_posicao(usuario_id, ativo_id, corretora_id, transacoes):
        """Processa transações de uma posição específica"""
        transacoes = sorted(transacoes, key=lambda t: t.data_transacao)
        
        quantidade_total = Decimal('0')
        custo_total = Decimal('0')
        taxas_acumuladas = Decimal('0')
        impostos_acumulados = Decimal('0')
        lucro_realizado = Decimal('0')
        data_primeira_compra = None
        
        for t in transacoes:
            if t.tipo.value == 'compra':
                quantidade_total += t.quantidade
                custo_total += t.valor_liquido
                taxas_acumuladas += t.custos_totais
                impostos_acumulados += t.imposto
                if data_primeira_compra is None:
                    data_primeira_compra = t.data_transacao
            
            elif t.tipo.value == 'venda':
                if quantidade_total > 0:
                    preco_medio = custo_total / quantidade_total
                    custo_vendido = preco_medio * t.quantidade
                    lucro_realizado += (t.valor_total - custo_vendido)
                
                quantidade_total -= t.quantidade
                if quantidade_total > 0:
                    custo_total -= (custo_total * t.quantidade / (quantidade_total + t.quantidade))
                else:
                    custo_total = Decimal('0')
                taxas_acumuladas += t.custos_totais
                impostos_acumulados += t.imposto
        
        preco_medio = custo_total / quantidade_total if quantidade_total > 0 else Decimal('0')
        
        posicao = Posicao.query.filter_by(
            usuario_id=usuario_id,
            ativo_id=ativo_id,
            corretora_id=corretora_id
        ).first()
        
        if quantidade_total <= 0:
            if posicao:
                db.session.delete(posicao)
                return 'zerada'
            return 'nenhuma'
        
        if not posicao:
            posicao = Posicao(
                usuario_id=usuario_id,
                ativo_id=ativo_id,
                corretora_id=corretora_id
            )
            db.session.add(posicao)
            resultado = 'criada'
        else:
            resultado = 'atualizada'
        
        posicao.quantidade = quantidade_total
        posicao.preco_medio = preco_medio
        posicao.custo_total = custo_total
        posicao.taxas_acumuladas = taxas_acumuladas
        posicao.impostos_acumulados = impostos_acumulados
        posicao.lucro_prejuizo_realizado = lucro_realizado
        posicao.data_primeira_compra = data_primeira_compra
        posicao.data_ultima_atualizacao = datetime.utcnow()
        
        return resultado


    @staticmethod
    def atualizar_valores_atuais(usuario_id):
        """Atualiza valores de mercado de todas as posições"""
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            atualizadas = 0
            for p in posicoes:
                if p.ativo.preco_atual and p.quantidade > 0:
                    p.valor_atual = p.ativo.preco_atual * p.quantidade
                    p.lucro_prejuizo_nao_realizado = p.valor_atual - p.custo_total
                    p.data_ultima_atualizacao = datetime.utcnow()
                    atualizadas += 1
            
            db.session.commit()
            return atualizadas
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar valores: {e}")
            raise


    @staticmethod
    def get_resumo(usuario_id):
        """Retorna resumo consolidado das posições"""
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            total_investido = sum(p.custo_total for p in posicoes)
            total_valor_atual = sum(p.valor_atual or Decimal('0') for p in posicoes)
            total_lucro_realizado = sum(p.lucro_prejuizo_realizado for p in posicoes)
            total_lucro_nao_realizado = sum(p.lucro_prejuizo_nao_realizado or Decimal('0') for p in posicoes)
            
            lucro_total = total_lucro_realizado + total_lucro_nao_realizado
            roi = (lucro_total / total_investido * 100) if total_investido > 0 else Decimal('0')
            
            return {
                'quantidade_posicoes': len(posicoes),
                'total_investido': float(total_investido),
                'total_valor_atual': float(total_valor_atual),
                'total_lucro_realizado': float(total_lucro_realizado),
                'total_lucro_nao_realizado': float(total_lucro_nao_realizado),
                'lucro_total': float(lucro_total),
                'roi_percentual': float(roi)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
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
            valor_atual_total = sum(p.valor_atual or Decimal('0') for p in posicoes)
            preco_medio = custo_total / quantidade_total if quantidade_total > 0 else Decimal('0')
            
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
                    }
                    for p in posicoes
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao consolidar posição: {e}")
            raise
