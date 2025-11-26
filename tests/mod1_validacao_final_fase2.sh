#!/bin/bash
# Script de validação da Fase 2 - Models Core

echo "======================================"
echo "  VALIDAÇÃO FASE 2 - MODELS CORE"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Contador de erros
ERRORS=0

echo "1. Verificando arquivos de models..."
MODELS=("usuario.py" "corretora.py" "ativo.py" "posicao.py" "transacao.py")
for model in "${MODELS[@]}"; do
    if [ -f "backend/app/models/$model" ]; then
        echo -e "${GREEN}✓${NC} backend/app/models/$model"
    else
        echo -e "${RED}✗${NC} backend/app/models/$model FALTANDO"
        ((ERRORS++))
    fi
done
echo ""

echo "2. Testando imports dos models..."
podman exec exitus-backend python3 -c "
from app.models import Usuario, UserRole, Corretora, TipoCorretora, Ativo, TipoAtivo, ClasseAtivo, Posicao, Transacao, TipoOperacao
print('✓ Todos os imports OK')
" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Imports bem-sucedidos"
else
    echo -e "${RED}✗${NC} Erro nos imports"
    ((ERRORS++))
fi
echo ""

echo "3. Testando criação de instâncias..."
podman exec exitus-backend python3 << 'EOF'
from app.models import *
from decimal import Decimal

errors = 0

# Testar Usuario
try:
    u = Usuario(username='test', email='test@test.com')
    u.set_password('123')
    print('✓ Usuario OK')
except Exception as e:
    print(f'✗ Usuario ERRO: {e}')
    errors += 1

# Testar Corretora
try:
    c = Corretora(usuario_id=u.id, nome='Test', pais='BR', moeda_padrao='BRL')
    print('✓ Corretora OK')
except Exception as e:
    print(f'✗ Corretora ERRO: {e}')
    errors += 1

# Testar Ativo
try:
    a = Ativo(ticker='TEST4', nome='Test SA', tipo=TipoAtivo.ACAO, classe=ClasseAtivo.RENDA_VARIAVEL, mercado='BR', moeda='BRL')
    print('✓ Ativo OK')
except Exception as e:
    print(f'✗ Ativo ERRO: {e}')
    errors += 1

# Testar Posicao
try:
    p = Posicao(usuario_id=u.id, corretora_id=c.id, ativo_id=a.id)
    p.adicionar_compra(Decimal('10'), Decimal('50'))
    print('✓ Posicao OK')
except Exception as e:
    print(f'✗ Posicao ERRO: {e}')
    errors += 1

# Testar Transacao
try:
    from datetime import date
    t = Transacao(
        usuario_id=u.id,
        corretora_id=c.id,
        ativo_id=a.id,
        tipo_operacao=TipoOperacao.COMPRA,
        quantidade=Decimal('10'),
        preco_unitario=Decimal('50'),
        data_operacao=date.today()
    )
    print('✓ Transacao OK')
except Exception as e:
    print(f'✗ Transacao ERRO: {e}')
    errors += 1

exit(errors)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Todas as instâncias criadas com sucesso"
else
    echo -e "${RED}✗${NC} Erros na criação de instâncias"
    ((ERRORS++))
fi
echo ""

echo "4. Verificando enums..."
podman exec exitus-backend python3 -c "
from app.models import UserRole, TipoCorretora, TipoAtivo, ClasseAtivo, TipoOperacao
print(f'✓ UserRole: {[r.value for r in UserRole]}')
print(f'✓ TipoCorretora: {[t.value for t in TipoCorretora]}')
print(f'✓ TipoAtivo: {[t.value for t in TipoAtivo]}')
print(f'✓ ClasseAtivo: {[c.value for c in ClasseAtivo]}')
print(f'✓ TipoOperacao: {[t.value for t in TipoOperacao]}')
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Todos os enums funcionando"
else
    echo -e "${RED}✗${NC} Erro nos enums"
    ((ERRORS++))
fi
echo ""

echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ FASE 2 VALIDADA COM SUCESSO!${NC}"
    echo "======================================"
    exit 0
else
    echo -e "${RED}✗ FASE 2 COM $ERRORS ERRO(S)${NC}"
    echo "======================================"
    exit 1
fi
