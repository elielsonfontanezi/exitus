# -*- coding: utf-8 -*-
"""
Testes para ReconciliacaoService
GAP: EXITUS-RECONCILIACAO-001
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.database import db
from app.models import Posicao, Transacao, MovimentacaoCaixa, Corretora, Ativo, TipoTransacao
from app.services.reconciliacao_service import ReconciliacaoService
from app.services.posicao_service import PosicaoService


class TestReconciliacaoService:
    """Testes unitários do ReconciliacaoService"""
    
    def test_verificar_tudo_sem_divergencias(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Testa verificação completa sem divergências"""
        with app.app_context():
            # Criar transação e calcular posição
            transacao = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                taxa_corretagem=5.00,
                custos_totais=5.00,
                valor_liquido=1005.00
            )
            db.session.add(transacao)
            db.session.commit()
            
            # Calcular posições
            PosicaoService.calcular_posicoes(usuario_seed.id)
            
            # Verificar reconciliação
            resultado = ReconciliacaoService.verificar_tudo(usuario_seed.id)
            
            assert resultado['status'] == 'OK'
            assert resultado['resumo']['total_divergencias'] == 0
    
    def test_verificar_posicoes_com_divergencia_quantidade(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Testa detecção de divergência de quantidade"""
        with app.app_context():
            # Criar transação
            transacao = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=5.00,
                valor_liquido=1005.00
            )
            db.session.add(transacao)
            db.session.commit()
            
            # Criar posição manualmente com quantidade errada
            posicao = Posicao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                quantidade=150,  # Divergente: deveria ser 100
                preco_medio=10.00,
                custo_total=1005.00,
                taxas_acumuladas=5.00,
                impostos_acumulados=0
            )
            db.session.add(posicao)
            db.session.commit()
            
            # Verificar posições
            divergencias = ReconciliacaoService.verificar_posicoes(usuario_seed.id)
            
            assert len(divergencias) > 0
            assert any(d['tipo'] == 'POSICAO_QUANTIDADE' for d in divergencias)
            div = next(d for d in divergencias if d['tipo'] == 'POSICAO_QUANTIDADE')
            assert div['diferenca'] == 50.0
    
    def test_verificar_saldos_corretoras_sem_divergencia(self, app, usuario_seed, corretora_seed):
        """Testa verificação de saldo sem divergência"""
        with app.app_context():
            # Criar movimentações
            mov1 = MovimentacaoCaixa(
                usuario_id=usuario_seed.id,
                corretora_id=corretora_seed.id,
                tipo_movimentacao='DEPOSITO',
                valor=1000.00,
                data_movimentacao=datetime.utcnow().date()
            )
            mov2 = MovimentacaoCaixa(
                usuario_id=usuario_seed.id,
                corretora_id=corretora_seed.id,
                tipo_movimentacao='SAQUE',
                valor=200.00,
                data_movimentacao=datetime.utcnow().date()
            )
            db.session.add_all([mov1, mov2])
            
            # Atualizar saldo da corretora
            corretora_seed.saldo_atual = 800.00  # 1000 - 200
            db.session.commit()
            
            # Verificar saldos
            divergencias = ReconciliacaoService.verificar_saldos_corretoras(usuario_seed.id)
            
            assert len(divergencias) == 0
    
    def test_verificar_saldos_corretoras_com_divergencia(self, app, usuario_seed, corretora_seed):
        """Testa detecção de divergência de saldo"""
        with app.app_context():
            # Criar movimentações
            mov1 = MovimentacaoCaixa(
                usuario_id=usuario_seed.id,
                corretora_id=corretora_seed.id,
                tipo_movimentacao='DEPOSITO',
                valor=1000.00,
                data_movimentacao=datetime.utcnow().date()
            )
            db.session.add(mov1)
            
            # Saldo registrado divergente
            corretora_seed.saldo_atual = 500.00  # Deveria ser 1000
            db.session.commit()
            
            # Verificar saldos
            divergencias = ReconciliacaoService.verificar_saldos_corretoras(usuario_seed.id)
            
            assert len(divergencias) > 0
            assert divergencias[0]['tipo'] == 'SALDO_CORRETORA'
            assert divergencias[0]['diferenca'] == 500.0
    
    def test_verificar_integridade_transacoes_sem_ativo(self, app, usuario_seed, corretora_seed):
        """Testa detecção de transação sem ativo"""
        with app.app_context():
            # Criar transação sem ativo (forçando)
            transacao = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=None,  # Sem ativo
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=0,
                valor_liquido=1000.00
            )
            db.session.add(transacao)
            db.session.commit()
            
            # Verificar integridade
            divergencias = ReconciliacaoService.verificar_integridade_transacoes(usuario_seed.id)
            
            assert len(divergencias) > 0
            assert any(d['tipo'] == 'TRANSACAO_SEM_ATIVO' for d in divergencias)
    
    def test_verificar_integridade_transacoes_duplicadas(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Testa detecção de transações duplicadas por hash"""
        with app.app_context():
            hash_comum = 'abc123def456'
            
            # Criar duas transações com mesmo hash
            t1 = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=0,
                valor_liquido=1000.00,
                hash_importacao=hash_comum
            )
            t2 = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=0,
                valor_liquido=1000.00,
                hash_importacao=hash_comum
            )
            db.session.add_all([t1, t2])
            db.session.commit()
            
            # Verificar integridade
            divergencias = ReconciliacaoService.verificar_integridade_transacoes(usuario_seed.id)
            
            assert len(divergencias) > 0
            assert any(d['tipo'] == 'TRANSACAO_DUPLICADA' for d in divergencias)
    
    def test_verificar_ativo_especifico_ok(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Testa verificação de ativo específico sem divergência"""
        with app.app_context():
            # Criar transação
            transacao = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=5.00,
                valor_liquido=1005.00
            )
            db.session.add(transacao)
            db.session.commit()
            
            # Calcular posições
            PosicaoService.calcular_posicoes(usuario_seed.id)
            
            # Verificar ativo específico
            resultado = ReconciliacaoService.verificar_ativo_especifico(
                usuario_seed.id,
                ativo_seed.id
            )
            
            assert len(resultado['corretoras']) > 0
            assert resultado['corretoras'][0]['status'] == 'OK'
            assert len(resultado['divergencias']) == 0
    
    def test_verificar_ativo_especifico_divergente(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Testa verificação de ativo específico com divergência"""
        with app.app_context():
            # Criar transação
            transacao = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=0,
                valor_liquido=1000.00
            )
            db.session.add(transacao)
            db.session.commit()
            
            # Criar posição com quantidade divergente
            posicao = Posicao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                quantidade=200,  # Divergente
                preco_medio=10.00,
                custo_total=1000.00,
                taxas_acumuladas=0,
                impostos_acumulados=0
            )
            db.session.add(posicao)
            db.session.commit()
            
            # Verificar ativo específico
            resultado = ReconciliacaoService.verificar_ativo_especifico(
                usuario_seed.id,
                ativo_seed.id
            )
            
            assert len(resultado['corretoras']) > 0
            assert resultado['corretoras'][0]['status'] == 'DIVERGENTE'
            assert len(resultado['divergencias']) > 0
    
    def test_tolerancia_arredondamento(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Testa que pequenas diferenças de arredondamento são toleradas"""
        with app.app_context():
            # Criar transação
            transacao = Transacao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                tipo=TipoTransacao.COMPRA,
                data_transacao=datetime.utcnow(),
                quantidade=100,
                preco_unitario=10.00,
                valor_total=1000.00,
                custos_totais=0,
                valor_liquido=1000.00
            )
            db.session.add(transacao)
            db.session.commit()
            
            # Criar posição com diferença mínima (dentro da tolerância)
            posicao = Posicao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo_seed.id,
                corretora_id=corretora_seed.id,
                quantidade=Decimal('100.005'),  # Diferença de 0.005 < tolerância 0.01
                preco_medio=10.00,
                custo_total=1000.00,
                taxas_acumuladas=0,
                impostos_acumulados=0
            )
            db.session.add(posicao)
            db.session.commit()
            
            # Verificar posições
            divergencias = ReconciliacaoService.verificar_posicoes(usuario_seed.id)
            
            # Não deve reportar divergência
            assert len([d for d in divergencias if d['tipo'] == 'POSICAO_QUANTIDADE']) == 0


class TestReconciliacaoIntegration:
    """Testes de integração com endpoints"""
    
    def test_endpoint_verificar_completo(self, auth_client):
        """Testa endpoint de verificação completa"""
        response = auth_client.get('/api/reconciliacao/verificar')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'divergencias' in data
        assert 'resumo' in data
    
    def test_endpoint_verificar_posicoes(self, auth_client):
        """Testa endpoint de verificação de posições"""
        response = auth_client.get('/api/reconciliacao/posicoes')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'divergencias' in data
        assert 'total' in data
    
    def test_endpoint_verificar_saldos(self, auth_client):
        """Testa endpoint de verificação de saldos"""
        response = auth_client.get('/api/reconciliacao/saldos')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'divergencias' in data
        assert 'total' in data
    
    def test_endpoint_verificar_integridade(self, auth_client):
        """Testa endpoint de verificação de integridade"""
        response = auth_client.get('/api/reconciliacao/integridade')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'divergencias' in data
        assert 'total' in data
    
    def test_endpoint_verificar_ativo_especifico(self, auth_client, ativo_seed):
        """Testa endpoint de verificação de ativo específico"""
        response = auth_client.get(f'/api/reconciliacao/ativo/{ativo_seed.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'ativo_id' in data
        assert 'corretoras' in data
        assert 'divergencias' in data
