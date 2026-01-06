#!/usr/bin/env python3
"""
Script para popular histórico de preços inicial
Uso: python scripts/popular_historico_inicial.py [--dias 365] [--ticker PETR4]
"""
import sys
import os
import argparse
from datetime import datetime

# Adicionar path do app
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Adicionar path do app (2 níveis acima: /app/app/scripts -> /app)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app
from app.database import db
from app.models.ativo import Ativo
from app.services.historico_service import HistoricoService

def popular_historico(dias=365, ticker_filtro=None, apenas_ativos=True):
    """Popula histórico de preços dos ativos."""
    app = create_app()
    
    with app.app_context():
        query = Ativo.query
        
        if ticker_filtro:
            query = query.filter_by(ticker=ticker_filtro.upper())
        
        if apenas_ativos:
            query = query.filter_by(ativo=True, deslistado=False)
        
        ativos = query.all()
        
        if not ativos:
            print(f"❌ Nenhum ativo encontrado")
            return
        
        print(f"🚀 Iniciando população de histórico")
        print(f"📊 Total de ativos: {len(ativos)}")
        print(f"📅 Dias a buscar: {dias}\n")
        print("=" * 60)
        
        stats = {'processados': 0, 'sucesso': 0, 'sem_dados': 0, 'erro': 0, 'total_registros': 0}
        
        for i, ativo in enumerate(ativos, 1):
            try:
                print(f"[{i}/{len(ativos)}] {ativo.ticker} ({ativo.mercado})...", end=" ", flush=True)
                
                historico = HistoricoService.obter_ou_criar_historico(str(ativo.id), dias=dias)
                
                stats['processados'] += 1
                
                if len(historico) > 0:
                    stats['sucesso'] += 1
                    stats['total_registros'] += len(historico)
                    print(f"✅ {len(historico)} registros")
                else:
                    stats['sem_dados'] += 1
                    print("⚠️ Sem dados")
                
            except Exception as e:
                stats['erro'] += 1
                print(f"❌ Erro: {str(e)[:50]}")
                continue
        
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL")
        print("=" * 60)
        print(f"✅ Processados: {stats['sucesso']}")
        print(f"⚠️ Sem dados: {stats['sem_dados']}")
        print(f"❌ Erros: {stats['erro']}")
        print(f"📈 Total registros: {stats['total_registros']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Popular histórico de preços')
    parser.add_argument('--dias', type=int, default=365, help='Dias (default: 365)')
    parser.add_argument('--ticker', type=str, default=None, help='Ticker específico')
    parser.add_argument('--incluir-deslistados', action='store_true', help='Incluir deslistados')
    
    args = parser.parse_args()
    
    popular_historico(
        dias=args.dias,
        ticker_filtro=args.ticker,
        apenas_ativos=not args.incluir_deslistados
    )
