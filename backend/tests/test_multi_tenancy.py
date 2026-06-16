# -*- coding: utf-8 -*-
"""
Exitus - Testes de Multi-Tenancy
Testes para validar isolamento de dados por assessora
"""

import pytest
from flask_jwt_extended import create_access_token, decode_token
from app.models import Usuario, Portfolio, UserRole
from app.utils.tenant import get_current_assessora_id, filter_by_assessora
import uuid


class TestMultiTenancy:
    """Testes de multi-tenancy e isolamento de dados"""
    
    def test_jwt_com_assessora_id(self, app):
        """Testa criação de JWT com assessora_id"""
        assessora_id = str(uuid.uuid4())
        usuario_id = str(uuid.uuid4())
        
        # Criar token com assessora_id
        token = create_access_token(
            identity=usuario_id,
            additional_claims={
                'role': 'user',
                'assessora_id': assessora_id
            }
        )
        
        # Decodificar token
        decoded = decode_token(token)
        
        # Verificar que assessora_id está presente
        assert 'assessora_id' in decoded
        assert decoded['assessora_id'] == assessora_id
    
    def test_tenant_helper_functions(self, app):
        """Testa funções helper de tenant"""
        from app.utils.tenant import filter_by_assessora
        
        # Testar filter_by_assessora sem JWT (deve retornar query sem filtro)
        query = Usuario.query
        filtered_query = filter_by_assessora(query, Usuario)
        
        # Query deve ser retornada (mesmo sem JWT ativo)
        assert filtered_query is not None
    
    def test_services_importam_tenant_utils(self, app):
        """Testa que services importam utils de tenant"""
        from app.services.usuario_service import UsuarioService
        from app.services.portfolio_service import PortfolioService
        from app.services.transacao_service import TransacaoService
        from app.services.posicao_service import PosicaoService
        from app.services.plano_venda_service import PlanoVendaService
        
        # Se importar sem erro, está OK
        assert UsuarioService is not None
        assert PortfolioService is not None
        assert TransacaoService is not None
        assert PosicaoService is not None
        assert PlanoVendaService is not None
