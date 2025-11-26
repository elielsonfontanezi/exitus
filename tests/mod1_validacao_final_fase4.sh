#!/bin/bash
# Script de validação da Fase 4 - Migrations e Schema

echo "======================================"
echo "  VALIDAÇÃO FASE 4 - MIGRATIONS E SCHEMA"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de erros
ERRORS=0

echo "1. Verificando migration gerada..."
MIGRATION_FILE=$(ls backend/alembic/versions/*_initial_schema_12_models.py 2>/dev/null | head -1)
if [ -f "$MIGRATION_FILE" ]; then
    LINES=$(wc -l < "$MIGRATION_FILE")
    if [ "$LINES" -gt 400 ]; then
        echo -e "${GREEN}✓${NC} Migration gerada: $MIGRATION_FILE ($LINES linhas)"
    else
        echo -e "${RED}✗${NC} Migration muito pequena: $LINES linhas"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} Migration não encontrada"
    ((ERRORS++))
fi
echo ""

echo "2. Verificando tabelas no PostgreSQL..."
TABLES=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
TABLES=$(echo $TABLES | xargs) # trim whitespace
if [ "$TABLES" -eq 13 ]; then
    echo -e "${GREEN}✓${NC} 13 tabelas criadas (12 models + alembic_version)"
else
    echo -e "${RED}✗${NC} Esperado 13 tabelas, encontrado: $TABLES"
    ((ERRORS++))
fi

# Listar tabelas
echo -e "${YELLOW}Tabelas encontradas:${NC}"
podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name;" | sed 's/^/ - /'
echo ""

echo "3. Verificando enums no PostgreSQL..."
ENUMS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM pg_type WHERE typtype='e';")
ENUMS=$(echo $ENUMS | xargs)
if [ "$ENUMS" -eq 11 ]; then
    echo -e "${GREEN}✓${NC} 11 enums criados"
else
    echo -e "${RED}✗${NC} Esperado 11 enums, encontrado: $ENUMS"
    ((ERRORS++))
fi

# Listar enums
echo -e "${YELLOW}Enums encontrados:${NC}"
podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT typname FROM pg_type WHERE typtype='e' ORDER BY typname;" | sed 's/^/ - /'
echo ""

echo "4. Verificando foreign keys..."
FKS=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type='FOREIGN KEY';")
FKS=$(echo $FKS | xargs)
if [ "$FKS" -ge 10 ]; then
    echo -e "${GREEN}✓${NC} $FKS foreign keys criadas"
else
    echo -e "${YELLOW}⚠${NC} Apenas $FKS foreign keys encontradas (esperado >=10)"
fi
echo ""

echo "5. Verificando índices..."
INDEXES=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public';")
INDEXES=$(echo $INDEXES | xargs)
if [ "$INDEXES" -ge 50 ]; then
    echo -e "${GREEN}✓${NC} $INDEXES índices criados"
else
    echo -e "${YELLOW}⚠${NC} Apenas $INDEXES índices encontrados"
fi
echo ""

echo "6. Testando insert em tabela usuario..."
podman exec exitus-db psql -U exitus -d exitusdb -c "
INSERT INTO usuario (id, username, email, password_hash, ativo, role, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'test_validation',
    'test@validation.com',
    'hash123',
    true,
    'USER'::userrole,
    NOW(),
    NOW()
) ON CONFLICT DO NOTHING;
" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Insert de teste bem-sucedido"
    # Limpar
    podman exec exitus-db psql -U exitus -d exitusdb -c "DELETE FROM usuario WHERE username='test_validation';" > /dev/null 2>&1
else
    echo -e "${RED}✗${NC} Erro no insert de teste"
    ((ERRORS++))
fi
echo ""

echo "7. Verificando versão do Alembic..."
ALEMBIC_VERSION=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT version_num FROM alembic_version;")
ALEMBIC_VERSION=$(echo $ALEMBIC_VERSION | xargs)
if [ ! -z "$ALEMBIC_VERSION" ]; then
    echo -e "${GREEN}✓${NC} Alembic version: $ALEMBIC_VERSION"
else
    echo -e "${RED}✗${NC} Versão do Alembic não encontrada"
    ((ERRORS++))
fi
echo ""

echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ FASE 4 VALIDADA COM SUCESSO!${NC}"
    echo "======================================"
    echo ""
    echo "📊 Resumo:"
    echo "  - 13 tabelas criadas"
    echo "  - 11 enums criados"
    echo "  - $FKS foreign keys"
    echo "  - $INDEXES índices"
    echo ""
    echo "✅ Próximo: Fase 5 - Seeds de Dados"
    echo ""
    exit 0
else
    echo -e "${RED}✗ FASE 4 COM $ERRORS ERRO(S)${NC}"
    echo "======================================"
    exit 1
fi
