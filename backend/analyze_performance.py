#!/usr/bin/env python3
"""
Script de Análise de Performance - Fase 4
Identifica queries lentas e endpoints críticos
"""

import time
import logging
from uuid import UUID
from app import create_app
from app.database import db
from app.services.portfolio_service import PortfolioService
from app.services.transacao_service import TransacaoService
from app.services.ativo_service import AtivoService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def time_query(func, *args, **kwargs):
    """Mede tempo de execução de uma função"""
    start = time.time()
    try:
        result = func(*args, **kwargs)
        end = time.time()
        return result, end - start
    except Exception as e:
        end = time.time()
        return None, end - start

def analyze_portfolio_performance():
    """Analisa performance dos endpoints de portfolio"""
    logger.info("=== ANÁLISE DE PERFORMANCE - PORTFOLIOS ===")
    
    # Usuário de teste (admin)
    usuario_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    
    # Testar endpoints críticos
    endpoints = [
        ("Dashboard", PortfolioService.get_dashboard, [usuario_id]),
        ("Lista Portfolios", PortfolioService.get_all, [usuario_id]),
    ]
    
    results = []
    
    for name, func, args in endpoints:
        logger.info(f"Testando: {name}")
        result, duration = time_query(func, *args)
        
        results.append({
            'endpoint': name,
            'duration': duration,
            'success': result is not None,
            'record_count': len(result) if isinstance(result, list) else 1
        })
        
        status = "✅" if result is not None else "❌"
        logger.info(f"  {status} {name}: {duration:.3f}s")
    
    return results

def analyze_transacoes_performance():
    """Analisa performance das queries de transações"""
    logger.info("\n=== ANÁLISE DE PERFORMANCE - TRANSAÇÕES ===")
    
    usuario_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    
    # Testar diferentes filtros
    test_cases = [
        ("Sem filtros", {}),
        ("Filtro tipo", {"tipo": ["COMPRA"]}),
        ("Filtro ativo", {"ativo_id": UUID("123e4567-e89b-12d3-a456-426614174001")}),
        ("Filtro data", {"data_inicio": "2024-01-01", "data_fim": "2024-12-31"}),
        ("Múltiplos filtros", {"tipo": ["COMPRA"], "data_inicio": "2024-01-01"}),
    ]
    
    results = []
    
    for name, filters in test_cases:
        logger.info(f"Testando: {name}")
        result, duration = time_query(
            TransacaoService.get_all, 
            usuario_id, 
            page=1, 
            per_page=50,
            **filters
        )
        
        results.append({
            'test_case': name,
            'duration': duration,
            'success': result is not None,
            'record_count': len(result.items) if result else 0
        })
        
        status = "✅" if result is not None else "❌"
        logger.info(f"  {status} {name}: {duration:.3f}s ({len(result.items) if result else 0} registros)")
    
    return results

def analyze_ativos_performance():
    """Analisa performance das queries de ativos"""
    logger.info("\n=== ANÁLISE DE PERFORMANCE - ATIVOS ===")
    
    # Testar diferentes consultas de ativos
    test_cases = [
        ("Lista todos", {}),
        ("Paginação 1", {"page": 1, "per_page": 20}),
        ("Paginação 5", {"page": 5, "per_page": 20}),
        ("Filtro tipo", {"tipo": "ACAO"}),
        ("Filtro mercado", {"mercado": "BR"}),
        ("Busca por ticker", {"ticker": "PETR4"}),
    ]
    
    results = []
    
    for name, params in test_cases:
        logger.info(f"Testando: {name}")
        result, duration = time_query(AtivoService.get_all, **params)
        
        results.append({
            'test_case': name,
            'duration': duration,
            'success': result is not None,
            'record_count': len(result.get('ativos', [])) if result else 0
        })
        
        status = "✅" if result is not None else "❌"
        count = len(result.get('ativos', [])) if result else 0
        logger.info(f"  {status} {name}: {duration:.3f}s ({count} registros)")
    
    return results

def check_missing_indexes():
    """Verifica índices que podem melhorar performance"""
    logger.info("\n=== ANÁLISE DE ÍNDICES ===")
    
    app = create_app()
    
    with app.app_context():
        # Queries que podem se beneficiar de índices
        critical_queries = [
            {
                'table': 'posicao',
                'where': 'usuario_id = ?',
                'recommendation': 'CREATE INDEX IF NOT EXISTS idx_posicao_usuario_id ON posicao(usuario_id);'
            },
            {
                'table': 'transacao',
                'where': 'usuario_id = ? AND data_transacao >= ?',
                'recommendation': 'CREATE INDEX IF NOT EXISTS idx_transacao_usuario_data ON transacao(usuario_id, data_transacao);'
            },
            {
                'table': 'transacao',
                'where': 'usuario_id = ? AND ativo_id = ?',
                'recommendation': 'CREATE INDEX IF NOT EXISTS idx_transacao_usuario_ativo ON transacao(usuario_id, ativo_id);'
            },
            {
                'table': 'plano_compra',
                'where': 'usuario_id = ? AND status = ?',
                'recommendation': 'CREATE INDEX IF NOT EXISTS idx_plano_usuario_status ON plano_compra(usuario_id, status);'
            },
            {
                'table': 'ativo',
                'where': 'ticker = ?',
                'recommendation': 'CREATE INDEX IF NOT EXISTS idx_ativo_ticker ON ativo(ticker);'
            }
        ]
        
        logger.info("Índices recomendados:")
        for query in critical_queries:
            logger.info(f"  📊 {query['table']}: {query['where']}")
            logger.info(f"     → {query['recommendation']}")

def generate_report():
    """Gera relatório completo de performance"""
    logger.info("\n" + "="*50)
    logger.info("RELATÓRIO DE PERFORMANCE - EXITUS")
    logger.info("="*50)
    
    # Coletar dados
    portfolio_results = analyze_portfolio_performance()
    transacoes_results = analyze_transacoes_performance()
    ativos_results = analyze_ativos_performance()
    check_missing_indexes()
    
    # Identificar problemas
    logger.info("\n=== PROBLEMAS IDENTIFICADOS ===")
    
    all_results = portfolio_results + transacoes_results + ativos_results
    
    for result in all_results:
        endpoint = result.get('endpoint') or result.get('test_case')
        duration = result['duration']
        
        if duration > 1.0:
            logger.warning(f"🐌 LENTO: {endpoint} - {duration:.3f}s")
        elif duration > 0.5:
            logger.warning(f"⚠️  ATENÇÃO: {endpoint} - {duration:.3f}s")
        else:
            logger.info(f"✅ OK: {endpoint} - {duration:.3f}s")
    
    # Recomendações
    logger.info("\n=== RECOMENDAÇÕES ===")
    logger.info("1. Implementar cache Redis para dashboard")
    logger.info("2. Adicionar índices faltantes")
    logger.info("3. Paginação eficiente para grandes volumes")
    logger.info("4. Lazy loading para relacionamentos")
    logger.info("5. Query otimizada para cálculo de patrimônio")

if __name__ == "__main__":
    generate_report()
