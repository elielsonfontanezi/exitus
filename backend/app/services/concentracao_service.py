# -*- coding: utf-8 -*-
"""
CONCENTRACAO-001 — Análise de concentração da carteira por ativo.

Métricas: top 1, top 5, índice HHI e alertas quando acima dos limites.
"""
from typing import Dict, List
from uuid import UUID

from app.services.portfolio_service import PortfolioService

# Limites de referência (percentual do patrimônio)
LIMITE_TOP1_PCT = 25.0
LIMITE_TOP5_PCT = 60.0
LIMITE_HHI = 2500.0


class ConcentracaoService:
    @staticmethod
    def calcular_concentracao(usuario_id: UUID) -> Dict:
        """Calcula concentração por ativo com HHI e alertas."""
        ativos: List[Dict] = []

        for _posicao, ativo, valor_brl in PortfolioService._iter_posicoes_valor_brl(usuario_id):
            if valor_brl <= 0:
                continue
            ativos.append({
                'ticker': ativo.ticker,
                'nome': ativo.nome or ativo.ticker,
                'valor': round(valor_brl, 2),
            })

        total = sum(a['valor'] for a in ativos)
        if total <= 0:
            return {
                'patrimonio_total': 0.0,
                'top1_percentual': 0.0,
                'top5_percentual': 0.0,
                'hhi': 0.0,
                'alertas': [],
                'ativos': [],
                'qtd_posicoes': 0,
                'concentrado': False,
            }

        ativos.sort(key=lambda x: x['valor'], reverse=True)
        for item in ativos:
            item['percentual'] = round(item['valor'] / total * 100, 2)

        top1 = ativos[0]['percentual']
        top5 = round(sum(a['percentual'] for a in ativos[:5]), 2)
        hhi = round(sum((a['percentual'] / 100) ** 2 for a in ativos) * 10000, 2)

        alertas = []
        if top1 > LIMITE_TOP1_PCT:
            alertas.append({
                'tipo': 'top1',
                'mensagem': f'Maior posição ({ativos[0]["ticker"]}) representa {top1:.1f}% da carteira (limite {LIMITE_TOP1_PCT:.0f}%)',
            })
        if top5 > LIMITE_TOP5_PCT:
            alertas.append({
                'tipo': 'top5',
                'mensagem': f'Top 5 ativos concentram {top5:.1f}% do patrimônio (limite {LIMITE_TOP5_PCT:.0f}%)',
            })
        if hhi > LIMITE_HHI:
            alertas.append({
                'tipo': 'hhi',
                'mensagem': f'Índice HHI {hhi:.0f} indica carteira concentrada (limite {LIMITE_HHI:.0f})',
            })

        return {
            'patrimonio_total': round(total, 2),
            'top1_percentual': top1,
            'top1_ticker': ativos[0]['ticker'],
            'top5_percentual': top5,
            'hhi': hhi,
            'limites': {
                'top1_pct': LIMITE_TOP1_PCT,
                'top5_pct': LIMITE_TOP5_PCT,
                'hhi': LIMITE_HHI,
            },
            'alertas': alertas,
            'ativos': ativos[:10],
            'qtd_posicoes': len(ativos),
            'concentrado': len(alertas) > 0,
        }
