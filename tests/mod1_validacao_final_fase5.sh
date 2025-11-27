#!/bin/bash
# Script de validação da Fase 5 - Seeds de Dados

echo "======================================"
echo "  VALIDAÇÃO FASE 5 - SEEDS DE DADOS"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

echo "1. Verificando usuários..."
USERS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM usuario;")
USERS=$(echo $USERS | xargs)
if [ "$USERS" -eq 4 ]; then
    echo -e "${GREEN}✓${NC} 4 usuários cadastrados"
else
    echo -e "${RED}✗${NC} Esperado 4 usuários, encontrado: $USERS"
    ((ERRORS++))
fi
echo ""

echo "2. Verificando ativos brasileiros..."
ATIVOS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM ativo WHERE mercado='BR';")
ATIVOS=$(echo $ATIVOS | xargs)
if [ "$ATIVOS" -eq 25 ]; then
    echo -e "${GREEN}✓${NC} 25 ativos brasileiros cadastrados"
else
    echo -e "${RED}✗${NC} Esperado 25 ativos, encontrado: $ATIVOS"
    ((ERRORS++))
fi

#ACOES=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM ativo WHERE mercado='BR' AND tipo='acao';")
ACOES=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM ativo WHERE mercado='BR' AND tipo='ACAO';")
ACOES=$(echo $ACOES | xargs)
echo -e "  - Ações: $ACOES"

#FIIS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM ativo WHERE mercado='BR' AND tipo='fii';")
FIIS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM ativo WHERE mercado='BR' AND tipo='FII';")
FIIS=$(echo $FIIS | xargs)
echo -e "  - FIIs: $FIIS"
echo ""

echo "3. Verificando regras fiscais BR..."
REGRAS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM regra_fiscal WHERE pais='BR';")
REGRAS=$(echo $REGRAS | xargs)
if [ "$REGRAS" -eq 6 ]; then
    echo -e "${GREEN}✓${NC} 6 regras fiscais brasileiras cadastradas"
else
    echo -e "${RED}✗${NC} Esperado 6 regras, encontrado: $REGRAS"
    ((ERRORS++))
fi
echo ""

echo "4. Verificando feriados B3..."
FERIADOS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM feriado_mercado WHERE pais='BR' AND mercado='B3';")
FERIADOS=$(echo $FERIADOS | xargs)
if [ "$FERIADOS" -eq 30 ]; then
    echo -e "${GREEN}✓${NC} 30 feriados B3 cadastrados"
else
    echo -e "${RED}✗${NC} Esperado 30 feriados, encontrado: $FERIADOS"
    ((ERRORS++))
fi
echo ""

echo "5. Verificando fontes de dados..."
FONTES=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM fonte_dados;")
FONTES=$(echo $FONTES | xargs)
if [ "$FONTES" -eq 7 ]; then
    echo -e "${GREEN}✓${NC} 7 fontes de dados cadastradas"
else
    echo -e "${RED}✗${NC} Esperado 7 fontes, encontrado: $FONTES"
    ((ERRORS++))
fi
echo ""

echo "6. Verificando dados específicos..."

# Verificar usuário admin
ADMIN=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT username FROM usuario WHERE role='ADMIN' LIMIT 1;")
ADMIN=$(echo $ADMIN | xargs)
if [ "$ADMIN" = "admin" ]; then
    echo -e "${GREEN}✓${NC} Usuário admin encontrado"
else
    echo -e "${RED}✗${NC} Usuário admin não encontrado"
    ((ERRORS++))
fi

# Verificar PETR4
PETR4=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT ticker FROM ativo WHERE ticker='PETR4';")
PETR4=$(echo $PETR4 | xargs)
if [ "$PETR4" = "PETR4" ]; then
    echo -e "${GREEN}✓${NC} Ativo PETR4 encontrado"
else
    echo -e "${RED}✗${NC} Ativo PETR4 não encontrado"
    ((ERRORS++))
fi

# Verificar yfinance
YFINANCE=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT nome FROM fonte_dados WHERE nome='yfinance';")
YFINANCE=$(echo $YFINANCE | xargs)
if [ "$YFINANCE" = "yfinance" ]; then
    echo -e "${GREEN}✓${NC} Fonte yfinance encontrada"
else
    echo -e "${RED}✗${NC} Fonte yfinance não encontrada"
    ((ERRORS++))
fi
echo ""

echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ FASE 5 VALIDADA COM SUCESSO!${NC}"
    echo "======================================"
    echo ""
    echo "📊 Resumo dos Dados:"
    echo "  - $USERS usuários"
    echo "  - $ATIVOS ativos ($ACOES ações + $FIIS FIIs)"
    echo "  - $REGRAS regras fiscais"
    echo "  - $FERIADOS feriados"
    echo "  - $FONTES fontes de dados"
    echo ""
    echo "✅ Banco de dados populado e pronto!"
    echo ""
    exit 0
else
    echo -e "${RED}✗ FASE 5 COM $ERRORS ERRO(S)${NC}"
    echo "======================================"
    exit 1
fi
