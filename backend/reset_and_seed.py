#!/usr/bin/env python3
"""
Script de reset e seed controlado do banco Exitus
Uso: ./scripts/reset_and_seed.sh [--clean] [--seed-type=full|minimal|custom]
"""

import argparse
import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Adicionar path do backend
sys.path.append('./backend')

try:
    from app import create_app
    from app.database import db
    from app.models.usuario import Usuario, UserRole
    from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
    from app.models.corretora import Corretora
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Execute este script na raiz do projeto")
    sys.exit(1)


class SeedManager:
    """Gerenciador de seed do banco de dados"""
    
    def __init__(self):
        self.app = create_app()
        # Suporta execução via container (/app/seed_data) ou direto (scripts/seed_data)
        container_seed_dir = Path('/app/seed_data')
        local_seed_dir = Path(__file__).parent / 'seed_data'
        self.seed_dir = container_seed_dir if container_seed_dir.exists() else local_seed_dir
        self.scenarios_dir = self.seed_dir / 'scenarios'
        
    def reset_database(self):
        """Reset completo do banco (apenas dados, preservando schema)"""
        print("🔄 Resetando banco de dados...")
        
        with self.app.app_context():
            from sqlalchemy import text, inspect
            
            # LIÇÃO 002: Sempre consultar tabelas reais, nunca deduzir
            inspector = inspect(db.engine)
            all_tables = set(inspector.get_table_names())
            print(f"📋 Tabelas encontradas no banco: {sorted(all_tables)}")
            
            # Tabelas de controle que NÃO devem ser limpas
            skip_tables = {'alembic_version'}
            
            # Ordem de DELETE respeitando dependências FK
            # (dependentes primeiro, pais depois)
            ordered_tables = [
                'calendario_dividendo',
                'evento_custodia',
                'evento_corporativo',
                'movimentacao_caixa',
                'provento',
                'transacao',
                'posicao',
                'alertas',
                'configuracoes_alertas',
                'projecoes_renda',
                'plano_compra',
                'plano_venda',
                'relatorios_performance',
                'auditoria_relatorios',
                'log_auditoria',
                'historico_preco',
                'historico_patrimonio',
                'portfolio',
                'saldo_darf_acumulado',
                'saldo_prejuizo',
                'taxa_cambio',
                'corretora',
                'ativo',
                'usuario',
                'assessora',
                'feriado_mercado',
                'fonte_dados',
                'regra_fiscal',
                'parametros_macro',
            ]
            
            # Filtrar apenas tabelas que existem de fato no banco
            tables_to_clean = [t for t in ordered_tables if t in all_tables and t not in skip_tables]
            
            # Adicionar tabelas encontradas no banco mas não na lista ordenada
            unlisted = all_tables - set(ordered_tables) - skip_tables
            if unlisted:
                print(f"⚠️  Tabelas no banco não cobertas pela lista: {sorted(unlisted)}")
            
            try:
                # Limpar dados de todas as tabelas
                for table in tables_to_clean:
                    try:
                        result = db.session.execute(text(f"DELETE FROM {table}"))
                        print(f"✅ {table}: {result.rowcount} registros removidos")
                    except Exception as e:
                        db.session.rollback()
                        print(f"⚠️  Erro em {table}: {e}")
                
                # Nota: PKs são UUID, não há sequences para resetar
                db.session.commit()
                print("✅ Banco resetado com sucesso (dados apenas)")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao resetar banco: {e}")
                raise
    
    def load_seed_data(self, seed_type='minimal'):
        """Carregar dados de seed (suporta múltiplos arquivos)"""
        
        # Mapeamento de seed types para arquivos
        seed_files = {
            'minimal': ['minimal.json'],
            'full': ['usuarios.json', 'ativos_br.json', 'ativos_us.json', 'ativos_eu.json', 'full.json'],
            'usuarios': ['usuarios.json'],
            'ativos': ['ativos_br.json', 'ativos_us.json', 'ativos_eu.json'],
            'legacy': ['usuarios.json', 'ativos_br.json', 'ativos_renda_fixa_br.json', 'feriados_b3.json', 'fontes_dados.json', 'regras_fiscais_br.json']
        }
        
        if seed_type not in seed_files:
            print(f"❌ Tipo de seed inválido: {seed_type}")
            print(f"   Tipos disponíveis: {list(seed_files.keys())}")
            return False
        
        files_to_load = seed_files[seed_type]
        print(f"📊 Carregando seed: {seed_type} ({len(files_to_load)} arquivos)")
        
        total_data = {
            'usuarios': [],
            'ativos': [],
            'corretoras': [],
            'feriados': [],
            'fontes_dados': [],
            'regras_fiscais': []
        }
        
        # Carregar e combinar dados de múltiplos arquivos
        for filename in files_to_load:
            file_path = self.seed_dir / filename
            
            if not file_path.exists():
                print(f"⚠️  Arquivo não encontrado: {filename}")
                continue
            
            print(f"📁 Carregando: {filename}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Combinar dados
            for key in total_data.keys():
                if key in data:
                    if isinstance(data[key], list):
                        total_data[key].extend(data[key])
                    else:
                        print(f"⚠️  Campo {key} não é lista em {filename}")
        
        # Remover duplicados
        for key in total_data.keys():
            if key in ['usuarios', 'ativos', 'corretoras']:
                # Remover duplicados por campo único
                unique_field = {'usuarios': 'username', 'ativos': 'ticker', 'corretoras': 'nome'}[key]
                seen = set()
                unique_items = []
                
                for item in total_data[key]:
                    field_value = item.get(unique_field)
                    if field_value and field_value not in seen:
                        seen.add(field_value)
                        unique_items.append(item)
                
                total_data[key] = unique_items
                print(f"✅ {key}: {len(unique_items)} itens únicos")
        
        # Inserir dados no banco
        with self.app.app_context():
            try:
                # Seed usuários
                if total_data['usuarios']:
                    self._seed_usuarios(total_data['usuarios'])
                
                # Seed ativos
                if total_data['ativos']:
                    self._seed_ativos(total_data['ativos'])
                
                # Seed corretoras
                if total_data['corretoras']:
                    self._seed_corretoras(total_data['corretoras'])
                
                # Seed feriados (se existir função)
                if total_data['feriados']:
                    self._seed_feriados(total_data['feriados'])
                
                # Seed fontes de dados (se existir função)
                if total_data['fontes_dados']:
                    self._seed_fontes_dados(total_data['fontes_dados'])
                
                # Seed regras fiscais (se existir função)
                if total_data['regras_fiscais']:
                    self._seed_regras_fiscais(total_data['regras_fiscais'])
                
                db.session.commit()
                print(f"✅ Seed {seed_type} carregado com sucesso")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao carregar seed: {e}")
                return False
    
    def _seed_usuarios(self, usuarios_data):
        """Seed de usuários"""
        print(f"👥 Criando {len(usuarios_data)} usuários...")
        
        for user_data in usuarios_data:
            # Verificar se usuário já existe
            existing = Usuario.query.filter_by(username=user_data['username']).first()
            if existing:
                print(f"⚠️  Usuário {user_data['username']} já existe, pulando...")
                continue
            
            # Mapear role string para enum
            role_map = {
                'ADMIN': UserRole.ADMIN,
                'USER': UserRole.USER,
                'READONLY': UserRole.READONLY
            }
            
            usuario = Usuario(
                username=user_data['username'],
                email=user_data['email'],
                nome_completo=user_data.get('nome_completo', user_data['username']),
                role=role_map.get(user_data['role'], UserRole.USER),
                password_hash=generate_password_hash(user_data['password']),
                ativo=user_data.get('ativo', True),
            )
            
            db.session.add(usuario)
            print(f"✅ Usuário criado: {user_data['username']}")
    
    def _seed_ativos(self, ativos_data):
        """Seed de ativos"""
        print(f"📈 Criando {len(ativos_data)} ativos...")
        
        for ativo_data in ativos_data:
            # Verificar se ativo já existe
            existing = Ativo.query.filter_by(ticker=ativo_data['ticker']).first()
            if existing:
                print(f"⚠️  Ativo {ativo_data['ticker']} já existe, pulando...")
                continue
            
            # Mapear tipo string para enum
            tipo_map = {
                'ACAO': TipoAtivo.ACAO,
                'FII': TipoAtivo.FII,
                'STOCK': TipoAtivo.STOCK,
                'ETF': TipoAtivo.ETF,
                'REIT': TipoAtivo.REIT
            }
            
            # Mapear classe (padrão RENDA_VARIAVEL para a maioria)
            classe_map = {
                'ACAO': ClasseAtivo.RENDA_VARIAVEL,
                'FII': ClasseAtivo.RENDA_VARIAVEL,
                'STOCK': ClasseAtivo.RENDA_VARIAVEL,
                'ETF': ClasseAtivo.RENDA_VARIAVEL,
                'REIT': ClasseAtivo.RENDA_VARIAVEL
            }
            
            ativo = Ativo(
                ticker=ativo_data['ticker'],
                nome=ativo_data['nome'],
                mercado=ativo_data.get('mercado', 'BR'),
                tipo=tipo_map.get(ativo_data['tipo'], TipoAtivo.ACAO),
                classe=ativo_data.get('classe') and ClasseAtivo[ativo_data['classe']] or classe_map.get(ativo_data['tipo'], ClasseAtivo.RENDA_VARIAVEL),
                moeda=ativo_data.get('moeda', 'BRL'),
                observacoes=ativo_data.get('observacoes'),
                ativo=ativo_data.get('ativo', True),
            )
            
            db.session.add(ativo)
            print(f"✅ Ativo criado: {ativo_data['ticker']}")
    
    def _seed_corretoras(self, corretoras_data):
        """Seed de corretoras"""
        print(f"🏦 Criando {len(corretoras_data)} corretoras...")
        
        for corretora_data in corretoras_data:
            # Verificar se corretora já existe
            existing = Corretora.query.filter_by(nome=corretora_data['nome']).first()
            if existing:
                print(f"⚠️  Corretora {corretora_data['nome']} já existe, pulando...")
                continue
            
            # Obter primeiro usuário admin para associar
            admin_user = Usuario.query.filter_by(role=UserRole.ADMIN).first()
            
            corretora = Corretora(
                nome=corretora_data['nome'],
                usuario_id=admin_user.id if admin_user else None,
                ativa=corretora_data.get('ativa', True),
                pais='BR',
                moeda_padrao='BRL',
                saldo_atual=0,
            )
            
            db.session.add(corretora)
            print(f"✅ Corretora criada: {corretora_data['nome']}")
    
    def backup_scenario(self, scenario_name):
        """Backup do cenário atual"""
        print(f"💾 Criando backup do cenário: {scenario_name}")
        
        scenario_file = self.scenarios_dir / f'{scenario_name}.json'
        scenario_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self.app.app_context():
            # Coletar dados atuais
            data = {
                'version': '1.0',
                'description': f'Backup do cenário {scenario_name}',
                'timestamp': datetime.utcnow().isoformat(),
                'usuarios': self._export_usuarios(),
                'ativos': self._export_ativos(),
                'corretoras': self._export_corretoras()
            }
        
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Backup salvo em: {scenario_file}")
    
    def _export_usuarios(self):
        """Exportar usuários"""
        usuarios = Usuario.query.all()
        return [
            {
                'username': u.username,
                'email': u.email,
                'nome_completo': u.nome_completo,
                'role': u.role.value,
                'ativo': u.ativo
            }
            for u in usuarios
        ]
    
    def _export_ativos(self):
        """Exportar ativos"""
        ativos = Ativo.query.all()
        return [
            {
                'ticker': a.ticker,
                'nome': a.nome,
                'mercado': a.mercado,
                'tipo': a.tipo.value,
                'classe': a.classe.value,
                'moeda': a.moeda,
                'ativo': a.ativo
            }
            for a in ativos
        ]
    
    def _export_corretoras(self):
        """Exportar corretoras"""
        corretoras = Corretora.query.all()
        return [
            {
                'nome': c.nome,
                'ativa': c.ativa
            }
            for c in corretoras
        ]
    
    def _seed_feriados(self, feriados_data):
        """Seed de feriados (placeholder para implementação futura)"""
        print(f"📅 {len(feriados_data)} feriados (não implementado ainda)")
        # TODO: Implementar quando tiver modelo Feriado
        pass
    
    def _seed_fontes_dados(self, fontes_data):
        """Seed de fontes de dados (placeholder para implementação futura)"""
        print(f"📊 {len(fontes_data)} fontes de dados (não implementado ainda)")
        # TODO: Implementar quando tiver modelo FonteDados
        pass
    
    def _seed_regras_fiscais(self, regras_data):
        """Seed de regras fiscais (placeholder para implementação futura)"""
        print(f"📋 {len(regras_data)} regras fiscais (não implementado ainda)")
        # TODO: Implementar quando tiver modelo RegraFiscal
        pass
    
    def restore_scenario(self, scenario_name):
        """Restaurar cenário salvo"""
        scenario_file = self.scenarios_dir / f'{scenario_name}.json'
        
        if not scenario_file.exists():
            print(f"❌ Cenário não encontrado: {scenario_file}")
            return False
        
        print(f"🔄 Restaurando cenário: {scenario_name}")
        
        # Reset banco primeiro
        self.reset_database()
        
        # Carregar cenário
        with open(scenario_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with self.app.app_context():
            try:
                # Restaurar dados
                if 'usuarios' in data:
                    self._seed_usuarios(data['usuarios'])
                if 'ativos' in data:
                    self._seed_ativos(data['ativos'])
                if 'corretoras' in data:
                    self._seed_corretoras(data['corretoras'])
                
                db.session.commit()
                print(f"✅ Cenário {scenario_name} restaurado com sucesso")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao restaurar cenário: {e}")
                return False


def show_help():
    """Mostra ajuda detalhada com exemplos"""
    help_text = """
🚀 EXITUS - Sistema de Seed Controlado

📋 FORMAS DE EXECUÇÃO:

1️⃣ RESET + SEED BÁSICO:
   python scripts/reset_and_seed.py --clean --seed-type=minimal
   → 3 usuários, 3 ativos, 2 corretoras

2️⃣ RESET + SEED COMPLETO:
   python scripts/reset_and_seed.py --clean --seed-type=full
   → 5 usuários, 35+ ativos, 5 corretoras

3️⃣ CENÁRIO DE TESTE COMPLETO (NOVO):
   python scripts/reset_and_seed.py --clean --scenario test_full
   → Usuários, ativos, transações, movimentações, alertas, portfolios, planos

4️⃣ CENÁRIO E2E:
   python scripts/reset_and_seed.py --clean --scenario test_e2e
   → Dados realistas para testes E2E

5️⃣ CENÁRIO IR:
   python scripts/reset_and_seed.py --clean --scenario test_ir
   → Dados específicos para testes de Imposto de Renda

6️⃣ APENAS USUÁRIOS:
   python scripts/reset_and_seed.py --clean --seed-type=usuarios
   → 5 usuários completos

7️⃣ APENAS ATIVOS:
   python scripts/reset_and_seed.py --clean --seed-type=ativos
   → Ativos BR, US, EU

8️⃣ LEGACY COMPLETO:
   python scripts/reset_and_seed.py --clean --seed-type=legacy
   → Equivalente ao run_all_seeds.py antigo

🔄 BACKUP/RESTORE:

6️⃣ BACKUP DO CENÁRIO ATUAL:
   python scripts/reset_and_seed.py --backup meu_teste

7️⃣ RESTAURAR CENÁRIO:
   python scripts/reset_and_seed.py --restore meu_teste

8️⃣ LISTAR CENÁRIOS:
   python scripts/reset_and_seed.py --list-scenarios

🎯 COMPARAÇÃO COM LEGACY:

❌ ANTIGO (múltiplos scripts):
   python backend/app/seeds/run_all_seeds.py
   python backend/app/seeds/seed_usuarios.py
   python backend/app/seeds/seed_ativos_br.py

✅ NOVO (único script):
   python scripts/reset_and_seed.py --clean --seed-type=full

📊 TIPOS DE SEED:
   minimal → Dados básicos para testes rápidos
   full    → Todos os dados para desenvolvimento
   usuarios→ Apenas usuários do sistema
   ativos  → Apenas ativos (BR, US, EU)
   legacy  → Equivalente ao sistema antigo

🔧 OPÇÕES:
   --clean         → Reset completo do banco
   --seed-type     → Tipo de seed (default: minimal)
   --scenario      → Carregar cenário de teste JSON (test_full, test_e2e, test_ir)
   --backup        → Nome do cenário para backup
   --restore       → Nome do cenário para restaurar
   --list-scenarios→ Listar cenários disponíveis

📁 ESTRUTURA DE ARQUIVOS:
   scripts/seed_data/
   ├── minimal.json      → Seed básico
   ├── usuarios.json     → Usuários completos
   ├── ativos_br.json    → Ativos brasileiros
   ├── full.json         → Seed completo
   └── scenarios/        → Cenários de backup

⚠️ IMPORTANTE:
   - Execute na raiz do projeto (como outros scripts)
   - --clean apaga TODOS os dados
   - Backup salva estado atual para restore
   - Legacy mantém compatibilidade total
"""
    print(help_text)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Reset e seed controlado do banco Exitus',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/reset_and_seed.py --clean --seed-type=minimal
  python scripts/reset_and_seed.py --clean --scenario test_full
  python scripts/reset_and_seed.py --backup meu_teste
  python scripts/reset_and_seed.py --restore meu_teste
  python scripts/reset_and_seed.py --list-scenarios
        """
    )
    
    parser.add_argument('--clean', action='store_true', help='Reset completo do banco')
    parser.add_argument('--seed-type', choices=['minimal', 'full', 'usuarios', 'ativos', 'legacy'], 
                       default='minimal', help='Tipo de seed (default: minimal)')
    parser.add_argument('--scenario', help='Nome do cenário de teste JSON (test_full, test_e2e, test_ir)')
    parser.add_argument('--backup', help='Nome do cenário para backup')
    parser.add_argument('--restore', help='Nome do cenário para restaurar')
    parser.add_argument('--list-scenarios', action='store_true', help='Listar cenários disponíveis')
    parser.add_argument('--help-examples', action='store_true', help='Mostrar ajuda detalhada com exemplos')
    
    args = parser.parse_args()
    
    if args.help_examples:
        show_help()
        return
    
    manager = SeedManager()
    
    # Listar cenários
    if args.list_scenarios:
        scenarios = list(manager.scenarios_dir.glob('*.json')) if manager.scenarios_dir.exists() else []
        if scenarios:
            print("📋 Cenários disponíveis:")
            for scenario in scenarios:
                print(f"  - {scenario.stem}")
        else:
            print("❌ Nenhum cenário encontrado")
        return
    
    # Backup
    if args.backup:
        manager.backup_scenario(args.backup)
        return
    
    # Restore
    if args.restore:
        manager.restore_scenario(args.restore)
        return
    
    # Reset + Seed
    if args.clean:
        manager.reset_database()
    
    # Carregar cenário JSON se especificado
    if args.scenario:
        from load_scenario import ScenarioLoader
        loader = ScenarioLoader()
        loader.load_scenario(args.scenario)
        success = loader.seed_all()
    else:
        success = manager.load_seed_data(args.seed_type)
    
    if success:
        print("🎉 Operação concluída com sucesso!")
    else:
        print("❌ Operação falhou!")
        sys.exit(1)


if __name__ == '__main__':
    main()
