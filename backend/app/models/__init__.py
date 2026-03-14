# -*- coding: utf-8 -*-
"""
Exitus - Models Package
Exportação centralizada de todos os models
"""

# Módulo 1 e 2 - Core
from .usuario import Usuario, UserRole
from .corretora import Corretora, TipoCorretora
from .ativo import Ativo, TipoAtivo, ClasseAtivo
from .transacao import Transacao, TipoTransacao

# Módulo 3 - Entidades Financeiras
from .posicao import Posicao
from .saldo_prejuizo import SaldoPrejuizo
from .saldo_darf_acumulado import SaldoDarfAcumulado
from .provento import Provento, TipoProvento
from .movimentacao_caixa import MovimentacaoCaixa, TipoMovimentacao
from .evento_corporativo import EventoCorporativo

# Módulo 4 - Dados de Suporte
from .feriado_mercado import FeriadoMercado
from .fonte_dados import FonteDados
from .regra_fiscal import RegraFiscal, IncidenciaImposto
from .log_auditoria import LogAuditoria
from .parametros_macro import ParametrosMacro

# Módulo 7 - Relatórios e Análises Avançadas
from .enums_m7 import (
    TipoRelatorio,
    FormatoExport,
    TipoAlerta,
    OperadorCondicao,
    FrequenciaNotificacao,
    CanalEntrega
)
from .auditoria_relatorio import AuditoriaRelatorio
from .configuracao_alerta import ConfiguracaoAlerta
from .projecao_renda import ProjecaoRenda
from .relatorio_performance import RelatorioPerformance
from .portfolio import Portfolio

from app.models.historico_preco import HistoricoPreco

# Fase 3 - Planos de Compra
from .plano_compra import PlanoCompra, StatusPlanoCompra

__all__ = [
    # Core
    "Usuario",
    "UserRole",
    "Corretora",
    "TipoCorretora",
    "Ativo",
    "TipoAtivo",
    "ClasseAtivo",
    "Transacao",
    "TipoTransacao",

    # Entidades Financeiras
    "Posicao",
    "SaldoPrejuizo",
    "SaldoDarfAcumulado",
    "Provento",
    "TipoProvento",
    "MovimentacaoCaixa",
    "TipoMovimentacao",
    "EventoCorporativo",

    # Dados de Suporte
    "FeriadoMercado",
    "FonteDados",
    "RegraFiscal",
    "IncidenciaImposto",
    "LogAuditoria",
    "ParametrosMacro",

    # Módulo 7 - Enums
    "TipoRelatorio",
    "FormatoExport",
    "TipoAlerta",
    "OperadorCondicao",
    "FrequenciaNotificacao",
    "CanalEntrega",

    # Módulo 7 - Models
    "AuditoriaRelatorio",
    "ConfiguracaoAlerta",
    "ProjecaoRenda",
    "RelatorioPerformance",
    "Portfolio",
    
    # Fase 3 - Planos de Compra
    "PlanoCompra",
    "StatusPlanoCompra",
]
