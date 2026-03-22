# Cenários de Teste - Sistema Exitus

> **Data:** 22/03/2026  
> **Versão:** 1.0  
> **Propósito:** Documentação dos cenários de teste disponíveis para desenvolvimento e QA

---

## 📋 Visão Geral

Cenários de teste são conjuntos de dados predefinidos para diferentes tipos de testes:

```
scripts/seed_data/scenarios/
├── test_e2e.json    # Testes E2E - dados completos e realistas
├── test_ir.json     # Testes de IR - operações específicas para cálculo fiscal
├── test_stress.json # Testes de carga - volume alto de dados
└── custom.json      # Cenários personalizados (criados pelo usuário)
```

---

## 🎯 Tipos de Cenários

### 1. test_e2e - Testes End-to-End

**Objetivo:** Dados completos para testes E2E da interface e APIs

**Conteúdo:**
- **Usuários:** 3 (admin, user, viewer)
- **Assessoras:** 1
- **Ativos:** 7 (Ações BR, FII, Stocks US)
- **Corretoras:** 3
- **Transações:** 4 (compras e vendas)
- **Proventos:** 2 (dividendos, rendimentos)
- **Movimentações:** 2 (depósito R$ 10.000, saque R$ 500)
- **Alertas:** 3 (preço alvo, stop loss, dividendo) ← **ATUALIZADO 22/03/2026**

**Uso recomendado:**
- Testes automatizados E2E com Playwright
- Validação de fluxos completos da UI
- Testes de API com dados realistas
- Testes de tela de alertas e notificações

### 2. test_ir - Testes de Imposto de Renda

**Objetivo:** Dados específicos para validar cálculos fiscais

**Conteúdo:**
- **Usuários:** 1
- **Ativos:** 4 (Ações, FII, CDB, Tesouro)
- **Transações:** 8 (múltiplas compras/vendas para teste de preço médio)
- **Proventos:** 3 (DIVIDENDO isento, JCP tributável, RENDIMENTO FII isento)

**Casos de teste cobertos:**
- Cálculo de preço médio (múltiplas compras)
- Venda parcial com lucro
- Venda parcial com prejuízo
- Proventos isentos vs tributáveis
- Day trade (implícito nas operações)

### 3. test_stress - Testes de Carga

**Objetivo:** Volume alto de dados para testes de performance

**Conteúdo:**
- **Usuários:** 6 (1 admin + 5 usuários)
- **Assessoras:** 2
- **Ativos:** 7 (diversos tipos)
- **Corretoras:** 3
- **Transações:** 13 (operações distribuídas)
- **Proventos:** 5
- **Movimentações:** 5 (depósitos de valores altos)

**Uso recomendado:**
- Testes de performance de queries
- Validação de limites do sistema
- Testes de concorrência
- Benchmarks de API

---

## 🛠️ Como Usar

### Via Script (Reset + Seed)

```bash
# Carregar cenário específico (limpa banco antes)
./scripts/reset_and_seed.sh --clean --seed-type=custom --restore test_e2e

# Listar cenários disponíveis
./scripts/reset_and_seed.sh --list-scenarios

# Salvar estado atual como novo cenário
./scripts/reset_and_seed.sh --backup meu_teste_custom
```

### Via pytest (Fixture)

```python
import pytest

@pytest.mark.parametrize("scenario", ["test_e2e", "test_ir", "test_stress"])
def test_fluxo_completo(app, load_scenario, scenario):
    """
    Testa fluxo completo com diferentes cenários
    - scenario="test_e2e": Dados realistas para UI
    - scenario="test_ir": Operações específicas para IR
    - scenario="test_stress": Volume alto para performance
    """
    # Cenário já está carregado no banco
    # Seu teste aqui...
    pass
```

### Exemplo Prático

```python
def test_calculo_ir_preco_medio(app, load_scenario):
    """Testa cálculo de IR com múltiplas compras"""
    # Carrega cenário test_ir automaticamente
    with app.app_context():
        from app.services.ir_service import IRService
        
        # Busca transações do cenário
        usuario = Usuario.query.filter_by(username='ir_test_user').first()
        ativo = Ativo.query.filter_by(ticker='IRACAO1').first()
        
        # Calcula IR
        ir_service = IRService()
        resultado = ir_service.calcular_ir_vendas(usuario.id, ativo.id)
        
        # Valida cálculo
        assert resultado['lucro'] > 0
        assert resultado['ir_devido'] > 0
```

---

