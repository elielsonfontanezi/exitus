# -*- coding: utf-8 -*-
"""
Exitus - MovimentacaoCaixa Service M3.2 (Corrigido)
"""

from app.database import db
from app.models import MovimentacaoCaixa, Corretora
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from decimal import Decimal
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

class MovimentacaoCaixaService:
    @staticmethod
    def get_all(usuario_id, page=1, per_page=50, corretora_id=None, data_inicio=None, data_fim=None):
        try:
            query = MovimentacaoCaixa.query.filter_by(usuario_id=usuario_id)

            if corretora_id:
                query = query.filter_by(corretora_id=corretora_id)
            if data_inicio:
                query = query.filter(MovimentacaoCaixa.data_movimentacao >= data_inicio)
            if data_fim:
                query = query.filter(MovimentacaoCaixa.data_movimentacao <= data_fim)

            query = query.order_by(MovimentacaoCaixa.data_movimentacao.desc())
            return query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            logger.error(f"Erro ao listar movimentações: {e}")
            raise

    @staticmethod
    def create(usuario_id, data):
        try:
            # Validar se corretora existe e pertence ao usuário
            corretora = Corretora.query.filter_by(id=data['corretora_id'], usuario_id=usuario_id).first()
            if not corretora:
                raise ValueError("Corretora não encontrada")

            # Criar objeto
            nova_mov = MovimentacaoCaixa(
                id=str(uuid4()),
                usuario_id=usuario_id,
                corretora_id=data['corretora_id'],
                tipo_movimentacao=data['tipo_movimentacao'], # String ou Enum
                valor=data['valor'],
                data_movimentacao=data['data_movimentacao'],
                descricao=data.get('descricao', ''),
                provento_id=data.get('provento_id') # Opcional
            )
            
            db.session.add(nova_mov)
            db.session.commit()
            return nova_mov
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar movimentação: {e}")
            raise

    @staticmethod
    def get_saldo(usuario_id, corretora_id):
        """Calcula saldo somando movimentações (simples)"""
        try:
            movimentacoes = MovimentacaoCaixa.query.filter_by(
                usuario_id=usuario_id, 
                corretora_id=corretora_id
            ).all()
            
            saldo = Decimal('0.0')
            for m in movimentacoes:
                # Lógica simples: Depósito/Dividendo/Venda (+) | Saque/Compra (-)
                tipo = str(m.tipo_movimentacao).upper()
                valor = Decimal(str(m.valor))
                
                if tipo in ['DEPOSITO', 'DIVIDENDO', 'JCP', 'VENDA', 'BONIFICACAO']:
                    saldo += valor
                elif tipo in ['SAQUE', 'COMPRA', 'TAXA']:
                    saldo -= valor
            
            return float(saldo)
        except Exception as e:
            logger.error(f"Erro ao calcular saldo: {e}")
            raise
