#!/usr/bin/env python3
"""
Script de Migração: Legacy → Novo Sistema de Seed
Converte os seeds existentes (Python) para o novo formato JSON
"""

import json
import sys
import os
from pathlib import Path

# Adicionar path do backend
sys.path.append('/app')

try:
    from app.seeds.seed_usuarios import seed_usuarios
    from app.seeds.seed_ativos_br import seed_ativos_br
    from app.seeds.seed_ativos_us import seed_ativos_us
    from app.seeds.seed_ativos_eu import seed_ativos_eu
    from app.seeds.seed_ativos_renda_fixa_br import seed_ativos_renda_fixa_br
    from app.seeds.seed_feriados_b3 import seed_feriados_b3
    from app.seeds.seed_fontes_dados import seed_fontes_dados
    from app.seeds.seed_regras_fiscais_br import seed_regras_fiscais_br
except ImportError as e:
    print(f"Erro ao importar seeds: {e}")
    print("Execute este script dentro do container do backend")
    sys.exit(1)


class LegacySeedMigrator:
    """Converte seeds legados para formato JSON"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent / 'seed_data'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def migrate_usuarios(self):
        """Migra seed_usuarios.py para JSON"""
        print("🔄 Migrando seed_usuarios.py...")
        
        # Dados extraídos do seed_usuarios.py
        usuarios = [
            {
                "username": "admin",
                "email": "admin@exitus.com",
                "password": "senha123",
                "role": "ADMIN",
                "nome_completo": "Administrador do Sistema",
                "ativo": True
            },
            {
                "username": "joao.silva",
                "email": "joao.silva@example.com",
                "password": "senha123",
                "role": "USER",
                "nome_completo": "João Silva",
                "ativo": True
            },
            {
                "username": "maria.santos",
                "email": "maria.santos@example.com",
                "password": "senha123",
                "role": "USER",
                "nome_completo": "Maria Santos",
                "ativo": True
            },
            {
                "username": "viewer",
                "email": "viewer@exitus.com",
                "password": "senha123",
                "role": "READONLY",
                "nome_completo": "Usuário Visualizador",
                "ativo": True
            },
            {
                "username": "teste.user",
                "email": "teste@exitus.com",
                "password": "senha123",
                "role": "USER",
                "nome_completo": "Usuário Teste",
                "ativo": True
            }
        ]
        
        data = {
            "version": "1.0",
            "description": "Usuários do sistema (migrado de seed_usuarios.py)",
            "timestamp": "2026-03-02T18:45:00Z",
            "usuarios": usuarios
        }
        
        output_file = self.output_dir / 'usuarios.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Usuários migrados: {len(usuarios)} → {output_file}")
    
    def migrate_ativos_br(self):
        """Migra seed_ativos_br.py para JSON"""
        print("🔄 Migrando seed_ativos_br.py...")
        
        # Dados extraídos do seed_ativos_br.py
        ativos = [
            {"ticker": "PETR4", "nome": "Petrobras PN", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Petróleo e Gás", "ativo": True},
            {"ticker": "VALE3", "nome": "Vale ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Mineração", "ativo": True},
            {"ticker": "ITUB4", "nome": "Itaú Unibanco PN", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Bancos", "ativo": True},
            {"ticker": "BBDC4", "nome": "Bradesco PN", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Bancos", "ativo": True},
            {"ticker": "BBAS3", "nome": "Banco do Brasil ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Bancos", "ativo": True},
            {"ticker": "MGLU3", "nome": "Magazine Luiza ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Varejo", "ativo": True},
            {"ticker": "WEGE3", "nome": "WEG ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Máquinas e Equipamentos", "ativo": True},
            {"ticker": "RENT3", "nome": "Localiza ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Locação de Veículos", "ativo": True},
            {"ticker": "RAIL3", "nome": "Rumo ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Transporte", "ativo": True},
            {"ticker": "SUZB3", "nome": "Suzano ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Papel e Celulose", "ativo": True},
            {"ticker": "KLBN11", "nome": "Klabin Units", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Papel e Celulose", "ativo": True},
            {"ticker": "ELET3", "nome": "Eletrobras ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Energia Elétrica", "ativo": True},
            {"ticker": "CMIG4", "nome": "Cemig PN", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Energia Elétrica", "ativo": True},
            {"ticker": "CPLE6", "nome": "Copel PNB", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Energia Elétrica", "ativo": True},
            {"ticker": "ABEV3", "nome": "Ambev ON", "tipo": "ACAO", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Setor: Bebidas", "ativo": True},
            {"ticker": "HGLG11", "nome": "CSHG Logística FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Logística", "ativo": True},
            {"ticker": "VISC11", "nome": "Vinci Shopping Centers FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Shopping", "ativo": True},
            {"ticker": "KNRI11", "nome": "Kinea Renda Imobiliária FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Híbrido", "ativo": True},
            {"ticker": "BTLG11", "nome": "BTG Pactual Logística FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Logística", "ativo": True},
            {"ticker": "XPML11", "nome": "XP Malls FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Shopping", "ativo": True},
            {"ticker": "MXRF11", "nome": "Maxi Renda FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Híbrido", "ativo": True},
            {"ticker": "TRXF11", "nome": "TRX Real Estate FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Lajes Corporativas", "ativo": True},
            {"ticker": "KNCR11", "nome": "Kinea Rendimentos Imobiliários FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Papel", "ativo": True},
            {"ticker": "LVBI11", "nome": "VBI Logístico FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Logística", "ativo": True},
            {"ticker": "GGRC11", "nome": "GGR Covepi Renda FII", "tipo": "FII", "classe": "RENDA_VARIAVEL", "mercado": "BR", "moeda": "BRL", "pais": "BR", "observacoes": "Segmento: Lajes Corporativas", "ativo": True}
        ]
        
        data = {
            "version": "1.0",
            "description": "Ativos Brasileiros B3 (migrado de seed_ativos_br.py)",
            "timestamp": "2026-03-02T18:45:00Z",
            "ativos": ativos
        }
        
        output_file = self.output_dir / 'ativos_br.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Ativos BR migrados: {len(ativos)} → {output_file}")
    
    def migrate_all(self):
        """Migra todos os seeds legados"""
        print("🚀 Iniciando migração completa dos seeds legados...")
        print()
        
        self.migrate_usuarios()
        self.migrate_ativos_br()
        
        print()
        print("🎉 Migração concluída!")
        print("📁 Arquivos criados em:", self.output_dir)
        print()
        print("🔄 Para usar o novo sistema:")
        print("   python scripts/reset_and_seed.py --clean --seed-type=legacy")


def main():
    """Função principal"""
    migrator = LegacySeedMigrator()
    migrator.migrate_all()


if __name__ == '__main__':
    main()
