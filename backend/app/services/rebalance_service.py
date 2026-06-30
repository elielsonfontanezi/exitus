# -*- coding: utf-8 -*-
"""
Exitus - RebalanceService — REBALANCE-001

Fonte única para metas de alocação, cálculo de desvios e sugestões de rebalanceamento.
Granularidade MVP: por classe (renda_variavel / renda_fixa / cripto).

Fluxo:
  obter_metas() → metas persistidas ou defaults vazios
  salvar_metas() → upsert com validação de soma ≤ 100%
  calcular_desvio() → alocação atual (PortfolioService) vs metas
  sugerir_rebalanceamento() → lista de ações comprar/vender por classe
"""
import logging
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import List, Dict

from app.database import db
from app.models.meta_alocacao import MetaAlocacao, CLASSES_VALIDAS
from app.models.posicao import Posicao
# Importação tardia dentro do método para evitar circular import com portfolio_service

logger = logging.getLogger(__name__)

_LABEL = {
    'renda_variavel': 'Renda Variável',
    'renda_fixa': 'Renda Fixa',
    'cripto': 'Criptoativos',
}


class RebalanceService:

    # ------------------------------------------------------------------
    # Metas
    # ------------------------------------------------------------------

    @staticmethod
    def obter_metas(usuario_id: UUID) -> List[Dict]:
        """
        Retorna metas do usuário para as 3 classes.
        Classes sem meta registrada retornam percentual_target=0.
        """
        registros = MetaAlocacao.query.filter_by(usuario_id=usuario_id).all()
        por_classe = {r.classe: r for r in registros}

        resultado = []
        for classe in CLASSES_VALIDAS:
            if classe in por_classe:
                resultado.append(por_classe[classe].to_dict())
            else:
                resultado.append({
                    'usuario_id': str(usuario_id),
                    'classe': classe,
                    'percentual_target': 0.0,
                    'tolerancia_pct': 2.0,
                    'updated_at': None,
                })
        return resultado

    @staticmethod
    def salvar_metas(usuario_id: UUID, metas: List[Dict],
                     assessora_id: UUID = None) -> List[Dict]:
        """
        Upsert das metas por classe.
        Valida soma ≤ 100% antes de persistir.

        Args:
            usuario_id: UUID do usuário
            metas: lista de {classe, percentual_target, tolerancia_pct?}
            assessora_id: UUID da assessora (multi-tenant)
        """
        soma = sum(float(m.get('percentual_target', 0)) for m in metas)
        if soma > 100:
            raise ValueError(
                f"Soma dos percentuais ({soma:.1f}%) não pode exceder 100%"
            )

        salvos = []
        for item in metas:
            classe = item['classe']
            if classe not in CLASSES_VALIDAS:
                raise ValueError(f"Classe inválida: {classe}")

            registro = MetaAlocacao.query.filter_by(
                usuario_id=usuario_id, classe=classe
            ).first()

            if registro:
                registro.percentual_target = Decimal(str(item['percentual_target']))
                registro.tolerancia_pct = Decimal(str(item.get('tolerancia_pct', 2.0)))
                registro.updated_at = datetime.utcnow()
            else:
                registro = MetaAlocacao(
                    usuario_id=usuario_id,
                    assessora_id=assessora_id,
                    classe=classe,
                    percentual_target=Decimal(str(item['percentual_target'])),
                    tolerancia_pct=Decimal(str(item.get('tolerancia_pct', 2.0))),
                )
                db.session.add(registro)

            salvos.append(registro)

        db.session.commit()
        return [r.to_dict() for r in salvos]

    # ------------------------------------------------------------------
    # Desvio
    # ------------------------------------------------------------------

    @staticmethod
    def calcular_desvio(usuario_id: UUID) -> Dict:
        """
        Compara alocação real (PortfolioService.get_alocacao) com metas.

        Retorno:
        {
          "patrimonio_total": float,
          "total_posicoes": int,
          "alocacao_atual": {classe: pct},
          "alocacao_target": {classe: pct},
          "desvios": {classe: pp_desvio},
          "classes": [
            {
              "classe": str,
              "label": str,
              "percentual_atual": float,
              "percentual_target": float,
              "tolerancia_pct": float,
              "valor_atual": float,
              "valor_target": float,
              "valor_ajuste": float,   # negativo=vender, positivo=comprar
              "desvio_pct": float,     # atual - target (positivo=sobrealoc)
              "precisa_rebalancear": bool,
            }
          ]
        }
        """
        from app.services.portfolio_service import PortfolioService

        alocacao_atual = PortfolioService.get_alocacao(usuario_id)
        metas = RebalanceService.obter_metas(usuario_id)
        meta_map = {m['classe']: m for m in metas}

        patrimonio_total = sum(
            v['valor'] for v in alocacao_atual.values()
            if isinstance(v, dict) and 'valor' in v
        )
        total_posicoes = Posicao.query.filter_by(usuario_id=usuario_id).count()

        classes_detalhe = []
        alocacao_atual_pct = {}
        alocacao_target_pct = {}
        desvios = {}

        for classe in CLASSES_VALIDAS:
            atual = alocacao_atual.get(classe, {'valor': 0.0, 'percentual': 0.0})
            pct_atual = float(atual.get('percentual', 0.0))
            valor_atual = float(atual.get('valor', 0.0))

            meta = meta_map.get(classe, {})
            pct_target = float(meta.get('percentual_target', 0.0))
            tolerancia = float(meta.get('tolerancia_pct', 2.0))

            valor_target = patrimonio_total * pct_target / 100.0 if patrimonio_total > 0 else 0.0
            valor_ajuste = valor_target - valor_atual  # positivo=comprar, negativo=vender
            desvio_pct = pct_atual - pct_target        # positivo=sobrealoc

            precisa_rebalancear = abs(desvio_pct) > tolerancia

            alocacao_atual_pct[classe] = round(pct_atual, 2)
            alocacao_target_pct[classe] = round(pct_target, 2)
            desvios[classe] = round(desvio_pct, 2)

            classes_detalhe.append({
                'classe': classe,
                'label': _LABEL.get(classe, classe),
                'percentual_atual': round(pct_atual, 2),
                'percentual_target': round(pct_target, 2),
                'tolerancia_pct': round(tolerancia, 2),
                'valor_atual': round(valor_atual, 2),
                'valor_target': round(valor_target, 2),
                'valor_ajuste': round(valor_ajuste, 2),
                'desvio_pct': round(desvio_pct, 2),
                'precisa_rebalancear': precisa_rebalancear,
            })

        return {
            'patrimonio_total': round(patrimonio_total, 2),
            'total_posicoes': total_posicoes,
            'alocacao_atual': alocacao_atual_pct,
            'alocacao_target': alocacao_target_pct,
            'desvios': desvios,
            'classes': classes_detalhe,
        }

    # ------------------------------------------------------------------
    # Sugestões
    # ------------------------------------------------------------------

    @staticmethod
    def sugerir_rebalanceamento(usuario_id: UUID) -> Dict:
        """
        Retorna lista de ações sugeridas (comprar/vender por classe).
        Inclui apenas classes com desvio além da tolerância.
        """
        desvio = RebalanceService.calcular_desvio(usuario_id)

        acoes = []
        for cls in desvio['classes']:
            if not cls['precisa_rebalancear']:
                continue
            direcao = 'vender' if cls['valor_ajuste'] < 0 else 'comprar'
            acoes.append({
                'classe': cls['classe'],
                'label': cls['label'],
                'direcao': direcao,
                'valor_brl': round(abs(cls['valor_ajuste']), 2),
                'desvio_pct': cls['desvio_pct'],
                'percentual_atual': cls['percentual_atual'],
                'percentual_target': cls['percentual_target'],
            })

        # ordenar: maior desvio absoluto primeiro
        acoes.sort(key=lambda x: abs(x['desvio_pct']), reverse=True)

        classes_fora = [c['classe'] for c in desvio['classes'] if c['precisa_rebalancear']]

        return {
            'patrimonio_total': desvio['patrimonio_total'],
            'acoes': acoes,
            'total_acoes': len(acoes),
            'classes_fora_tolerancia': classes_fora,
            'carteira_balanceada': len(acoes) == 0,
            'resumo': (
                'Carteira balanceada.' if len(acoes) == 0
                else f"{len(acoes)} classe(s) fora da tolerância: "
                     + ', '.join(_LABEL.get(c, c) for c in classes_fora)
            ),
        }
