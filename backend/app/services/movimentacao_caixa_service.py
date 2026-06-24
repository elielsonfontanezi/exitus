# -*- coding: utf-8 -*-
"""
Exitus - MovimentacaoCaixa Service M3.2 (Corrigido)
"""

from app.database import db
from app.models import MovimentacaoCaixa, Corretora
from app.models.movimentacao_caixa import TipoMovimentacao
from app.utils.exceptions import NotFoundError
from app.services.auditoria_service import AuditoriaService
from app.utils.tenant import filter_by_assessora, get_current_assessora_id
from decimal import Decimal
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

class MovimentacaoCaixaService:
    @staticmethod
    def get_all(usuario_id, page=1, per_page=50, filters=None):
        try:
            if filters is None:
                filters = {}

            query = MovimentacaoCaixa.query.filter_by(usuario_id=usuario_id)
            query = filter_by_assessora(query, MovimentacaoCaixa)

            if filters.get('corretora_id'):
                query = query.filter_by(corretora_id=filters['corretora_id'])
            if filters.get('tipo_movimentacao'):
                query = query.filter_by(tipo_movimentacao=filters['tipo_movimentacao'])
            if filters.get('moeda'):
                query = query.filter_by(moeda=filters['moeda'])
            if filters.get('data_inicio'):
                query = query.filter(MovimentacaoCaixa.data_movimentacao >= filters['data_inicio'])
            if filters.get('data_fim'):
                query = query.filter(MovimentacaoCaixa.data_movimentacao <= filters['data_fim'])

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
                raise NotFoundError("Corretora não encontrada")

            # Normalizar tipo_movimentacao para enum
            tipo_mov = data['tipo_movimentacao']
            if isinstance(tipo_mov, str):
                tipo_mov = TipoMovimentacao(tipo_mov)

            # Criar objeto
            nova_mov = MovimentacaoCaixa(
                id=str(uuid4()),
                usuario_id=usuario_id,
                assessora_id=get_current_assessora_id(),
                corretora_id=data['corretora_id'],
                tipo_movimentacao=tipo_mov,
                valor=data['valor'],
                data_movimentacao=data['data_movimentacao'],
                descricao=data.get('descricao', ''),
                provento_id=data.get('provento_id') # Opcional
            )
            
            db.session.add(nova_mov)
            db.session.commit()
            db.session.refresh(nova_mov)
            
            # Auditoria
            AuditoriaService.registrar_create(
                usuario_id=usuario_id,
                entidade='MovimentacaoCaixa',
                entidade_id=nova_mov.id,
                dados_depois=nova_mov.to_dict()
            )
            
            return nova_mov
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar movimentação: {e}")
            raise

    @staticmethod
    def get_saldo(usuario_id, corretora_id):
        """Calcula saldo somando movimentações (simples)"""
        try:
            query = MovimentacaoCaixa.query.filter_by(
                usuario_id=usuario_id, 
                corretora_id=corretora_id
            )
            query = filter_by_assessora(query, MovimentacaoCaixa)
            movimentacoes = query.all()
            
            saldo = Decimal('0.0')
            for m in movimentacoes:
                saldo += m.impacto_saldo()
            
            return float(saldo)
        except Exception as e:
            logger.error(f"Erro ao calcular saldo: {e}")
            raise
