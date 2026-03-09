# -*- coding: utf-8 -*-
"""
Testes para AuditoriaService e integração com services
GAP: EXITUS-AUDITLOG-001
"""

import pytest
from datetime import datetime
from app.database import db
from app.models import LogAuditoria, Usuario, Ativo, Transacao, Provento, MovimentacaoCaixa, TipoAtivo
from app.services.auditoria_service import AuditoriaService
from app.services.transacao_service import TransacaoService
from app.services.ativo_service import AtivoService
from app.services.auth_service import AuthService


class TestAuditoriaService:
    """Testes unitários do AuditoriaService"""
    
    def test_registrar_create(self, app):
        with app.app_context():
            # Criar usuário de teste
            usuario = Usuario.query.first()
            
            # Registrar auditoria
            log = AuditoriaService.registrar_create(
                usuario_id=usuario.id,
                entidade='Teste',
                entidade_id='123e4567-e89b-12d3-a456-426614174000',
                dados_depois={'campo': 'valor'}
            )
            
            assert log is not None
            assert log.acao == 'CREATE'
            assert log.entidade == 'Teste'
            assert log.sucesso is True
            assert log.dados_depois == {'campo': 'valor'}
            assert log.dados_antes is None
    
    def test_registrar_update(self, app):
        with app.app_context():
            usuario = Usuario.query.first()
            
            log = AuditoriaService.registrar_update(
                usuario_id=usuario.id,
                entidade='Teste',
                entidade_id='123e4567-e89b-12d3-a456-426614174000',
                dados_antes={'campo': 'valor_antigo'},
                dados_depois={'campo': 'valor_novo'}
            )
            
            assert log is not None
            assert log.acao == 'UPDATE'
            assert log.dados_antes == {'campo': 'valor_antigo'}
            assert log.dados_depois == {'campo': 'valor_novo'}
    
    def test_registrar_delete(self, app):
        with app.app_context():
            usuario = Usuario.query.first()
            
            log = AuditoriaService.registrar_delete(
                usuario_id=usuario.id,
                entidade='Teste',
                entidade_id='123e4567-e89b-12d3-a456-426614174000',
                dados_antes={'campo': 'valor'}
            )
            
            assert log is not None
            assert log.acao == 'DELETE'
            assert log.dados_antes == {'campo': 'valor'}
            assert log.dados_depois is None
    
    def test_registrar_login_sucesso(self, app):
        with app.app_context():
            usuario = Usuario.query.first()
            
            log = AuditoriaService.registrar_login(
                usuario_id=usuario.id,
                sucesso=True
            )
            
            assert log is not None
            assert log.acao == 'LOGIN'
            assert log.sucesso is True
            assert log.mensagem is None
    
    def test_registrar_login_falha(self, app):
        with app.app_context():
            usuario = Usuario.query.first()
            
            log = AuditoriaService.registrar_login(
                usuario_id=usuario.id,
                sucesso=False,
                mensagem='Senha incorreta'
            )
            
            assert log is not None
            assert log.acao == 'LOGIN'
            assert log.sucesso is False
            assert log.mensagem == 'Senha incorreta'
    
    def test_registrar_nunca_levanta_excecao(self, app):
        with app.app_context():
            # Tentar registrar com dados inválidos não deve quebrar
            log = AuditoriaService.registrar(
                usuario_id=None,  # Inválido mas não deve quebrar
                acao='TESTE',
                entidade='Teste'
            )
            
            # Pode retornar None em caso de erro, mas não deve levantar exceção
            assert True  # Se chegou aqui, não levantou exceção


class TestAuditoriaIntegracaoTransacao:
    """Testes de integração com TransacaoService"""
    
    def test_create_transacao_registra_auditoria(self, app, usuario_seed, ativo_seed, corretora_seed):
        with app.app_context():
            count_antes = LogAuditoria.query.filter_by(acao='CREATE', entidade='Transacao').count()
            
            # Criar transação
            data = {
                'tipo': 'compra',
                'ativo_id': ativo_seed.id,
                'corretora_id': corretora_seed.id,
                'data_transacao': '2024-01-15',
                'quantidade': 100,
                'preco_unitario': 25.50,
                'taxa_corretagem': 10.00,
                'imposto': 0,
                'outros_custos': 0
            }
            
            resultado = TransacaoService.create(usuario_seed.id, data)
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(acao='CREATE', entidade='Transacao').count()
            assert count_depois == count_antes + 1
            
            # Verificar último log
            log = LogAuditoria.query.filter_by(
                acao='CREATE',
                entidade='Transacao',
                entidade_id=resultado['transacao'].id
            ).first()
            
            assert log is not None
            assert log.usuario_id == usuario_seed.id
            assert log.sucesso is True
            assert log.dados_depois is not None
            assert 'quantidade' in log.dados_depois
    
    def test_update_transacao_registra_auditoria(self, app, transacao_seed):
        with app.app_context():
            count_antes = LogAuditoria.query.filter_by(acao='UPDATE', entidade='Transacao').count()
            
            # Atualizar transação
            data = {'quantidade': 150}
            TransacaoService.update(transacao_seed.id, transacao_seed.usuario_id, data)
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(acao='UPDATE', entidade='Transacao').count()
            assert count_depois == count_antes + 1
            
            # Verificar log
            log = LogAuditoria.query.filter_by(
                acao='UPDATE',
                entidade='Transacao',
                entidade_id=transacao_seed.id
            ).order_by(LogAuditoria.timestamp.desc()).first()
            
            assert log is not None
            assert log.dados_antes is not None
            assert log.dados_depois is not None
            assert log.dados_antes['quantidade'] != log.dados_depois['quantidade']
    
    def test_delete_transacao_registra_auditoria(self, app, transacao_seed):
        with app.app_context():
            transacao_id = transacao_seed.id
            usuario_id = transacao_seed.usuario_id
            
            count_antes = LogAuditoria.query.filter_by(acao='DELETE', entidade='Transacao').count()
            
            # Deletar transação
            TransacaoService.delete(transacao_id, usuario_id)
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(acao='DELETE', entidade='Transacao').count()
            assert count_depois == count_antes + 1
            
            # Verificar log
            log = LogAuditoria.query.filter_by(
                acao='DELETE',
                entidade='Transacao',
                entidade_id=transacao_id
            ).first()
            
            assert log is not None
            assert log.dados_antes is not None
            assert log.dados_depois is None


