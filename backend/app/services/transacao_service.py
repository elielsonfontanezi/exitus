# -*- coding: utf-8 -*-
"""Exitus - Transacao Service - Lógica de negócio"""

from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import and_, or_, func
from app.database import db
from app.models import Transacao, TipoTransacao, Ativo, Corretora

class TransacaoService:
    """Serviço para operações de transações"""
    
    @staticmethod
    def get_all(usuario_id, page=1, per_page=20, tipo=None, ativo_id=None, 
                corretora_id=None, data_inicio=None, data_fim=None):
        """
        Lista transações do usuário com paginação e filtros.
        
        Args:
            usuario_id: ID do usuário (multi-tenant)
            page: Número da página
            per_page: Itens por página
            tipo: Filtro por tipo (COMPRA, VENDA, etc)
            ativo_id: Filtro por ativo
            corretora_id: Filtro por corretora
            data_inicio: Data inicial
            data_fim: Data final
        """
        query = Transacao.query.filter_by(usuario_id=usuario_id)
        
        # Filtros
        if tipo:
            query = query.filter_by(tipo=TipoTransacao[tipo.upper()])
        
        if ativo_id:
            query = query.filter_by(ativo_id=ativo_id)
        
        if corretora_id:
            query = query.filter_by(corretora_id=corretora_id)
        
        if data_inicio:
            query = query.filter(Transacao.data_transacao >= data_inicio)
        
        if data_fim:
            query = query.filter(Transacao.data_transacao <= data_fim)
        
        # Ordenar por data (mais recentes primeiro)
        query = query.order_by(Transacao.data_transacao.desc())
        
        # Paginação
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(transacao_id, usuario_id):
        """Busca transação por ID (com verificação de ownership)"""
        return Transacao.query.filter_by(
            id=transacao_id,
            usuario_id=usuario_id
        ).first()
    
    @staticmethod
    def create(usuario_id, data):
        """
        Cria nova transação.
        
        Args:
            usuario_id: ID do usuário
            data: Dict com tipo, ativo_id, corretora_id, quantidade, preco, etc
        """
        # Verificar se ativo existe
        ativo = Ativo.query.get(data['ativo_id'])
        if not ativo:
            raise ValueError("Ativo não encontrado")
        
        # Verificar se corretora existe e pertence ao usuário
        corretora = Corretora.query.filter_by(
            id=data['corretora_id'],
            usuario_id=usuario_id
        ).first()
        
        if not corretora:
            raise ValueError("Corretora não encontrada ou não pertence ao usuário")
        
        # Calcular valores
        quantidade = Decimal(str(data['quantidade']))
        preco_unitario = Decimal(str(data['preco_unitario']))
        valor_total = quantidade * preco_unitario
        
        # Somar custos
        taxa_corretagem = Decimal(str(data.get('taxa_corretagem', 0)))
        taxa_liquidacao = Decimal(str(data.get('taxa_liquidacao', 0)))
        emolumentos = Decimal(str(data.get('emolumentos', 0)))
        imposto = Decimal(str(data.get('imposto', 0)))
        outros_custos = Decimal(str(data.get('outros_custos', 0)))
        
        custos_totais = (taxa_corretagem + taxa_liquidacao + emolumentos + 
                        imposto + outros_custos)
        
        # Valor líquido (compra: total + custos, venda: total - custos)
        tipo = TipoTransacao[data['tipo'].upper()]
        if tipo == TipoTransacao.COMPRA:
            valor_liquido = valor_total + custos_totais
        elif tipo == TipoTransacao.VENDA:
            valor_liquido = valor_total - custos_totais
        else:
            valor_liquido = valor_total  # Dividendos, JCP, etc
        
        transacao = Transacao(
            usuario_id=usuario_id,
            tipo=tipo,
            ativo_id=data['ativo_id'],
            corretora_id=data['corretora_id'],
            data_transacao=data['data_transacao'],
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            valor_total=valor_total,
            taxa_corretagem=taxa_corretagem,
            taxa_liquidacao=taxa_liquidacao,
            emolumentos=emolumentos,
            imposto=imposto,
            outros_custos=outros_custos,
            custos_totais=custos_totais,
            valor_liquido=valor_liquido,
            observacoes=data.get('observacoes')
        )
        
        db.session.add(transacao)
        db.session.commit()
        return transacao
    
    @staticmethod
    def update(transacao_id, usuario_id, data):
        """
        Atualiza transação.
        
        Args:
            transacao_id: ID da transação
            usuario_id: ID do usuário
            data: Dict com campos a atualizar
        """
        transacao = Transacao.query.filter_by(
            id=transacao_id,
            usuario_id=usuario_id
        ).first()
        
        if not transacao:
            raise ValueError("Transação não encontrada")
        
        # Atualizar campos permitidos
        if 'data_transacao' in data:
            transacao.data_transacao = data['data_transacao']
        
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
        
        if 'observacoes' in data:
            transacao.observacoes = data['observacoes']
        
        # Recalcular valores
        transacao.valor_total = transacao.quantidade * transacao.preco_unitario
        transacao.custos_totais = (transacao.taxa_corretagem + transacao.taxa_liquidacao + 
                                   transacao.emolumentos + transacao.imposto + 
                                   transacao.outros_custos)
        
        if transacao.tipo == TipoTransacao.COMPRA:
            transacao.valor_liquido = transacao.valor_total + transacao.custos_totais
        elif transacao.tipo == TipoTransacao.VENDA:
            transacao.valor_liquido = transacao.valor_total - transacao.custos_totais
        else:
            transacao.valor_liquido = transacao.valor_total
        
        db.session.commit()
        return transacao
    
    @staticmethod
    def delete(transacao_id, usuario_id):
        """Deleta transação"""
        transacao = Transacao.query.filter_by(
            id=transacao_id,
            usuario_id=usuario_id
        ).first()
        
        if not transacao:
            raise ValueError("Transação não encontrada")
        
        db.session.delete(transacao)
        db.session.commit()
        return True
    
    @staticmethod
    def get_resumo_por_ativo(usuario_id, ativo_id):
        """
        Retorna resumo de transações de um ativo.
        
        Returns:
            Dict com quantidade_total, valor_investido, preco_medio
        """
        transacoes = Transacao.query.filter_by(
            usuario_id=usuario_id,
            ativo_id=ativo_id
        ).all()
        
        quantidade_comprada = Decimal('0')
        quantidade_vendida = Decimal('0')
        valor_investido = Decimal('0')
        valor_vendido = Decimal('0')
        
        for t in transacoes:
            if t.tipo == TipoTransacao.COMPRA:
                quantidade_comprada += t.quantidade
                valor_investido += t.valor_liquido
            elif t.tipo == TipoTransacao.VENDA:
                quantidade_vendida += t.quantidade
                valor_vendido += t.valor_liquido
        
        quantidade_atual = quantidade_comprada - quantidade_vendida
        preco_medio = (valor_investido / quantidade_comprada 
                      if quantidade_comprada > 0 else Decimal('0'))
        
        return {
            "quantidade_total": quantidade_atual,
            "quantidade_comprada": quantidade_comprada,
            "quantidade_vendida": quantidade_vendida,
            "valor_investido": valor_investido,
            "valor_vendido": valor_vendido,
            "preco_medio": preco_medio
        }
