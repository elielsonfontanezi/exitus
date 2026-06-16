# -*- coding: utf-8 -*-
"""
Testes para DARF Acumulado (EXITUS-DARF-ACUMULADO-001)
Verifica acúmulo de DARF < R$10,00 e pagamento quando atingir o mínimo
"""

import pytest
from decimal import Decimal
from datetime import datetime
from app.database import db
from app.services.ir_service import IRService
from app.models.saldo_darf_acumulado import SaldoDarfAcumulado


class TestDarfAcumulado:
    """Testes unitários do sistema de acúmulo de DARF"""
    
    def test_acumulo_darf_abaixo_minimo(self, app, usuario_seed):
        """Testa que IR < R$10,00 é acumulado e não gera DARF a pagar"""
        with app.app_context():
            # Mês 1: IR de R$5,00 (deve acumular)
            darf = IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('5.00'),  # ir_br
                Decimal('0'),     # ir_exterior
                Decimal('0'),     # ir_rf
                persist=True
            )
            
            # Não deve gerar DARF a pagar
            assert len(darf['darfs']) == 0
            
            # Verificar saldo acumulado no banco
            saldo = SaldoDarfAcumulado.query.filter_by(
                usuario_id=usuario_seed.id,
                categoria='swing_acoes',
                codigo_receita='6015',
                ano_mes='2025-01'
            ).first()
            
            assert saldo is not None
            assert saldo.saldo == Decimal('5.00')
    
    def test_acumulo_multiplos_meses_ate_minimo(self, app, usuario_seed):
        """Testa acúmulo por vários meses até atingir R$10,00"""
        with app.app_context():
            # Mês 1: R$3,00
            IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('3.00'), Decimal('0'), Decimal('0'),
                persist=True
            )
            
            # Mês 2: R$4,00 (total acumulado: R$7,00)
            IRService._calcular_darf(
                usuario_seed.id, "2025-02",
                Decimal('4.00'), Decimal('0'), Decimal('0'),
                persist=True
            )
            
            # Mês 3: R$5,00 (total acumulado: R$12,00 - deve pagar)
            darf = IRService._calcular_darf(
                usuario_seed.id, "2025-03",
                Decimal('5.00'), Decimal('0'), Decimal('0'),
                persist=True
            )
            
            # Deve gerar DARF de R$12,00
            assert len(darf['darfs']) == 1
            assert darf['darfs'][0]['valor'] == 12.0
            assert darf['darfs'][0]['pagar'] is True
            assert 'acumulado de meses anteriores' in darf['darfs'][0]['obs']
            
            # Saldo do mês atual deve ser zero (já pago)
            saldo_atual = SaldoDarfAcumulado.query.filter_by(
                usuario_id=usuario_seed.id,
                categoria='swing_acoes',
                codigo_receita='6015',
                ano_mes='2025-03'
            ).first()
            assert saldo_atual.saldo == Decimal('0')
    
    def test_darf_acima_minimo_sem_acumulado(self, app, usuario_seed):
        """Testa que IR >= R$10,00 gera DARF imediato sem acúmulo"""
        with app.app_context():
            darf = IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('15.00'),  # ir_br > R$10,00
                Decimal('0'),      # ir_exterior
                Decimal('0'),      # ir_rf
                persist=True
            )
            
            # Deve gerar DARF de R$15,00
            assert len(darf['darfs']) == 1
            assert darf['darfs'][0]['valor'] == 15.0
            assert darf['darfs'][0]['pagar'] is True
            assert darf['darfs'][0]['obs'] is None  # Sem observação de acúmulo
    
    def test_ir_zero_nao_acumula(self, app, usuario_seed):
        """Testa que IR = 0 não gera registro de acúmulo"""
        with app.app_context():
            darf = IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('0'),  # ir_br = 0
                Decimal('0'),  # ir_exterior = 0
                Decimal('0'),  # ir_rf = 0
                persist=True
            )
            
            # Não deve gerar DARF nem saldo acumulado
            assert len(darf['darfs']) == 0
            
            saldo = SaldoDarfAcumulado.query.filter_by(
                usuario_id=usuario_seed.id,
                ano_mes='2025-01'
            ).first()
            assert saldo is None
    
    def test_acumulo_por_categoria(self, app, usuario_seed):
        """Testa que acúmulo é separado por categoria e código de receita"""
        with app.app_context():
            # IR BR (categoria swing_acoes, código 6015)
            IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('5.00'),  # ir_br
                Decimal('0'),     # ir_exterior
                Decimal('0'),     # ir_rf
                persist=True
            )
            
            # IR Exterior (categoria exterior, código 0561)
            IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('0'),     # ir_br
                Decimal('3.00'),  # ir_exterior
                Decimal('0'),     # ir_rf
                persist=True
            )
            
            # Verificar dois saldos acumulados separados
            saldos = SaldoDarfAcumulado.query.filter_by(
                usuario_id=usuario_seed.id,
                ano_mes='2025-01'
            ).all()
            
            assert len(saldos) == 2
            
            # Verificar categorias e valores
            swing = next(s for s in saldos if s.categoria == 'swing_acoes')
            exterior = next(s for s in saldos if s.categoria == 'exterior')
            
            assert swing.codigo_receita == '6015'
            assert swing.saldo == Decimal('5.00')
            
            assert exterior.codigo_receita == '0561'
            assert exterior.saldo == Decimal('3.00')
    
    def test_ir_renda_fixa_nao_acumula(self, app, usuario_seed):
        """Testa que IR de renda fixa é sempre informativo (retido na fonte)"""
        with app.app_context():
            darf = IRService._calcular_darf(
                usuario_seed.id, "2025-01",
                Decimal('0'),      # ir_br
                Decimal('0'),      # ir_exterior
                Decimal('5.00'),  # ir_rf (retido na fonte)
                persist=True
            )
            
            # Deve gerar DARF informativo
            assert len(darf['darfs']) == 1
            assert darf['darfs'][0]['pagar'] is False
            assert 'retido na fonte' in darf['darfs'][0]['obs'].lower()
            
            # Não deve gerar saldo acumulado
            saldo = SaldoDarfAcumulado.query.filter_by(
                usuario_id=usuario_seed.id,
                categoria='rf',
                ano_mes='2025-01'
            ).first()
            assert saldo is None


class TestDarfAcumuladoIntegracao:
    """Testes de integração com endpoints reais"""
    
    def test_endpoint_ir_apuracao_com_acumulo(self, auth_client, usuario_seed):
        """Testa endpoint /api/ir/apuracao com acúmulo de DARF"""
        # Criar transação com IR pequeno para testar acúmulo
        # (Este teste requer setup mais complexo com transações reais)
        pass  # TODO: Implementar quando houver transações de teste
    
    def test_endpoint_darf_com_acumulado(self, auth_client, usuario_seed):
        """Testa endpoint /api/ir/darf com acúmulo"""
        # TODO: Implementar quando houver dados reais
        pass
