# -*- coding: utf-8 -*-
"""
Testes formais para IOF regressivo sobre rendimentos de RF.
GAP: EXITUS-IOF-001

Cobertura:
- Tabela regressiva TABELA_IOF_REGRESSIVA (dia 1 a 29)
- _calcular_iof(): limites de prazo, valores, isenção
- Integração com _apurar_renda_fixa(): campo iof_devido no retorno
"""
import pytest
from decimal import Decimal
from datetime import date

from app.services.ir_service import (
    TABELA_IOF_REGRESSIVA,
    _calcular_iof,
    _aliquota_rf,
)


# ---------------------------------------------------------------------------
# Testes da tabela TABELA_IOF_REGRESSIVA
# ---------------------------------------------------------------------------

class TestTabelaIOFRegressiva:

    def test_tabela_tem_30_entradas(self):
        assert len(TABELA_IOF_REGRESSIVA) == 30

    def test_dia_0_e_zero(self):
        assert TABELA_IOF_REGRESSIVA[0] == Decimal('0')

    def test_dia_1_e_096(self):
        assert TABELA_IOF_REGRESSIVA[1] == Decimal('0.96')

    def test_dia_15_e_050(self):
        assert TABELA_IOF_REGRESSIVA[15] == Decimal('0.50')

    def test_dia_29_e_003(self):
        assert TABELA_IOF_REGRESSIVA[29] == Decimal('0.03')

    def test_tabela_e_decrescente(self):
        # Cada alíquota deve ser <= à anterior (a partir do dia 1)
        for i in range(2, len(TABELA_IOF_REGRESSIVA)):
            assert TABELA_IOF_REGRESSIVA[i] <= TABELA_IOF_REGRESSIVA[i - 1], (
                f"Alíquota dia {i} ({TABELA_IOF_REGRESSIVA[i]}) maior que dia {i-1} ({TABELA_IOF_REGRESSIVA[i-1]})"
            )

    def test_todos_valores_entre_0_e_1(self):
        for i, aliquota in enumerate(TABELA_IOF_REGRESSIVA):
            assert Decimal('0') <= aliquota <= Decimal('1'), (
                f"Alíquota inválida no dia {i}: {aliquota}"
            )


# ---------------------------------------------------------------------------
# Testes de _calcular_iof()
# ---------------------------------------------------------------------------

class TestCalcularIOF:

    def test_prazo_zero_nao_cobra_iof(self):
        assert _calcular_iof(0, Decimal('1000.00')) == Decimal('0')

    def test_prazo_30_nao_cobra_iof(self):
        assert _calcular_iof(30, Decimal('1000.00')) == Decimal('0')

    def test_prazo_acima_30_nao_cobra_iof(self):
        assert _calcular_iof(365, Decimal('1000.00')) == Decimal('0')

    def test_rendimento_zero_nao_cobra_iof(self):
        assert _calcular_iof(5, Decimal('0')) == Decimal('0')

    def test_rendimento_negativo_nao_cobra_iof(self):
        assert _calcular_iof(5, Decimal('-100.00')) == Decimal('0')

    def test_dia_1_aliquota_96_porcento(self):
        # R$ 100 × 96% = R$ 96,00
        iof = _calcular_iof(1, Decimal('100.00'))
        assert iof == Decimal('96.00')

    def test_dia_15_aliquota_50_porcento(self):
        # R$ 200 × 50% = R$ 100,00
        iof = _calcular_iof(15, Decimal('200.00'))
        assert iof == Decimal('100.00')

    def test_dia_29_aliquota_3_porcento(self):
        # R$ 100 × 3% = R$ 3,00
        iof = _calcular_iof(29, Decimal('100.00'))
        assert iof == Decimal('3.00')

    def test_arredondamento_dois_casas(self):
        # R$ 100 × 96% = R$ 96,00 (sem casas problemáticas)
        iof = _calcular_iof(1, Decimal('33.33'))
        # 33.33 × 0.96 = 31.9968 → arredonda para 32.00
        assert iof == Decimal('32.00')

    def test_retorna_decimal(self):
        resultado = _calcular_iof(10, Decimal('500.00'))
        assert isinstance(resultado, Decimal)

    def test_dia_29_limite_antes_isencao(self):
        # Dia 29: ainda cobra IOF
        iof_29 = _calcular_iof(29, Decimal('1000.00'))
        assert iof_29 > Decimal('0')
        # Dia 30: isento
        iof_30 = _calcular_iof(30, Decimal('1000.00'))
        assert iof_30 == Decimal('0')


