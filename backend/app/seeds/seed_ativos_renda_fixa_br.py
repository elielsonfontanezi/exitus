#!/usr/bin/env python3
"""
Seed para Renda Fixa BR - Sistema Exitus v0.7.8 (Método correto via Flask app)
Adiciona 8 ativos Renda Fixa BR: 3 CDBs, 3 Tesouro Direto, 2 Debêntures
Idempotente (verifica ticker+mercado)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.ativo import Ativo

def seed_renda_fixa_br():
    """Seed idempotente para 8 ativos Renda Fixa BR"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Iniciando Seed Renda Fixa BR...")
        
        ativos_renda_fixa_br = [
            # CDBs
            {"ticker": "CDBNUBANK100CDI", "nome": "Nubank CDB 100% do CDI", "tipo": "cdb", "observacoes": "Liquidez D+0, mínimo R$1.000,00, rendimento 100% CDI", "preco_atual": 1000.00},
            {"ticker": "CDBINTER105CDI", "nome": "Banco Inter CDB 105% do CDI", "tipo": "cdb", "observacoes": "Liquidez D+1, mínimo R$1.000,00, rendimento 105% CDI (>R$500k)", "preco_atual": 1000.00},
            {"ticker": "CDBC6107CDI", "nome": "C6 Bank CDB 107% do CDI", "tipo": "cdb", "observacoes": "Liquidez D+0, mínimo R$1.000,00, rendimento 107% CDI (>R$1M)", "preco_atual": 1000.00},
            # Tesouro Direto
            {"ticker": "TESOUROSELIC2029", "nome": "Tesouro Selic 2029", "tipo": "tesouro_direto", "observacoes": "Vencimento 01/03/2029, rentabilidade Selic + 0,00%", "preco_atual": 920.45},
            {"ticker": "TESOUROIPCA2035", "nome": "Tesouro IPCA+ 2035", "tipo": "tesouro_direto", "observacoes": "Vencimento 15/08/2035, rentabilidade IPCA + 5,82%", "preco_atual": 4500.20},
            {"ticker": "TESOUROPREFIX2027", "nome": "Tesouro Prefixado 2027", "tipo": "tesouro_direto", "observacoes": "Vencimento 01/01/2027, rentabilidade 11,85% a.a.", "preco_atual": 880.75},
            # Debêntures
            {"ticker": "VALE23DBNT", "nome": "Vale Debênture 2023 NT", "tipo": "debenture", "observacoes": "Debênture Não Tributável, cupom 7,5% a.a., vencimento 2030", "preco_atual": 1050.30},
            {"ticker": "PETR4DBNT", "nome": "Petrobras Debênture NT", "tipo": "debenture", "observacoes": "Debênture Não Tributável, cupom CDI + 2,0%, vencimento 2028", "preco_atual": 1025.80}
        ]
        
        total_criados = 0
        
        for ativo_data in ativos_renda_fixa_br:
            existente = Ativo.query.filter_by(
                ticker=ativo_data["ticker"],
                mercado="BR"
            ).first()
            
            if existente:
                print(f"✅ Já existe: {ativo_data['ticker']} ({ativo_data['nome'][:30]}...)")
                continue
            
            novo_ativo = Ativo(
                ticker=ativo_data["ticker"],
                nome=ativo_data["nome"],
                tipo=ativo_data["tipo"],
                classe="renda_fixa",
                mercado="BR",
                moeda="BRL",
                preco_atual=ativo_data["preco_atual"],
                observacoes=ativo_data["observacoes"],
                ativo=True,
                deslistado=False
            )
            
            db.session.add(novo_ativo)
            db.session.commit()
            total_criados += 1
            print(f"🆕 Criado: {ativo_data['ticker']} ({ativo_data['nome'][:30]}...)")
        
        print(f"\n🎉 Seed concluído: {total_criados}/8 novos ativos Renda Fixa BR criados!")
        print("💾 Agora valide com: podman exec exitus-db psql -U exitus -d exitusdb -c \"SELECT ticker,nome,tipo FROM ativo WHERE mercado='BR' AND tipo IN('CDB','TESOURO_DIRETO','DEBENTURE');\"")

if __name__ == "__main__":
    seed_renda_fixa_br()
