# -*- coding: utf-8 -*-
"""
Exitus - Carteira Service
Serviços para dados consolidados da carteira
"""

from uuid import UUID
from typing import Dict
from decimal import Decimal
from app.models import MovimentacaoCaixa
from app.services.cambio_service import CambioService
import logging

logger = logging.getLogger(__name__)


class CarteiraService:
    """Serviço para gerenciar dados consolidados da carteira"""
    
    @staticmethod
    def get_saldo_caixa(usuario_id: UUID, moeda_exibicao: str = 'BRL') -> Dict:
        """
        Calcula saldo disponível em caixa do usuário.
        
        Args:
            usuario_id: ID do usuário
            moeda_exibicao: Moeda para exibição (BRL ou USD)
            
        Returns:
            Dict com saldo_brl, saldo_usd, moeda_exibicao, taxa_cambio
        """
        # Buscar todas as movimentações de caixa do usuário
        movimentacoes = MovimentacaoCaixa.query.filter_by(
            usuario_id=usuario_id
        ).all()
        
        saldo_brl = Decimal('0')
        saldo_usd = Decimal('0')
        
        for mov in movimentacoes:
            valor = Decimal(str(mov.valor))
            moeda = mov.moeda.upper()
            
            # Entrada positiva, saída negativa
            if mov.tipo_movimentacao in ['DEPOSITO', 'CREDITO', 'DIVIDENDO', 'JCP', 'RENDIMENTO']:
                multiplicador = Decimal('1')
            else:
                multiplicador = Decimal('-1')
            
            valor_final = valor * multiplicador
            
            # Acumular por moeda
            if moeda == 'BRL':
                saldo_brl += valor_final
            elif moeda == 'USD':
                saldo_usd += valor_final
            else:
                # Converter outras moedas para BRL
                valor_convertido = CambioService.converter_para_brl(valor_final, moeda)
                if valor_convertido:
                    saldo_brl += Decimal(str(valor_convertido))
        
        # Obter taxa de câmbio atual (fallback hardcoded por enquanto)
        taxa_dict = CambioService.get_taxa('USD', 'BRL')
        taxa_cambio = Decimal(str(taxa_dict['taxa'])) if taxa_dict else Decimal('5.46')
        
        # Converter USD para BRL se necessário
        saldo_usd_em_brl = saldo_usd * Decimal(str(taxa_cambio))
        
        return {
            'saldo_brl': float(saldo_brl),
            'saldo_usd': float(saldo_usd),
            'saldo_total_brl': float(saldo_brl + saldo_usd_em_brl),
            'moeda_exibicao': moeda_exibicao,
            'taxa_cambio': float(taxa_cambio)
        }
