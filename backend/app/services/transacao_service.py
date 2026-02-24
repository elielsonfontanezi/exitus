# -- coding: utf-8 --
# Exitus - Transacao Service
# Fix batch: TRX-002, TRX-003, TRX-004, TRX-007

import logging
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import joinedload

from app.database import db
from app.models import Transacao, Ativo, Corretora

logger = logging.getLogger(__name__)


class TransacaoService:

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------
    @staticmethod
    def getall(usuario_id, page=1, perpage=20,
               tipo=None, ativo_id=None, corretora_id=None,
               data_inicio=None, data_fim=None):
        """Lista transações do usuário com filtros opcionais"""
        try:
            query = (
                Transacao.query
                .filter_by(usuario_id=usuario_id)
                .options(
                    joinedload(Transacao.ativo),
                    joinedload(Transacao.corretora),
                )
            )
            if tipo:
                query = query.filter(
                    Transacao.tipo.in_([tipo.upper()])
                )
            if ativo_id:
                query = query.filter_by(ativo_id=ativo_id)
            if corretora_id:
                query = query.filter_by(corretora_id=corretora_id)
            if data_inicio:
                query = query.filter(Transacao.data_transacao >= data_inicio)
            if data_fim:
                query = query.filter(Transacao.data_transacao <= data_fim)

            query = query.order_by(Transacao.data_transacao.desc())
            return query.paginate(page=page, per_page=perpage, error_out=False)
        except Exception as e:
            logger.error(f"Erro ao listar transações: {e}")
            raise

    # ------------------------------------------------------------------
    # GET BY ID
    # ------------------------------------------------------------------
    @staticmethod
    def get_by_id(transacao_id, usuario_id):
        """
        Busca transação por ID com isolamento de ownership.

        Raises:
            ValueError:      ID não encontrado em nenhum usuário  → 404
            PermissionError: ID existe mas pertence a outro user  → 403
        """
        # Busca sem filtro de usuário para distinguir 404 vs 403
        transacao = (
            Transacao.query
            .options(
                joinedload(Transacao.ativo),
                joinedload(Transacao.corretora),
            )
            .get(transacao_id)
        )

        if transacao is None:
            raise ValueError(f"Transação {transacao_id} não encontrada")

        if str(transacao.usuario_id) != str(usuario_id):
            raise PermissionError("Acesso negado: transação pertence a outro usuário")

        return transacao

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    @staticmethod
    def create(usuario_id, data):
        """Cria nova transação com cálculos automáticos"""
        try:
            # Valida ativo e corretora (existência básica)
            ativo = Ativo.query.get(data['ativo_id'])
            if not ativo:
                raise ValueError("Ativo não encontrado")

            corretora = Corretora.query.filter_by(
                id=data['corretora_id'], usuario_id=usuario_id
            ).first()
            if not corretora:
                raise ValueError("Corretora não encontrada ou não pertence ao usuário")

            quantidade      = Decimal(str(data['quantidade']))
            preco_unitario  = Decimal(str(data['preco_unitario']))
            taxa_corretagem = Decimal(str(data.get('taxa_corretagem', 0)))
            taxa_liquidacao = Decimal(str(data.get('taxa_liquidacao', 0)))
            emolumentos     = Decimal(str(data.get('emolumentos', 0)))
            imposto         = Decimal(str(data.get('imposto', 0)))
            outros_custos   = Decimal(str(data.get('outros_custos', 0)))

            valor_total   = quantidade * preco_unitario
            custos_totais = (
                taxa_corretagem + taxa_liquidacao
                + emolumentos + outros_custos
            )

            tipo = data['tipo'].lower()
            if tipo in ('compra',):
                valor_liquido = valor_total + custos_totais
            elif tipo in ('venda',):
                valor_liquido = valor_total - custos_totais
            else:
                # dividendo, jcp, aluguel, etc.
                valor_liquido = valor_total - imposto

            transacao = Transacao(
                usuario_id      = usuario_id,
                tipo            = data['tipo'].lower(),
                ativo_id        = data['ativo_id'],
                corretora_id    = data['corretora_id'],
                data_transacao  = data['data_transacao'],
                quantidade      = quantidade,
                preco_unitario  = preco_unitario,
                valor_total     = valor_total,
                taxa_corretagem = taxa_corretagem,
                taxa_liquidacao = taxa_liquidacao,
                emolumentos     = emolumentos,
                imposto         = imposto,
                outros_custos   = outros_custos,
                custos_totais   = custos_totais,
                valor_liquido   = valor_liquido,
                observacoes     = data.get('observacoes'),
            )
            db.session.add(transacao)
            db.session.commit()
            db.session.refresh(transacao)
            return transacao
        except (ValueError, PermissionError):
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar transação: {e}")
            raise

    # ------------------------------------------------------------------
    # UPDATE
    # TRX-002: lançar PermissionError (→ 403) quando TRX pertence a
    #           outro usuário, em vez de ValueError (→ 400/404).
    # TRX-003: lançar ValueError com mensagem clara quando ID não existe
    #           (→ 404), separado do caso de permissão.
    # ------------------------------------------------------------------
    @staticmethod
    def update(transacao_id, usuario_id, data):
        """
        Atualiza transação com recalculo automático de valores.

        Raises:
            ValueError:      transação não existe → 404
            PermissionError: transação de outro usuário → 403
        """
        # TRX-003: busca sem filtro de usuário → 404 real
        transacao = Transacao.query.get(transacao_id)
        if transacao is None:
            raise ValueError(f"Transação {transacao_id} não encontrada")   # → 404

        # TRX-002: ownership check → 403
        if str(transacao.usuario_id) != str(usuario_id):
            raise PermissionError("Acesso negado: transação pertence a outro usuário")  # → 403

        try:
            if 'quantidade' in data:
                transacao.quantidade = Decimal(str(data['quantidade']))
            if 'preco_unitario' in data:
                transacao.preco_unitario = Decimal(str(data['preco_unitario']))
            if 'taxa_corretagem' in data:
                transacao.taxa_corretagem = Decimal(str(data['taxa_corretagem']))
            if 'taxa_liquidacao' in data:
                transacao.taxa_liquidacao = Decimal(str(data['taxa_liquidacao']))
            if 'emolumentos' in data:
                transacao.emolumentos = Decimal(str(data['emolumentos']))
            if 'imposto' in data:
                transacao.imposto = Decimal(str(data['imposto']))
            if 'outros_custos' in data:
                transacao.outros_custos = Decimal(str(data['outros_custos']))
            if 'data_transacao' in data:
                transacao.data_transacao = data['data_transacao']
            if 'observacoes' in data:
                transacao.observacoes = data['observacoes']

            # Recalcula totais
            transacao.valor_total = transacao.quantidade * transacao.preco_unitario
            transacao.custos_totais = (
                transacao.taxa_corretagem + transacao.taxa_liquidacao
                + transacao.emolumentos + transacao.outros_custos
            )
            tipo = transacao.tipo.value.lower()
            if tipo == 'compra':
                transacao.valor_liquido = transacao.valor_total + transacao.custos_totais
            elif tipo == 'venda':
                transacao.valor_liquido = transacao.valor_total - transacao.custos_totais
            else:
                transacao.valor_liquido = transacao.valor_total - transacao.imposto

            transacao.updated_at = datetime.utcnow()
            db.session.commit()
            db.session.refresh(transacao)
            return transacao
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar transação: {e}")
            raise

    # ------------------------------------------------------------------
    # DELETE
    # TRX-004: lançar PermissionError (→ 403) quando TRX pertence a
    #           outro usuário, em vez de ValueError (→ 404).
    # ------------------------------------------------------------------
    @staticmethod
    def delete(transacao_id, usuario_id):
        """
        Deleta transação.

        Raises:
            ValueError:      transação não existe → 404
            PermissionError: transação de outro usuário → 403
        """
        transacao = Transacao.query.get(transacao_id)
        if transacao is None:
            raise ValueError(f"Transação {transacao_id} não encontrada")   # → 404

        # TRX-004: ownership check → 403
        if str(transacao.usuario_id) != str(usuario_id):
            raise PermissionError("Acesso negado: transação pertence a outro usuário")  # → 403

        try:
            db.session.delete(transacao)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar transação: {e}")
            raise

    # ------------------------------------------------------------------
    # RESUMO POR ATIVO
    # TRX-007: antes retornava 200 com dados zerados para ativo_id
    #           inexistente. Agora valida o ativo e lança ValueError → 404.
    # ------------------------------------------------------------------
    @staticmethod
    def get_resumo_por_ativo(usuario_id, ativo_id):
        """
        Retorna resumo agregado de transações de um ativo.

        Raises:
            ValueError: ativo_id não existe no catálogo → 404
        """
        # TRX-007: valida existência do ativo antes de qualquer cálculo
        ativo = Ativo.query.get(ativo_id)
        if not ativo:
            raise ValueError(f"Ativo {ativo_id} não encontrado")   # → 404

        transacoes = (
            Transacao.query
            .filter_by(usuario_id=usuario_id, ativo_id=ativo_id)
            .order_by(Transacao.data_transacao.asc())
            .all()
        )

        qtd_comprada  = Decimal('0')
        qtd_vendida   = Decimal('0')
        valor_compras = Decimal('0')
        valor_vendas  = Decimal('0')
        custos_total  = Decimal('0')

        for t in transacoes:
            tipo = t.tipo.value.lower()
            if tipo == 'compra':
                qtd_comprada  += t.quantidade
                valor_compras += t.valor_total
                custos_total  += t.custos_totais
            elif tipo == 'venda':
                qtd_vendida  += t.quantidade
                valor_vendas += t.valor_total
                custos_total += t.custos_totais

        qtd_total  = qtd_comprada - qtd_vendida
        investido  = valor_compras - valor_vendas
        preco_medio = (
            (valor_compras / qtd_comprada)
            if qtd_comprada > 0 else Decimal('0')
        )

        return {
            'ativo_id':       str(ativo_id),
            'ticker':         ativo.ticker,
            'qtd_comprada':   float(qtd_comprada),
            'qtd_vendida':    float(qtd_vendida),
            'qtd_total':      float(qtd_total),
            'preco_medio':    float(round(preco_medio, 6)),
            'valor_investido': float(round(investido, 2)),
            'custos_totais':  float(round(custos_total, 2)),
            'total_transacoes': len(transacoes),
        }
