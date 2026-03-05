# -*- coding: utf-8 -*-
"""Exitus - CambioService - Conversão de moedas e busca de taxas de câmbio"""

from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, List

from app.database import db
from app.models.taxa_cambio import TaxaCambio, TAXAS_FALLBACK, MOEDAS_SUPORTADAS


class CambioService:
    """
    Serviço de câmbio multi-moeda.

    Estratégia de resolução de taxa (em ordem):
    1. Banco de dados — cotação mais recente para o par
    2. Cálculo cruzado via BRL (ex: USD→EUR via USD/BRL e BRL/EUR)
    3. Fallback hardcoded em TAXAS_FALLBACK
    """

    @staticmethod
    def _construir_par(moeda_base: str, moeda_cotacao: str) -> str:
        return f"{moeda_base.upper()}/{moeda_cotacao.upper()}"

    @staticmethod
    def _taxa_do_banco(par_moeda: str, data: Optional[date] = None) -> Optional[Decimal]:
        """Busca taxa no banco — data específica ou mais recente"""
        if data:
            registro = TaxaCambio.get_taxa_na_data(par_moeda, data)
        else:
            registro = TaxaCambio.get_taxa_atual(par_moeda)
        return Decimal(str(registro.taxa)) if registro else None

    @staticmethod
    def _taxa_cruzada_via_brl(moeda_origem: str, moeda_destino: str,
                               data: Optional[date] = None) -> Optional[Decimal]:
        """
        Calcula taxa cruzada usando BRL como moeda pivô.
        Ex: USD → EUR = (USD/BRL) * (BRL/EUR)
        """
        if moeda_origem == 'BRL':
            par = CambioService._construir_par('BRL', moeda_destino)
            return CambioService._taxa_do_banco(par, data) or TAXAS_FALLBACK.get(par)

        if moeda_destino == 'BRL':
            par = CambioService._construir_par(moeda_origem, 'BRL')
            return CambioService._taxa_do_banco(par, data) or TAXAS_FALLBACK.get(par)

        par_orig_brl = CambioService._construir_par(moeda_origem, 'BRL')
        par_brl_dest = CambioService._construir_par('BRL', moeda_destino)

        taxa_orig_brl = (CambioService._taxa_do_banco(par_orig_brl, data)
                         or TAXAS_FALLBACK.get(par_orig_brl))
        taxa_brl_dest = (CambioService._taxa_do_banco(par_brl_dest, data)
                         or TAXAS_FALLBACK.get(par_brl_dest))

        if taxa_orig_brl and taxa_brl_dest:
            return taxa_orig_brl * taxa_brl_dest
        return None

    @classmethod
    def get_taxa(cls, moeda_origem: str, moeda_destino: str,
                 data: Optional[date] = None) -> Dict:
        """
        Retorna taxa de câmbio entre dois pares.
        Tenta banco → cruzamento via BRL → fallback hardcoded.
        """
        moeda_origem = moeda_origem.upper()
        moeda_destino = moeda_destino.upper()

        if moeda_origem == moeda_destino:
            return {
                'par_moeda': f'{moeda_origem}/{moeda_destino}',
                'moeda_base': moeda_origem,
                'moeda_cotacao': moeda_destino,
                'taxa': 1.0,
                'fonte': 'identidade',
                'data_referencia': (data or date.today()).isoformat(),
            }

        par = cls._construir_par(moeda_origem, moeda_destino)

        taxa = cls._taxa_do_banco(par, data)
        fonte = 'banco'

        if taxa is None:
            taxa = cls._taxa_cruzada_via_brl(moeda_origem, moeda_destino, data)
            fonte = 'cruzamento_brl'

        if taxa is None:
            taxa = TAXAS_FALLBACK.get(par)
            fonte = 'fallback'

        if taxa is None:
            return {
                'par_moeda': par,
                'moeda_base': moeda_origem,
                'moeda_cotacao': moeda_destino,
                'taxa': None,
                'fonte': None,
                'data_referencia': (data or date.today()).isoformat(),
                'erro': f'Taxa não disponível para {par}',
            }

        registro = TaxaCambio.get_taxa_atual(par) if fonte == 'banco' else None
        data_ref = (registro.data_referencia.isoformat()
                    if registro and registro.data_referencia
                    else (data or date.today()).isoformat())

        return {
            'par_moeda': par,
            'moeda_base': moeda_origem,
            'moeda_cotacao': moeda_destino,
            'taxa': float(taxa),
            'fonte': fonte,
            'data_referencia': data_ref,
        }

    @classmethod
    def converter(cls, valor: Decimal, moeda_origem: str, moeda_destino: str,
                  data: Optional[date] = None) -> Dict:
        """
        Converte um valor de moeda_origem para moeda_destino.
        Retorna dicionário com valor convertido e taxa utilizada.
        """
        resultado_taxa = cls.get_taxa(moeda_origem, moeda_destino, data)

        if resultado_taxa.get('erro'):
            return {
                'valor_original': float(valor),
                'moeda_origem': moeda_origem.upper(),
                'moeda_destino': moeda_destino.upper(),
                'valor_convertido': None,
                'taxa': None,
                'fonte': None,
                'erro': resultado_taxa['erro'],
            }

        taxa = Decimal(str(resultado_taxa['taxa']))
        valor_convertido = (valor * taxa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'valor_original': float(valor),
            'moeda_origem': moeda_origem.upper(),
            'moeda_destino': moeda_destino.upper(),
            'valor_convertido': float(valor_convertido),
            'taxa': resultado_taxa['taxa'],
            'fonte': resultado_taxa['fonte'],
            'data_referencia': resultado_taxa['data_referencia'],
        }

    @classmethod
    def converter_para_brl(cls, valor: Decimal, moeda_origem: str,
                            data: Optional[date] = None) -> Optional[Decimal]:
        """
        Atalho: converte qualquer moeda para BRL.
        Retorna apenas o Decimal convertido (para uso interno em services).
        """
        if moeda_origem.upper() == 'BRL':
            return valor

        resultado = cls.converter(valor, moeda_origem, 'BRL', data)
        if resultado.get('erro'):
            return None
        return Decimal(str(resultado['valor_convertido']))

    @classmethod
    def registrar_taxa(cls, par_moeda: str, taxa: Decimal,
                        data_referencia: date, fonte: str = 'manual') -> TaxaCambio:
        """
        Registra ou atualiza uma taxa de câmbio no banco.
        Se já existir o par na data, atualiza a taxa.
        """
        par_moeda = par_moeda.upper()
        partes = par_moeda.split('/')
        if len(partes) != 2:
            raise ValueError(f'Formato de par inválido: {par_moeda}. Use BASE/COTACAO (ex: BRL/USD)')

        moeda_base, moeda_cotacao = partes

        existente = (TaxaCambio.query
                     .filter_by(par_moeda=par_moeda, data_referencia=data_referencia)
                     .first())

        if existente:
            existente.taxa = taxa
            existente.fonte = fonte
            db.session.commit()
            return existente

        nova = TaxaCambio(
            par_moeda=par_moeda,
            moeda_base=moeda_base,
            moeda_cotacao=moeda_cotacao,
            taxa=taxa,
            data_referencia=data_referencia,
            fonte=fonte,
            created_at=datetime.utcnow(),
        )
        db.session.add(nova)
        db.session.commit()
        return nova

    @classmethod
    def buscar_taxa_yfinance(cls, par_moeda: str) -> Optional[Dict]:
        """
        Busca taxa de câmbio atual via yfinance.
        yfinance usa o formato BASECOTACAO=X (ex: BRLUSD=X, USDEUR=X).
        Retorna dict com taxa e data, ou None se indisponível.
        """
        try:
            import yfinance as yf
            partes = par_moeda.upper().split('/')
            if len(partes) != 2:
                return None
            moeda_base, moeda_cotacao = partes
            ticker_symbol = f'{moeda_base}{moeda_cotacao}=X'
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.fast_info
            taxa = getattr(info, 'last_price', None)
            if taxa is None or taxa == 0:
                return None
            return {
                'taxa': Decimal(str(round(taxa, 8))),
                'data_referencia': date.today(),
                'fonte': 'yfinance',
            }
        except Exception:
            return None

    @classmethod
    def atualizar_taxas_yfinance(cls, pares: Optional[List[str]] = None) -> Dict:
        """
        Atualiza taxas de câmbio via yfinance para os pares informados.
        Se pares=None, atualiza os pares com fallback definido.
        Retorna resumo de sucesso/falha.
        """
        if pares is None:
            pares = list(TAXAS_FALLBACK.keys())

        resultado = {'atualizados': [], 'falhas': []}

        for par in pares:
            dados = cls.buscar_taxa_yfinance(par)
            if dados:
                try:
                    cls.registrar_taxa(
                        par_moeda=par,
                        taxa=dados['taxa'],
                        data_referencia=dados['data_referencia'],
                        fonte=dados['fonte'],
                    )
                    resultado['atualizados'].append(par)
                except Exception as e:
                    resultado['falhas'].append({'par': par, 'erro': str(e)})
            else:
                resultado['falhas'].append({'par': par, 'erro': 'yfinance indisponível'})

        return resultado

    @classmethod
    def listar_pares_disponiveis(cls) -> List[Dict]:
        """Lista todos os pares com a taxa mais recente disponível"""
        from sqlalchemy import func
        subq = (db.session.query(
            TaxaCambio.par_moeda,
            func.max(TaxaCambio.data_referencia).label('ultima_data')
        ).group_by(TaxaCambio.par_moeda).subquery())

        registros = (db.session.query(TaxaCambio)
                     .join(subq, db.and_(
                         TaxaCambio.par_moeda == subq.c.par_moeda,
                         TaxaCambio.data_referencia == subq.c.ultima_data
                     ))
                     .order_by(TaxaCambio.par_moeda)
                     .all())

        resultado = [r.to_dict() for r in registros]

        pares_no_banco = {r['par_moeda'] for r in resultado}
        for par, taxa in TAXAS_FALLBACK.items():
            if par not in pares_no_banco:
                partes = par.split('/')
                resultado.append({
                    'par_moeda': par,
                    'moeda_base': partes[0],
                    'moeda_cotacao': partes[1],
                    'taxa': float(taxa),
                    'fonte': 'fallback',
                    'data_referencia': None,
                })

        return resultado