class TestAuditoriaIntegracaoAtivo:
    """Testes de integração com AtivoService"""
    
    def test_create_ativo_registra_auditoria(self, app):
        with app.app_context():
            count_antes = LogAuditoria.query.filter_by(acao='CREATE', entidade='Ativo').count()
            
            # Criar ativo
            data = {
                'ticker': 'TEST4',
                'nome': 'Teste Ativo Auditoria',
                'tipo': 'ACAO',
                'classe': 'RENDA_VARIAVEL',
                'mercado': 'BR',
                'moeda': 'BRL',
                'preco_atual': 100.00
            }
            
            ativo = AtivoService.create(data)
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(acao='CREATE', entidade='Ativo').count()
            assert count_depois == count_antes + 1
            
            # Limpar
            db.session.delete(ativo)
            db.session.commit()
    
    def test_update_ativo_registra_auditoria(self, app, ativo_seed):
        with app.app_context():
            count_antes = LogAuditoria.query.filter_by(acao='UPDATE', entidade='Ativo').count()
            
            # Atualizar ativo
            data = {'nome': 'Nome Atualizado Auditoria'}
            AtivoService.update(ativo_seed.id, data)
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(acao='UPDATE', entidade='Ativo').count()
            assert count_depois == count_antes + 1


class TestAuditoriaIntegracaoAuth:
    """Testes de integração com AuthService"""
    
    def test_login_sucesso_registra_auditoria(self, app, usuario_seed):
        with app.app_context():
            count_antes = LogAuditoria.query.filter_by(
                acao='LOGIN',
                usuario_id=usuario_seed.id,
                sucesso=True
            ).count()
            
            # Login bem-sucedido
            AuthService.login(usuario_seed.username, 'senha_teste_123')
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(
                acao='LOGIN',
                usuario_id=usuario_seed.id,
                sucesso=True
            ).count()
            
            assert count_depois == count_antes + 1
    
    def test_login_falha_senha_registra_auditoria(self, app, usuario_seed):
        with app.app_context():
            count_antes = LogAuditoria.query.filter_by(
                acao='LOGIN',
                usuario_id=usuario_seed.id,
                sucesso=False
            ).count()
            
            # Login com senha incorreta
            with pytest.raises(ValueError):
                AuthService.login(usuario_seed.username, 'senha_errada')
            
            # Verificar auditoria
            count_depois = LogAuditoria.query.filter_by(
                acao='LOGIN',
                usuario_id=usuario_seed.id,
                sucesso=False
            ).count()
            
            assert count_depois == count_antes + 1
            
            # Verificar mensagem
            log = LogAuditoria.query.filter_by(
                acao='LOGIN',
                usuario_id=usuario_seed.id,
                sucesso=False
            ).order_by(LogAuditoria.timestamp.desc()).first()
            
            assert log.mensagem == 'Senha incorreta'


class TestLogAuditoriaModel:
    """Testes do model LogAuditoria"""
    
    def test_get_alteracoes(self, app):
        with app.app_context():
            usuario = Usuario.query.first()
            
            log = LogAuditoria(
                usuario_id=usuario.id,
                acao='UPDATE',
                entidade='Teste',
                dados_antes={'campo1': 'valor1', 'campo2': 'valor2'},
                dados_depois={'campo1': 'valor1', 'campo2': 'valor_novo'}
            )
            
            alteracoes = log.get_alteracoes()
            
            assert 'campo1' not in alteracoes  # Não mudou
            assert 'campo2' in alteracoes
            assert alteracoes['campo2']['antes'] == 'valor2'
            assert alteracoes['campo2']['depois'] == 'valor_novo'
    
    def test_to_dict(self, app):
        with app.app_context():
            usuario = Usuario.query.first()
            
            log = LogAuditoria(
                usuario_id=usuario.id,
                acao='CREATE',
                entidade='Teste',
                dados_depois={'campo': 'valor'}
            )
            db.session.add(log)
            db.session.commit()
            
            data = log.to_dict(include_dados=True)
            
            assert 'id' in data
            assert data['acao'] == 'CREATE'
            assert data['entidade'] == 'Teste'
            assert data['dados_depois'] == {'campo': 'valor'}
            assert 'alteracoes' in data
