# -*- coding: utf-8 -*-
"""
Exitus - Reconciliacao Service
Serviço para verificação de consistência entre dados calculados e importados
GAP: EXITUS-RECONCILIACAO-001
"""

from decimal import Decimal
from typing import Dict, List
import logging

from app.database import db
from app.models import Posicao, Transacao, MovimentacaoCaixa, Corretora, Ativo
from sqlalchemy import func

logger = logging.getLogger(__name__)


class ReconciliacaoService:
    """
    Serviço para reconciliação e verificação de consistência de dados.
    
    Verifica:
    1. Posições calculadas vs transações importadas
    2. Saldo da corretora vs soma de movimentações
    3. Integridade geral dos dados
    """
    
    TOLERANCIA = Decimal('0.01')  # Tolerância para diferenças de arredondamento
    
    @staticmethod
    def verificar_tudo(usuario_id) -> Dict:
        """
        Executa todas as verificações de reconciliação.
        
        Args:
            usuario_id (UUID): ID do usuário
        
        Returns:
            dict: {
                'status': 'OK' | 'WARNING' | 'ERROR',
                'divergencias': [...],
                'resumo': {...}
            }
        """
        try:
            divergencias = []
            
            # 1. Verificar posições
            div_posicoes = ReconciliacaoService.verificar_posicoes(usuario_id)
            divergencias.extend(div_posicoes)
            
            # 2. Verificar saldos de corretoras
            div_saldos = ReconciliacaoService.verificar_saldos_corretoras(usuario_id)
            divergencias.extend(div_saldos)
            
            # 3. Verificar integridade de transações
            div_transacoes = ReconciliacaoService.verificar_integridade_transacoes(usuario_id)
            divergencias.extend(div_transacoes)
            
            # Determinar status geral
            if not divergencias:
                status = 'OK'
            elif any(d['severidade'] == 'ERROR' for d in divergencias):
                status = 'ERROR'
            else:
                status = 'WARNING'
            
            return {
                'status': status,
                'divergencias': divergencias,
                'resumo': {
                    'total_divergencias': len(divergencias),
                    'erros': sum(1 for d in divergencias if d['severidade'] == 'ERROR'),
                    'avisos': sum(1 for d in divergencias if d['severidade'] == 'WARNING')
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na reconciliação: {e}")
            raise
    
    @staticmethod
    def verificar_posicoes(usuario_id) -> List[Dict]:
        """
        Verifica consistência entre posições calculadas e transações.
        
        Compara:
        - Quantidade em Posicao vs soma de transações (compra - venda)
        - Custo total vs soma de valores líquidos de compras
        
        Returns:
            list: Lista de divergências encontradas
        """
        divergencias = []
        
        try:
            # Buscar todas as posições do usuário
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
            
            for posicao in posicoes:
                # Calcular quantidade esperada a partir de transações
                transacoes = Transacao.query.filter_by(
                    usuario_id=usuario_id,
                    ativo_id=posicao.ativo_id,
                    corretora_id=posicao.corretora_id
                ).all()
                
                quantidade_calculada = Decimal('0')
                custo_calculado = Decimal('0')
                
                for t in transacoes:
                    if t.tipo.value == 'compra':
                        quantidade_calculada += t.quantidade
                        custo_calculado += t.valor_liquido
                    elif t.tipo.value == 'venda':
                        quantidade_calculada -= t.quantidade
                        # Custo reduz proporcionalmente na venda
                
                # Verificar divergência de quantidade
                diff_quantidade = abs(posicao.quantidade - quantidade_calculada)
                if diff_quantidade > ReconciliacaoService.TOLERANCIA:
                    divergencias.append({
                        'tipo': 'POSICAO_QUANTIDADE',
                        'severidade': 'ERROR',
                        'ativo_id': str(posicao.ativo_id),
                        'ativo_ticker': posicao.ativo.ticker if posicao.ativo else 'N/A',
                        'corretora_id': str(posicao.corretora_id),
                        'corretora_nome': posicao.corretora.nome if posicao.corretora else 'N/A',
                        'quantidade_posicao': float(posicao.quantidade),
                        'quantidade_calculada': float(quantidade_calculada),
                        'diferenca': float(diff_quantidade),
                        'mensagem': f"Divergência de quantidade: {posicao.ativo.ticker if posicao.ativo else 'N/A'} "
                                   f"na {posicao.corretora.nome if posicao.corretora else 'N/A'}"
                    })
                
                # Verificar divergência de custo (apenas se quantidade > 0)
                if quantidade_calculada > 0:
                    diff_custo = abs(posicao.custo_total - custo_calculado)
                    if diff_custo > Decimal('1.00'):  # Tolerância maior para custos
                        divergencias.append({
                            'tipo': 'POSICAO_CUSTO',
                            'severidade': 'WARNING',
                            'ativo_id': str(posicao.ativo_id),
                            'ativo_ticker': posicao.ativo.ticker if posicao.ativo else 'N/A',
                            'corretora_id': str(posicao.corretora_id),
                            'custo_posicao': float(posicao.custo_total),
                            'custo_calculado': float(custo_calculado),
                            'diferenca': float(diff_custo),
                            'mensagem': f"Divergência de custo: {posicao.ativo.ticker if posicao.ativo else 'N/A'}"
                        })
            
            return divergencias
            
        except Exception as e:
            logger.error(f"Erro ao verificar posições: {e}")
            raise
    
    @staticmethod
    def verificar_saldos_corretoras(usuario_id) -> List[Dict]:
        """
        Verifica se saldo da corretora bate com soma de movimentações.
        
        Saldo esperado = SUM(DEPOSITO + DIVIDENDO + VENDA) - SUM(SAQUE + COMPRA + TAXA)
        
        Returns:
            list: Lista de divergências encontradas
        """
        divergencias = []
        
        try:
            # Buscar corretoras do usuário
            corretoras = Corretora.query.filter_by(usuario_id=usuario_id).all()
            
            for corretora in corretoras:
                # Calcular saldo a partir de movimentações
                movimentacoes = MovimentacaoCaixa.query.filter_by(
                    usuario_id=usuario_id,
                    corretora_id=corretora.id
                ).all()
                
                saldo_calculado = Decimal('0')
                
                for mov in movimentacoes:
                    tipo = str(mov.tipo_movimentacao).upper()
                    valor = Decimal(str(mov.valor))
                    
                    # Entradas (+)
                    if tipo in ['DEPOSITO', 'DIVIDENDO', 'JCP', 'VENDA', 'BONIFICACAO']:
                        saldo_calculado += valor
                    # Saídas (-)
                    elif tipo in ['SAQUE', 'COMPRA', 'TAXA']:
                        saldo_calculado -= valor
                
                # Comparar com saldo registrado na corretora
                saldo_registrado = corretora.saldo_atual or Decimal('0')
                diff_saldo = abs(saldo_registrado - saldo_calculado)
                
                if diff_saldo > Decimal('1.00'):  # Tolerância de R$ 1,00
                    divergencias.append({
                        'tipo': 'SALDO_CORRETORA',
                        'severidade': 'WARNING',
                        'corretora_id': str(corretora.id),
                        'corretora_nome': corretora.nome,
                        'saldo_registrado': float(saldo_registrado),
                        'saldo_calculado': float(saldo_calculado),
                        'diferenca': float(diff_saldo),
                        'mensagem': f"Divergência de saldo na corretora {corretora.nome}"
                    })
            
            return divergencias
            
        except Exception as e:
            logger.error(f"Erro ao verificar saldos: {e}")
            raise
    
    @staticmethod
    def verificar_integridade_transacoes(usuario_id) -> List[Dict]:
        """
        Verifica integridade geral das transações.
        
        Verifica:
        - Transações sem ativo ou corretora
        - Transações com valores zerados
        - Transações duplicadas (mesmo hash_importacao)
        
        Returns:
            list: Lista de divergências encontradas
        """
        divergencias = []
        
        try:
            # Verificar transações sem ativo
            transacoes_sem_ativo = Transacao.query.filter_by(
                usuario_id=usuario_id,
                ativo_id=None
            ).count()
            
            if transacoes_sem_ativo > 0:
                divergencias.append({
                    'tipo': 'TRANSACAO_SEM_ATIVO',
                    'severidade': 'ERROR',
                    'quantidade': transacoes_sem_ativo,
                    'mensagem': f"{transacoes_sem_ativo} transações sem ativo vinculado"
                })
            
            # Verificar transações com quantidade zero
            transacoes_zero = Transacao.query.filter_by(
                usuario_id=usuario_id
            ).filter(
                Transacao.quantidade == 0
            ).count()
            
            if transacoes_zero > 0:
                divergencias.append({
                    'tipo': 'TRANSACAO_QUANTIDADE_ZERO',
                    'severidade': 'WARNING',
                    'quantidade': transacoes_zero,
                    'mensagem': f"{transacoes_zero} transações com quantidade zero"
                })
            
            # Verificar duplicatas por hash_importacao
            duplicatas = db.session.query(
                Transacao.hash_importacao,
                func.count(Transacao.id).label('count')
            ).filter(
                Transacao.usuario_id == usuario_id,
                Transacao.hash_importacao.isnot(None)
            ).group_by(
                Transacao.hash_importacao
            ).having(
                func.count(Transacao.id) > 1
            ).all()
            
            if duplicatas:
                for hash_imp, count in duplicatas:
                    divergencias.append({
                        'tipo': 'TRANSACAO_DUPLICADA',
                        'severidade': 'WARNING',
                        'hash_importacao': hash_imp[:16] + '...',
                        'quantidade': count,
                        'mensagem': f"{count} transações com mesmo hash de importação"
                    })
            
            return divergencias
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")
            raise
    
    @staticmethod
    def verificar_ativo_especifico(usuario_id, ativo_id, corretora_id=None) -> Dict:
        """
        Verifica reconciliação de um ativo específico.
        
        Args:
            usuario_id (UUID): ID do usuário
            ativo_id (UUID): ID do ativo
            corretora_id (UUID, optional): ID da corretora (None = todas)
        
        Returns:
            dict: Detalhes da reconciliação do ativo
        """
        try:
            query = Posicao.query.filter_by(
                usuario_id=usuario_id,
                ativo_id=ativo_id
            )
            
            if corretora_id:
                query = query.filter_by(corretora_id=corretora_id)
            
            posicoes = query.all()
            
            resultado = {
                'ativo_id': str(ativo_id),
                'corretoras': [],
                'divergencias': []
            }
            
            for posicao in posicoes:
                # Calcular a partir de transações
                transacoes = Transacao.query.filter_by(
                    usuario_id=usuario_id,
                    ativo_id=ativo_id,
                    corretora_id=posicao.corretora_id
                ).order_by(Transacao.data_transacao).all()
                
                quantidade_calc = Decimal('0')
                for t in transacoes:
                    if t.tipo.value == 'compra':
                        quantidade_calc += t.quantidade
                    elif t.tipo.value == 'venda':
                        quantidade_calc -= t.quantidade
                
                corretora_info = {
                    'corretora_id': str(posicao.corretora_id),
                    'corretora_nome': posicao.corretora.nome if posicao.corretora else 'N/A',
                    'quantidade_posicao': float(posicao.quantidade),
                    'quantidade_calculada': float(quantidade_calc),
                    'diferenca': float(abs(posicao.quantidade - quantidade_calc)),
                    'status': 'OK' if abs(posicao.quantidade - quantidade_calc) <= ReconciliacaoService.TOLERANCIA else 'DIVERGENTE'
                }
                
                resultado['corretoras'].append(corretora_info)
                
                if corretora_info['status'] == 'DIVERGENTE':
                    resultado['divergencias'].append({
                        'tipo': 'QUANTIDADE',
                        'corretora': corretora_info['corretora_nome'],
                        'diferenca': corretora_info['diferenca']
                    })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar ativo específico: {e}")
            raise