# ---------------------------------------------------------------------------
# Testes de integração com _apurar_renda_fixa()
# ---------------------------------------------------------------------------

class TestApurarRendaFixaComIOF:

    def test_retorno_vazio_tem_iof_devido(self, app):
        from app.services.ir_service import IRService
        with app.app_context():
            resultado = IRService._apurar_renda_fixa([], {}, {}, date.today())
            assert 'iof_devido' in resultado
            assert resultado['iof_devido'] == 0.0

    def test_detalhe_lci_tem_iof_zero(self, app):
        """LCI/LCA são isentos — iof_devido deve ser 0 nos detalhes."""
        from app.services.ir_service import IRService
        from unittest.mock import MagicMock
        from app.models.ativo import TipoAtivo

        with app.app_context():
            t = MagicMock()
            t.valor_total = 1000.0
            t.imposto = 0
            t.quantidade = 100
            t.custos_totais = 0
            t.ativo_id = 'uuid-lci'
            t.corretora_id = 'uuid-corretora'
            t.data_transacao = date(2026, 3, 10)

            resultado = IRService._apurar_renda_fixa(
                [(t, TipoAtivo.LCI_LCA, 'LCI-XYZ')],
                {},
                {},
                date(2026, 3, 10)
            )
            assert resultado['iof_devido'] == 0.0
            assert resultado['detalhes'][0]['iof_devido'] == 0.0

    def test_detalhe_cdb_prazo_longo_tem_iof_zero(self, app):
        """CDB com prazo >= 30 dias: iof_devido = 0."""
        from app.services.ir_service import IRService
        from unittest.mock import MagicMock
        from app.models.ativo import TipoAtivo

        with app.app_context():
            t = MagicMock()
            t.valor_total = 1100.0
            t.imposto = 20.0
            t.quantidade = 1
            t.custos_totais = 0
            t.ativo_id = 'uuid-cdb'
            t.corretora_id = 'uuid-corretora'
            t.data_transacao = date(2026, 3, 10)

            data_compra = date(2026, 1, 1)  # 68 dias antes → prazo >= 30 → IOF = 0
            pm_map = {('uuid-cdb', 'uuid-corretora'): Decimal('1000.00')}
            data_compra_map = {('uuid-cdb', 'uuid-corretora'): data_compra}

            resultado = IRService._apurar_renda_fixa(
                [(t, TipoAtivo.CDB, 'CDB-BANCO')],
                pm_map,
                data_compra_map,
                date(2026, 3, 10)
            )
            assert resultado['iof_devido'] == 0.0
            assert resultado['detalhes'][0]['iof_devido'] == 0.0

    def test_detalhe_cdb_prazo_curto_tem_iof(self, app):
        """CDB com prazo < 30 dias: iof_devido > 0."""
        from app.services.ir_service import IRService
        from unittest.mock import MagicMock
        from app.models.ativo import TipoAtivo

        with app.app_context():
            t = MagicMock()
            t.valor_total = 1100.0
            t.imposto = 0
            t.quantidade = 1
            t.custos_totais = 0
            t.ativo_id = 'uuid-cdb2'
            t.corretora_id = 'uuid-corretora2'
            t.data_transacao = date(2026, 3, 10)

            data_compra = date(2026, 3, 1)  # 9 dias antes → IOF = 70%
            pm_map = {('uuid-cdb2', 'uuid-corretora2'): Decimal('1000.00')}
            data_compra_map = {('uuid-cdb2', 'uuid-corretora2'): data_compra}

            resultado = IRService._apurar_renda_fixa(
                [(t, TipoAtivo.CDB, 'CDB-CURTO')],
                pm_map,
                data_compra_map,
                date(2026, 3, 10)
            )
            # rendimento = 1100 - 1000 = 100; IOF dia 9 = 70% → R$70,00
            assert resultado['iof_devido'] == 70.0
            assert resultado['detalhes'][0]['iof_devido'] == 70.0
