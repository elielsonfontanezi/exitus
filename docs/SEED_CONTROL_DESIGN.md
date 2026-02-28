# Design: Sistema de Seed/Reset Controlado

> **GAP:** EXITUS-SEED-001  
> **Objetivo:** Permitir reset e populate controlado do banco para testes  
> **Data:** 28 de Fevereiro de 2026

---

## 🎯 Problema Atual

- DB acumula dados de testes anteriores
- Sem forma de voltar ao estado inicial conhecido
- Testes inconsistentes
- Debug difícil sem ambiente limpo

---

## 📋 Requisitos

### Funcionais
1. **Reset completo** do banco (drop + recreate)
2. **Seed controlado** com diferentes níveis de dados
3. **Backup/Restore** de cenários específicos
4. **Integração com pytest** (fixtures)
5. **Execução via linha de comando**

### Não-funcionais
- **Performance:** Reset < 30 segundos
- **Segurança:** Apenas ambiente dev/teste
- **Flexibilidade:** Múltiplos tipos de seed
- **Idempotência:** Pode rodar múltiplas vezes

---

## 🏗️ Arquitetura Proposta

### 1. Scripts Principais

```
scripts/
├── reset_and_seed.py          # Script principal
├── backup_test_data.py        # Backup/Restore de cenários
└── seed_data/                  # Dados de seed
    ├── minimal.json           # Dados mínimos
    ├── full.json              # Dados completos
    └── scenarios/             # Cenários específicos
        ├── import_test.json
        ├── crud_test.json
        └── performance_test.json
```

### 2. Estrutura de Dados

```json
// seed_data/minimal.json
{
  "version": "1.0",
  "description": "Dados mínimos para testes básicos",
  "usuarios": [
    {
      "username": "test_admin",
      "email": "admin@test.com",
      "role": "ADMIN",
      "nome_completo": "Administrador Teste"
    },
    {
      "username": "test_user",
      "email": "user@test.com", 
      "role": "USER",
      "nome_completo": "Usuário Teste"
    }
  ],
  "ativos": [
    {
      "ticker": "PETR4",
      "nome": "PETROBRAS",
      "tipo": "ACAO",
      "pais": "BR",
      "moeda": "BRL"
    }
  ]
}
```

---

## ⚙️ Implementação

### 1. Script Principal (reset_and_seed.py)

```python
#!/usr/bin/env python3
"""
Script de reset e seed controlado do banco Exitus
Uso: python scripts/reset_and_seed.py [--clean] [--seed-type=full|minimal|custom]
"""

import argparse
import sys
import os
from pathlib import Path

# Adicionar backend ao path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from backend.app import create_app, db
from backend.app.models.usuario import Usuario
from backend.app.models.ativo import Ativo
import json

def reset_database():
    """Drop e recreate todas as tabelas"""
    print("🔄 Resetando banco de dados...")
    db.drop_all()
    db.create_all()
    print("✅ Banco resetado")

def seed_minimal():
    """Seed com dados mínimos"""
    print("📝 Populando dados mínimos...")
    
    # Criar usuários básicos
    admin = Usuario(
        username="test_admin",
        email="admin@test.com",
        role="ADMIN",
        nome_completo="Administrador Teste"
    )
    admin.set_password("senha123")
    
    user = Usuario(
        username="test_user", 
        email="user@test.com",
        role="USER",
        nome_completo="Usuário Teste"
    )
    user.set_password("senha123")
    
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
    print("✅ Seed minimal concluído")

def seed_full():
    """Seed com dados completos (56 ativos, transações, etc.)"""
    print("📝 Populando dados completos...")
    
    # Seed minimal primeiro
    seed_minimal()
    
    # Carregar dados completos do JSON
    with open('scripts/seed_data/full.json', 'r') as f:
        data = json.load(f)
    
    # Criar ativos
    for ativo_data in data['ativos']:
        ativo = Ativo(**ativo_data)
        db.session.add(ativo)
    
    # Criar outros dados (transações, posições, etc.)
    # ... implementação
    
    db.session.commit()
    print("✅ Seed full concluído")

def seed_custom(scenario_file):
    """Seed com arquivo customizado"""
    print(f"📝 Populando cenário custom: {scenario_file}")
    
    with open(scenario_file, 'r') as f:
        data = json.load(f)
    
    # Implementar seed customizado
    # ... implementação
    
    print("✅ Seed custom concluído")

def main():
    parser = argparse.ArgumentParser(description='Reset e seed do banco Exitus')
    parser.add_argument('--clean', action='store_true', help='Reset completo do banco')
    parser.add_argument('--seed-type', choices=['minimal', 'full', 'custom'], 
                       default='minimal', help='Tipo de seed')
    parser.add_argument('--scenario', help='Arquivo JSON para seed customizado')
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.clean:
            reset_database()
        
        if args.seed_type == 'minimal':
            seed_minimal()
        elif args.seed_type == 'full':
            seed_full()
        elif args.seed_type == 'custom':
            if not args.scenario:
                print("❌ --scenario obrigatório para seed customizado")
                sys.exit(1)
            seed_custom(args.scenario)
        
        print("\n🎉 Banco pronto para testes!")

if __name__ == "__main__":
    main()
```

