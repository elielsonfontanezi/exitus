# -*- coding: utf-8 -*-
"""
Exitus - Services Registry (M1-M7)
Registro de todos os services do sistema
"""

# M1-M6: Services existentes
from .auth_service import AuthService
from .usuario_service import UsuarioService
from .ativo_service import AtivoService
from .corretora_service import CorretoraService
from .transacao_service import TransacaoService
from .posicao_service import PosicaoService
from .provento_service import ProventoService
from .cotacao_service import CotacaoService

# M7.2: Novos Services - Relatórios e Análises Avançadas
from .relatorio_service import RelatorioService
from .alerta_service import AlertaService
from .projecao_service import ProjecaoService
from .analise_service import AnaliseService

# Lista completa de services disponíveis
SERVICES = [
    'AuthService',
    'UsuarioService', 
    'AtivoService',
    'CorretoraService',
    'TransacaoService',
    'PosicaoService',
    'ProventoService',
    'CotacaoService',
    # M7 Services
    'RelatorioService',
    'AlertaService',
    'ProjecaoService',
    'AnaliseService'
]

__all__ = SERVICES