## 📊 Estrutura dos Cenários

### Formato JSON

```json
{
  "version": "1.0",
  "description": "Descrição do cenário",
  "timestamp": "2026-03-22T00:00:00Z",
  "usuarios": [...],
  "assessoras": [...],
  "ativos": [...],
  "corretoras": [...],
  "transacoes": [...],
  "proventos": [...],
  "movimentacoes_caixa": [...]
}
```

### Campos Opcionais

Todos os campos opcionais devem usar `get()` com valor padrão:

```python
preco_atual=Decimal(str(ativo_data.get('preco_atual', 0)))
ativo=usuario_data.get('ativo', True)
```

### Relacionamentos

- **Transações:** Referenciam usuários, ativos e corretoras por nome
- **Proventos:** Referenciam ativos por ticker
- **Movimentações:** Referenciam usuários e corretoras por nome

---

## 🚀 Boas Práticas

### 1. Nomenclatura
- `test_<tipo>` para cenários predefinidos
- `<feature>_<scenario>` para cenários específicos (ex: `ir_day_trade`)
- `<user>_<data>` para cenários personalizados (ex: `joao_teste_2026`)

### 2. Volume de Dados
- **E2E:** < 50 transações (foco na cobertura)
- **IR:** < 20 transações (foco nos casos de cálculo)
- **Stress:** 100+ transações (foco na performance)

### 3. Dados Realistas
- Usar tickers reais quando possível
- Preços e datas consistentes
- Operações com valores representativos

### 4. Idempotência
- Cenários podem ser carregados múltiplas vezes
- Cleanup automático via `cleanup_test_data`
- Sem efeitos colaterais entre testes

---

## 🔧 Criar Novo Cenário

### 1. Via Backup

```bash
# 1. Prepare os dados manualmente ou via seeds
./scripts/reset_and_seed.sh --clean --seed-type=full

# 2. Modifique os dados conforme necessário
# (via UI, API ou SQL direto)

# 3. Salve como novo cenário
./scripts/reset_and_seed.sh --backup meu_novo_cenario
```

### 2. Via JSON

```bash
# 1. Copie cenário existente como template
cp scripts/seed_data/scenarios/test_e2e.json scripts/seed_data/scenarios/meu_cenario.json

# 2. Edite o JSON com seus dados
vim scripts/seed_data/scenarios/meu_cenario.json

# 3. Teste o cenário
./scripts/reset_and_seed.sh --clean --seed-type=custom --restore meu_cenario
```

---

## 📈 Métricas e Validação

### Validação Automática

```bash
# Verificar integridade do cenário
podman exec exitus-backend python -c "
from app import create_app
from app.database import db
app = create_app()
with app.app_context():
    print(f'Usuários: {db.session.query(Usuario).count()}')
    print(f'Ativos: {db.session.query(Ativo).count()}')
    print(f'Transações: {db.session.query(Transacao).count()}')
"
```

### Performance por Cenário

| Cenário | Transações | Tempo Load (s) | Memória (MB) |
|---------|-------------|----------------|--------------|
| test_e2e | 4 | < 1 | ~50 |
| test_ir | 8 | < 1 | ~60 |
| test_stress | 13 | < 2 | ~80 |

---

## 🐛 Troubleshooting

### Erros Comuns

1. **"Cenário não encontrado"**
   - Verifique se o arquivo JSON existe em `scripts/seed_data/scenarios/`
   - Confirme a extensão `.json`

2. **"Dados incompletos para transação"**
   - Verifique se usuários, ativos e corretoras existem no cenário
   - Confirme a grafia exata dos nomes

3. **"Erro ao carregar cenário"**
   - Valide sintaxe do JSON (use `jq . scenario.json`)
   - Verifique campos obrigatórios

### Debug

```python
# Adicionar ao teste para debug
def test_com_debug(app, load_scenario):
    scenario_name = request.param
    print(f"Cenário carregado: {scenario_name}")
    
    with app.app_context():
        print(f"Usuários: {Usuario.query.count()}")
        print(f"Ativos: {Ativo.query.count()}")
        print(f"Transações: {Transacao.query.count()}")
```

---

## 📚 Referências

- **Fixtures pytest:** `backend/tests/conftest.py`
- **Seed manager:** `scripts/reset_and_seed.py`
- **Modelos:** `backend/app/models/`
- **Testes existentes:** `backend/tests/test_*.py`

---

*Última atualização: 22/03/2026*  
*Para dúvidas, consulte o canal #dev-tests*