### 2. Backup/Restore (backup_test_data.py)

```python
#!/usr/bin/env python3
"""
Backup e restore de cenários de teste
Uso: python scripts/backup_test_data.py --save|--restore scenario_name
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# ... imports do backend

def backup_scenario(scenario_name):
    """Salva estado atual do banco como cenário"""
    print(f"💾 Salvando cenário: {scenario_name}")
    
    # Coletar dados do banco
    data = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "usuarios": [user.to_dict() for user in Usuario.query.all()],
        "ativos": [ativo.to_dict() for ativo in Ativo.query.all()],
        # ... outras tabelas
    }
    
    # Salvar em arquivo
    scenario_file = Path(f"scripts/seed_data/scenarios/{scenario_name}.json")
    scenario_file.parent.mkdir(exist_ok=True)
    
    with open(scenario_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Cenário salvo: {scenario_file}")

def restore_scenario(scenario_name):
    """Restaura cenário salvo"""
    print(f"🔄 Restaurando cenário: {scenario_name}")
    
    scenario_file = Path(f"scripts/seed_data/scenarios/{scenario_name}.json")
    
    if not scenario_file.exists():
        print(f"❌ Cenário não encontrado: {scenario_file}")
        sys.exit(1)
    
    with open(scenario_file, 'r') as f:
        data = json.load(f)
    
    # Resetar banco
    db.drop_all()
    db.create_all()
    
    # Restaurar dados
    for user_data in data['usuarios']:
        user = Usuario(**user_data)
        db.session.add(user)
    
    # ... restaurar outros dados
    
    db.session.commit()
    print(f"✅ Cenário restaurado: {scenario_name}")

def main():
    parser = argparse.ArgumentParser(description='Backup/Restore de cenários')
    parser.add_argument('--save', help='Nome do cenário para salvar')
    parser.add_argument('--restore', help='Nome do cenário para restaurar')
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.save:
            backup_scenario(args.save)
        elif args.restore:
            restore_scenario(args.restore)
        else:
            print("❌ Use --save ou --restore")
            sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3. Fixture pytest (tests/conftest.py)

```python
import pytest
import subprocess
import sys
from pathlib import Path

@pytest.fixture(scope="function")
def clean_db():
    """Reset banco antes de cada teste"""
    script_path = Path(__file__).parent.parent / "scripts" / "reset_and_seed.py"
    
    # Executar script de reset
    result = subprocess.run([
        sys.executable, str(script_path), 
        "--clean", "--seed-type", "minimal"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Erro no reset: {result.stderr}")
    
    yield
    
    # Cleanup após teste (opcional)

@pytest.fixture(scope="function")
def full_db():
    """Banco com dados completos"""
    script_path = Path(__file__).parent.parent / "scripts" / "reset_and_seed.py"
    
    result = subprocess.run([
        sys.executable, str(script_path),
        "--clean", "--seed-type", "full"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Erro no seed full: {result.stderr}")
    
    yield
```

---

## 📋 Exemplos de Uso

### Reset Rápido
```bash
# Reset completo + seed mínimo
python scripts/reset_and_seed.py --clean --seed-type=minimal

# Reset + dados completos
python scripts/reset_and_seed.py --clean --seed-type=full
```

### Cenários de Teste
```bash
# Salvar cenário atual
python scripts/backup_test_data.py --save meu_teste

# Restaurar cenário
python scripts/backup_test_data.py --restore meu_teste
```

### Testes Automáticos
```python
def test_import_csv(clean_db):
    """Teste com banco limpo"""
    # clean_db garante estado conhecido
    # ... teste de importação
```

---

## 📦 Estrutura de Arquivos

```
scripts/seed_data/
├── minimal.json              # Seed básico
├── full.json                # Seed completo  
├── scenarios/               # Cenários específicos
│   ├── import_test.json     # Para testes de importação
│   ├── crud_test.json       # Para testes de CRUD
│   └── performance_test.json # Para testes de performance
└── templates/               # Templates para novos cenários
    ├── basic_template.json
    └── full_template.json
```

---

## 🚀 Próximos Passos

1. Criar estrutura de diretórios
2. Implementar scripts principais
3. Criar arquivos JSON de seed
4. Implementar fixture pytest
5. Documentar comandos
6. Testar com cenários reais

---

*Design aprovado pelo usuário. Pronto para implementação.*
