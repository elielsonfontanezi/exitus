# -*- coding: utf-8 -*-
"""
Exitus - Enums Módulo 7
Enumerações para Relatórios, Alertas e Análises Avançadas
"""

import enum


class TipoRelatorio(enum.Enum):
    """Tipos de relatórios disponíveis"""
    PORTFOLIO = "portfolio"
    PERFORMANCE = "performance"
    RENDA_PASSIVA = "renda_passiva"
    INVESTIMENTO = "investimento"
    CUSTOMIZADO = "customizado"


class FormatoExport(enum.Enum):
    """Formatos de exportação de relatórios"""
    VISUALIZACAO = "visualizacao"
    PDF = "pdf"
    EXCEL = "excel"


class TipoAlerta(enum.Enum):
    """Tipos de alertas configuráveis"""
    QUEDA_PRECO = "queda_preco"
    ALTA_PRECO = "alta_preco"
    DIVIDENDO_PREVISTO = "dividendo_previsto"
    META_RENTABILIDADE = "meta_rentabilidade"
    VOLATILIDADE_ALTA = "volatilidade_alta"
    DESVIO_ALOCACAO = "desvio_alocacao"
    NOTICIAS_ATIVO = "noticias_ativo"


class OperadorCondicao(enum.Enum):
    """Operadores para condições de alertas"""
    MAIOR = ">"
    MENOR = "<"
    IGUAL = "=="
    MAIOR_IGUAL = ">="
    MENOR_IGUAL = "<="
    ENTRE = "ENTRE"


class FrequenciaNotificacao(enum.Enum):
    """Frequência de envio de notificações"""
    IMEDIATA = "imediata"
    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSAL = "mensal"


class CanalEntrega(enum.Enum):
    """Canais de entrega de notificações"""
    EMAIL = "email"
    WEBAPP = "webapp"
    SMS = "sms"
    TELEGRAM = "telegram"
