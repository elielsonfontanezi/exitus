# -*- coding: utf-8 -*-
"""
Exitus - MovimentacaoCaixa Service
Service layer para gerenciamento de movimentações de caixa
"""

from app.database import db
from app.models import MovimentacaoCaixa, Corretora, Provento
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MovimentacaoCaixaService:
    """Service para operações de movimentação de caixa"""

    @staticmethod
    def get_all(usuario_id, page=1, per_page=50, filters=None):
        """
        Lista movimentações de caixa do usuário
        
        Args:
            usuario_id (UUID): ID do usuário
            page (int): Página atual
            per_page (int): Registros por página
            filters (dict): Filtros opcionais
        
        Returns:
            Pagination: Objeto de paginação
        """
        try:
            query = MovimentacaoCaixa.query.filter_by(usuario_id=usuario_id)
            
            query = query.options(
                joinedload(MovimentacaoCaixa.corretora),
                joinedload(MovimentacaoCaixa.corretora_destino),
                joinedload(MovimentacaoCaixa.provento)
            )
            
            if filters:
                if filters.get('corretora_id'):
                    query = query.filter(
                        or_(
                            MovimentacaoCaixa.corretora_id == filters['corretora_id'],
                            MovimentacaoCaixa.corretora_destino_id == filters['corretora_id']
                        )
                    )
                if filters.get('tipo_movimentacao'):
                    query = query.filter_by(tipo_movimentacao=filters['tipo_movimentacao'])
                if filters.get('data_inicio'):
                    query = query.filter(MovimentacaoCaixa.data_movimentacao >= filters['data_inicio'])
                if filters.get('data_fim'):
                    query = query.filter(MovimentacaoCaixa.data_movimentacao <= filters['data_fim'])
                if filters.get('moeda'):
                    query = query.filter_by(moeda=filters['moeda'])
            
            query = query.order_by(MovimentacaoCaixa.data_movimentacao.desc())
            return query.paginate(page=page, per_page=per_page, error_out=False)
            
        except Exception as e:
            logger.error(f"Erro ao listar movimentações: {e}")
            raise


    @staticmethod
    def get_by_id(movimentacao_id, usuario_id):
        """Busca movimentação por ID com validação de propriedade"""
        return MovimentacaoCaixa.query.filter_by(
            id=movimentacao_id,
            usuario_id=usuario_id
        ).options(
            joinedload(MovimentacaoCaixa.corretora),
            joinedload(MovimentacaoCaixa.corretora_destino),
            joinedload(MovimentacaoCaixa.provento)
        ).first()


    @staticmethod
    def create(usuario_id, data):
        """
        Cria nova movimentação de caixa
        
        Args:
            usuario_id (UUID): ID do usuário
            data (dict): Dados da movimentação
        
        Returns:
            MovimentacaoCaixa: Movimentação criada
        """
        try:
            # Validar corretora pertence ao usuário
            corretora = Corretora.query.filter_by(
                id=data['corretora_id'],
                usuario_id=usuario_id
            ).first()
            
            if not corretora:
                raise ValueError("Corretora não encontrada ou não pertence ao usuário")
            
            # Validar corretora destino se for transferência
            tipo = data.get('tipo_movimentacao', '').upper()
            if tipo in ['TRANSFERENCIA_ENVIADA', 'TRANSFERENCIA_RECEBIDA']:
                if not data.get('corretora_destino_id'):
                    raise ValueError("Transferência requer corretora de destino")
                
                corretora_destino = Corretora.query.filter_by(
                    id=data['corretora_destino_id'],
                    usuario_id=usuario_id
                ).first()
                
                if not corretora_destino:
                    raise ValueError("Corretora destino não encontrada")
            
            # Criar movimentação
            data['usuario_id'] = usuario_id
            movimentacao = MovimentacaoCaixa(**data)
            db.session.add(movimentacao)
            
            # Atualizar saldo da corretora
            MovimentacaoCaixaService._atualizar_saldo_corretora(
                corretora, 
                movimentacao.impacto_saldo
            )
            
            # Se for transferência, atualizar corretora destino
            if tipo == 'TRANSFERENCIA_ENVIADA':
                MovimentacaoCaixaService._atualizar_saldo_corretora(
                    corretora_destino,
                    movimentacao.valor
                )
            
            db.session.commit()
            
            logger.info(f"Movimentação criada: {movimentacao.id} - {tipo}")
            return movimentacao
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar movimentação: {e}")
            raise


    @staticmethod
    def _atualizar_saldo_corretora(corretora, valor):
        """Atualiza saldo da corretora"""
        corretora.saldo_atual += valor


    @staticmethod
    def update(movimentacao_id, usuario_id, data):
        """
        Atualiza movimentação de caixa
        
        Args:
            movimentacao_id (UUID): ID da movimentação
            usuario_id (UUID): ID do usuário
            data (dict): Dados a atualizar
        
        Returns:
            MovimentacaoCaixa: Movimentação atualizada
        """
        try:
            movimentacao = MovimentacaoCaixaService.get_by_id(movimentacao_id, usuario_id)
            
            if not movimentacao:
                raise ValueError("Movimentação não encontrada")
            
            # Reverter saldo anterior
            MovimentacaoCaixaService._atualizar_saldo_corretora(
                movimentacao.corretora,
                -movimentacao.impacto_saldo
            )
            
            # Atualizar campos permitidos
            campos_permitidos = [
                'tipo_movimentacao', 'valor', 'moeda', 
                'data_movimentacao', 'descricao', 'comprovante'
            ]
            
            for campo in campos_permitidos:
                if campo in data:
                    setattr(movimentacao, campo, data[campo])
            
            # Aplicar novo saldo
            MovimentacaoCaixaService._atualizar_saldo_corretora(
                movimentacao.corretora,
                movimentacao.impacto_saldo
            )
            
            db.session.commit()
            logger.info(f"Movimentação atualizada: {movimentacao_id}")
            return movimentacao
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar movimentação: {e}")
            raise


    @staticmethod
    def delete(movimentacao_id, usuario_id):
        """
        Deleta movimentação de caixa
        
        Args:
            movimentacao_id (UUID): ID da movimentação
            usuario_id (UUID): ID do usuário
        
        Returns:
            bool: True se deletado
        """
        try:
            movimentacao = MovimentacaoCaixaService.get_by_id(movimentacao_id, usuario_id)
            
            if not movimentacao:
                raise ValueError("Movimentação não encontrada")
            
            # Reverter saldo
            MovimentacaoCaixaService._atualizar_saldo_corretora(
                movimentacao.corretora,
                -movimentacao.impacto_saldo
            )
            
            db.session.delete(movimentacao)
            db.session.commit()
            
            logger.info(f"Movimentação deletada: {movimentacao_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar movimentação: {e}")
            raise


    @staticmethod
    def get_saldo_corretora(usuario_id, corretora_id):
        """
        Calcula saldo consolidado de uma corretora
        
        Args:
            usuario_id (UUID): ID do usuário
            corretora_id (UUID): ID da corretora
        
        Returns:
            dict: Saldo por moeda
        """
        try:
            movimentacoes = MovimentacaoCaixa.query.filter_by(
                usuario_id=usuario_id,
                corretora_id=corretora_id
            ).all()
            
            # Agrupar por moeda
            saldos = {}
            
            for m in movimentacoes:
                moeda = m.moeda
                if moeda not in saldos:
                    saldos[moeda] = Decimal('0')
                
                saldos[moeda] += m.impacto_saldo
            
            return {
                moeda: float(saldo)
                for moeda, saldo in saldos.items()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular saldo: {e}")
            raise


    @staticmethod
    def get_extrato(usuario_id, corretora_id=None, data_inicio=None, data_fim=None):
        """
        Gera extrato de movimentações
        
        Args:
            usuario_id (UUID): ID do usuário
            corretora_id (UUID, optional): Filtrar por corretora
            data_inicio (date, optional): Data inicial
            data_fim (date, optional): Data final
        
        Returns:
            list: Lista de movimentações com saldo acumulado
        """
        try:
            query = MovimentacaoCaixa.query.filter_by(usuario_id=usuario_id)
            
            if corretora_id:
                query = query.filter_by(corretora_id=corretora_id)
            
            if data_inicio:
                query = query.filter(MovimentacaoCaixa.data_movimentacao >= data_inicio)
            
            if data_fim:
                query = query.filter(MovimentacaoCaixa.data_movimentacao <= data_fim)
            
            query = query.options(
                joinedload(MovimentacaoCaixa.corretora)
            ).order_by(MovimentacaoCaixa.data_movimentacao.asc())
            
            movimentacoes = query.all()
            
            # Calcular saldo acumulado
            saldo_acumulado = Decimal('0')
            extrato = []
            
            for m in movimentacoes:
                saldo_acumulado += m.impacto_saldo
                
                extrato.append({
                    'id': str(m.id),
                    'data': m.data_movimentacao.isoformat(),
                    'tipo': m.tipo_movimentacao.value,
                    'descricao': m.descricao or m.tipo_movimentacao.value,
                    'valor': float(m.valor),
                    'impacto': float(m.impacto_saldo),
                    'saldo_acumulado': float(saldo_acumulado),
                    'moeda': m.moeda,
                    'corretora': m.corretora.nome
                })
            
            return extrato
            
        except Exception as e:
            logger.error(f"Erro ao gerar extrato: {e}")
            raise
