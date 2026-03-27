# -*- coding: utf-8 -*-
"""
Exitus - Service de Cálculos RF e FII (RFCALC-001)
Duration (Macaulay, Modified), YTM (Newton-Raphson), FFO, AFFO, P/FFO
"""

from datetime import date, datetime
from decimal import Decimal


class RFCalcService:
    """Cálculos avançados de Renda Fixa e FII/REIT"""

    # ================================================================
    # RENDA FIXA
    # ================================================================

    @staticmethod
    def calcular_fluxos_cupom(valor_nominal, taxa_cupom, frequencia_anual, periodos):
        """
        Gera lista de fluxos de caixa de um título com cupons.

        Args:
            valor_nominal (float): Valor de face do título
            taxa_cupom (float): Taxa de cupom anual (ex: 0.105 = 10,5%)
            frequencia_anual (int): Cupons por ano (1=anual, 2=semestral, 4=trimestral)
            periodos (int): Número total de períodos até o vencimento

        Returns:
            list[float]: Fluxos de caixa por período (último inclui devolução do principal)
        """
        cupom_por_periodo = (valor_nominal * taxa_cupom) / frequencia_anual
        fluxos = [cupom_por_periodo] * periodos
        fluxos[-1] += valor_nominal  # Devolução do principal no vencimento
        return fluxos

    @staticmethod
    def calcular_periodos(data_hoje, data_vencimento, frequencia_anual=1):
        """
        Calcula número de períodos restantes até o vencimento.

        Args:
            data_hoje (date): Data de referência
            data_vencimento (date): Data de vencimento do título
            frequencia_anual (int): Períodos por ano

        Returns:
            int: Número de períodos restantes (mínimo 1)
        """
        if isinstance(data_hoje, datetime):
            data_hoje = data_hoje.date()
        if isinstance(data_vencimento, datetime):
            data_vencimento = data_vencimento.date()

        dias_restantes = (data_vencimento - data_hoje).days
        anos_restantes = dias_restantes / 365.25
        periodos = max(1, round(anos_restantes * frequencia_anual))
        return periodos

    @staticmethod
    def duration_macaulay(preco_mercado, fluxos, taxa_desconto_periodo):
        """
        Calcula Duration de Macaulay.

        Fórmula: D = Σ[t × PV(CFt)] / Preço
        Onde PV(CFt) = CFt / (1 + y)^t

        Args:
            preco_mercado (float): Preço atual de mercado do título
            fluxos (list[float]): Fluxos de caixa por período
            taxa_desconto_periodo (float): Taxa de desconto por período (YTM / frequência)

        Returns:
            float: Duration de Macaulay em períodos
        """
        if preco_mercado <= 0 or taxa_desconto_periodo <= -1:
            raise ValueError("Preço de mercado e taxa de desconto devem ser positivos")

        soma_ponderada = 0.0
        for t, fluxo in enumerate(fluxos, start=1):
            pv_fluxo = fluxo / (1 + taxa_desconto_periodo) ** t
            soma_ponderada += t * pv_fluxo

        return soma_ponderada / preco_mercado

    @staticmethod
    def duration_modificada(duration_macaulay, taxa_desconto_periodo):
        """
        Calcula Duration Modificada.

        Fórmula: D_mod = D_macaulay / (1 + y)
        Mede a sensibilidade do preço a variações na taxa de juros.

        Args:
            duration_macaulay (float): Duration de Macaulay em períodos
            taxa_desconto_periodo (float): Taxa de desconto por período

        Returns:
            float: Duration Modificada (variação % do preço por +1% na taxa)
        """
        return duration_macaulay / (1 + taxa_desconto_periodo)

    @staticmethod
    def calcular_ytm(preco_mercado, fluxos, chute_inicial=0.10, max_iter=1000, tolerancia=1e-8):
        """
        Calcula Yield to Maturity via método de Newton-Raphson.

        YTM é a taxa que iguala o valor presente dos fluxos ao preço de mercado:
        P = Σ[CFt / (1 + ytm)^t]

        Args:
            preco_mercado (float): Preço atual de mercado
            fluxos (list[float]): Fluxos de caixa por período
            chute_inicial (float): Estimativa inicial (padrão: 10%)
            max_iter (int): Máximo de iterações
            tolerancia (float): Precisão mínima

        Returns:
            float: YTM por período (multiplique por frequência para anualizar)
        """
        if preco_mercado <= 0:
            raise ValueError("Preço de mercado deve ser positivo")
        if not fluxos:
            raise ValueError("Lista de fluxos não pode ser vazia")

        ytm = chute_inicial

        for _ in range(max_iter):
            # f(ytm) = Σ[CFt / (1+ytm)^t] - Preço
            f = sum(cf / (1 + ytm) ** (t + 1) for t, cf in enumerate(fluxos)) - preco_mercado

            # f'(ytm) = -Σ[t * CFt / (1+ytm)^(t+1)]
            df = sum(-(t + 1) * cf / (1 + ytm) ** (t + 2) for t, cf in enumerate(fluxos))

            if df == 0:
                break

            ytm_novo = ytm - f / df

            if abs(ytm_novo - ytm) < tolerancia:
                return ytm_novo

            ytm = ytm_novo

        return ytm

    @staticmethod
    def calcular_rf_completo(preco_mercado, valor_nominal, taxa_cupom,
                              data_vencimento, frequencia_anual=1,
                              data_hoje=None):
        """
        Calcula todos os indicadores de RF para um título.

        Args:
            preco_mercado (float): Preço atual de mercado
            valor_nominal (float): Valor nominal/face do título
            taxa_cupom (float): Taxa de cupom anual
            data_vencimento (date): Data de vencimento
            frequencia_anual (int): Cupons por ano (1=anual, 2=semestral)
            data_hoje (date): Data de referência (default: hoje)

        Returns:
            dict: ytm_anual, duration_macaulay, duration_modificada, periodos,
                  cupom_por_periodo, premio_desconto, percentual_par
        """
        if data_hoje is None:
            data_hoje = date.today()

        preco_mercado = float(preco_mercado)
        valor_nominal = float(valor_nominal)
        taxa_cupom = float(taxa_cupom)

        # Número de períodos restantes
        periodos = RFCalcService.calcular_periodos(data_hoje, data_vencimento, frequencia_anual)

        # Taxa de cupom por período
        taxa_cupom_periodo = taxa_cupom / frequencia_anual

        # Fluxos de caixa
        fluxos = RFCalcService.calcular_fluxos_cupom(
            valor_nominal, taxa_cupom, frequencia_anual, periodos
        )

        # YTM por período → anualizar
        ytm_periodo = RFCalcService.calcular_ytm(preco_mercado, fluxos)
        ytm_anual = ytm_periodo * frequencia_anual

        # Duration de Macaulay (em períodos) → converter para anos
        dur_macaulay_periodos = RFCalcService.duration_macaulay(
            preco_mercado, fluxos, ytm_periodo
        )
        dur_macaulay_anos = dur_macaulay_periodos / frequencia_anual

        # Duration Modificada (em anos)
        dur_modificada = RFCalcService.duration_modificada(dur_macaulay_anos, ytm_anual)

        # Prêmio ou desconto em relação ao par
        premio_desconto = preco_mercado - valor_nominal
        percentual_par = (preco_mercado / valor_nominal) * 100

        return {
            'ytm_anual': round(ytm_anual, 6),
            'ytm_anual_pct': round(ytm_anual * 100, 4),
            'duration_macaulay_anos': round(dur_macaulay_anos, 4),
            'duration_modificada_anos': round(dur_modificada, 4),
            'periodos_restantes': periodos,
            'frequencia_anual': frequencia_anual,
            'taxa_cupom_anual': taxa_cupom,
            'taxa_cupom_anual_pct': round(taxa_cupom * 100, 4),
            'cupom_por_periodo': round(fluxos[0] if len(fluxos) > 1 else 0, 4),
            'valor_nominal': valor_nominal,
            'preco_mercado': preco_mercado,
            'premio_desconto': round(premio_desconto, 2),
            'percentual_par': round(percentual_par, 2),
            'negociando_acima_par': preco_mercado > valor_nominal,
        }

    # ================================================================
    # FII / REIT
    # ================================================================

    @staticmethod
    def calcular_ffo(lucro_liquido, depreciacao_amortizacao, ganhos_venda_imoveis=0):
        """
        Calcula FFO (Funds From Operations).

        Fórmula: FFO = Lucro Líquido + Depreciação/Amortização - Ganhos na venda de imóveis

        Args:
            lucro_liquido (float): Lucro líquido do FII
            depreciacao_amortizacao (float): Depreciação e amortização
            ganhos_venda_imoveis (float): Ganhos não recorrentes com venda de imóveis

        Returns:
            float: FFO
        """
        return lucro_liquido + depreciacao_amortizacao - ganhos_venda_imoveis

    @staticmethod
    def calcular_affo(ffo, capex_manutencao, ajustes_nao_recorrentes=0):
        """
        Calcula AFFO (Adjusted FFO).

        Fórmula: AFFO = FFO - CapEx de manutenção + Ajustes não recorrentes

        Args:
            ffo (float): FFO calculado
            capex_manutencao (float): Capex necessário para manter os imóveis
            ajustes_nao_recorrentes (float): Outros ajustes

        Returns:
            float: AFFO
        """
        return ffo - capex_manutencao + ajustes_nao_recorrentes

    @staticmethod
    def calcular_fii_completo(preco_atual, ffo_por_cota, affo_por_cota=None,
                               dividend_yield=None, p_vp=None, valor_patrimonial=None):
        """
        Calcula todos os indicadores de FII/REIT para um ativo.

        Args:
            preco_atual (float): Preço atual da cota
            ffo_por_cota (float): FFO por cota (anualizado)
            affo_por_cota (float): AFFO por cota (opcional)
            dividend_yield (float): DY atual (ex: 0.085 = 8,5%)
            p_vp (float): Preço/Valor Patrimonial atual
            valor_patrimonial (float): Valor patrimonial por cota

        Returns:
            dict: p_ffo, p_affo, ffo_yield, affo_yield, cap_rate_implícito, análise
        """
        preco_atual = float(preco_atual)
        ffo_por_cota = float(ffo_por_cota)

        # P/FFO — quanto o mercado paga por cada R$1 de FFO
        p_ffo = preco_atual / ffo_por_cota if ffo_por_cota > 0 else None

        # FFO Yield — rendimento baseado no FFO (mais conservador que DY)
        ffo_yield = ffo_por_cota / preco_atual if preco_atual > 0 else None

        # P/AFFO e AFFO Yield (se disponível)
        p_affo = None
        affo_yield = None
        if affo_por_cota:
            affo_por_cota = float(affo_por_cota)
            p_affo = preco_atual / affo_por_cota if affo_por_cota > 0 else None
            affo_yield = affo_por_cota / preco_atual if preco_atual > 0 else None

        # Cap Rate implícito via DY (se disponível)
        cap_rate_implicito = float(dividend_yield) if dividend_yield else None

        # Análise qualitativa
        analise = RFCalcService._analisar_fii(p_ffo, ffo_yield, p_vp)

        resultado = {
            'preco_atual': preco_atual,
            'ffo_por_cota': ffo_por_cota,
            'p_ffo': round(p_ffo, 2) if p_ffo else None,
            'ffo_yield': round(ffo_yield * 100, 4) if ffo_yield else None,
            'ffo_yield_pct': round(ffo_yield * 100, 2) if ffo_yield else None,
        }

        if affo_por_cota:
            resultado.update({
                'affo_por_cota': affo_por_cota,
                'p_affo': round(p_affo, 2) if p_affo else None,
                'affo_yield_pct': round(affo_yield * 100, 2) if affo_yield else None,
            })

        if cap_rate_implicito is not None:
            resultado['cap_rate_implicito_pct'] = round(cap_rate_implicito * 100, 2)

        if p_vp is not None:
            resultado['p_vp'] = float(p_vp)

        if valor_patrimonial is not None:
            resultado['valor_patrimonial'] = float(valor_patrimonial)
            resultado['desconto_premio_vp'] = round(preco_atual - float(valor_patrimonial), 2)

        resultado['analise'] = analise

        return resultado

    @staticmethod
    def _analisar_fii(p_ffo, ffo_yield, p_vp):
        """Análise qualitativa dos indicadores de FII"""
        sinais = []

        if p_ffo is not None:
            if p_ffo < 10:
                sinais.append('P/FFO abaixo de 10x — potencialmente barato')
            elif p_ffo < 15:
                sinais.append('P/FFO entre 10-15x — faixa justa')
            else:
                sinais.append('P/FFO acima de 15x — potencialmente caro')

        if ffo_yield is not None:
            ffo_yield_pct = ffo_yield * 100
            if ffo_yield_pct > 8:
                sinais.append(f'FFO Yield de {ffo_yield_pct:.1f}% — acima da média histórica')
            elif ffo_yield_pct > 6:
                sinais.append(f'FFO Yield de {ffo_yield_pct:.1f}% — na média histórica')
            else:
                sinais.append(f'FFO Yield de {ffo_yield_pct:.1f}% — abaixo da média histórica')

        if p_vp is not None:
            p_vp = float(p_vp)
            if p_vp < 0.9:
                sinais.append(f'P/VP de {p_vp:.2f}x — negociando com desconto ao patrimônio')
            elif p_vp <= 1.1:
                sinais.append(f'P/VP de {p_vp:.2f}x — próximo ao valor patrimonial')
            else:
                sinais.append(f'P/VP de {p_vp:.2f}x — negociando com prêmio ao patrimônio')

        return sinais
