#!/bin/bash
# Script de validação da Fase 3 - Models Complementares

echo "======================================"
echo "  VALIDAÇÃO FASE 3 - MODELS COMPLEMENTARES"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de erros
ERRORS=0

echo "1. Verificando arquivos de models..."
MODELS=("provento.py" "movimentacao_caixa.py" "evento_corporativo.py" "fonte_dados.py" "regra_fiscal.py" "feriado_mercado.py" "log_auditoria.py")
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
from app.models import (
    Provento, TipoProvento,
    MovimentacaoCaixa, TipoMovimentacao,
    EventoCorporativo, TipoEventoCorporativo,
    FonteDados, TipoFonteDados,
    RegraFiscal, IncidenciaImposto,
    FeriadoMercado, TipoFeriado,
    LogAuditoria
)
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
from datetime import date, time

errors = 0

# Testar Provento
try:
    ativo = Ativo(ticker='TEST4', nome='Test', tipo=TipoAtivo.ACAO, classe=ClasseAtivo.RENDA_VARIAVEL, mercado='BR', moeda='BRL')
    p = Provento(
        ativo_id=ativo.id,
        tipo_provento=TipoProvento.DIVIDENDO,
        valor_por_acao=Decimal('1.50'),
        quantidade_ativos=Decimal('100'),
        imposto_retido=Decimal('0'),
        data_com=date(2025, 11, 20),
        data_pagamento=date(2025, 12, 5)
    )
    print('✓ Provento OK')
except Exception as e:
    print(f'✗ Provento ERRO: {e}')
    errors += 1

# Testar MovimentacaoCaixa
try:
    user = Usuario(username='test', email='test@test.com')
    corr = Corretora(usuario_id=user.id, nome='Test', pais='BR', moeda_padrao='BRL')
    m = MovimentacaoCaixa(
        usuario_id=user.id,
        corretora_id=corr.id,
        tipo_movimentacao=TipoMovimentacao.DEPOSITO,
        valor=Decimal('1000'),
        moeda='BRL',
        data_movimentacao=date.today()
    )
    print('✓ MovimentacaoCaixa OK')
except Exception as e:
    print(f'✗ MovimentacaoCaixa ERRO: {e}')
    errors += 1

# Testar EventoCorporativo
try:
    e = EventoCorporativo(
        ativo_id=ativo.id,
        tipo_evento=TipoEventoCorporativo.SPLIT,
        data_evento=date(2025, 12, 1),
        proporcao='2:1',
        descricao='Split 2 para 1'
    )
    print('✓ EventoCorporativo OK')
except Exception as e:
    print(f'✗ EventoCorporativo ERRO: {e}')
    errors += 1

# Testar FonteDados
try:
    f = FonteDados(
        nome='yfinance',
        tipo_fonte=TipoFonteDados.API,
        url_base='https://finance.yahoo.com',
        ativa=True,
        prioridade=1
    )
    print('✓ FonteDados OK')
except Exception as e:
    print(f'✗ FonteDados ERRO: {e}')
    errors += 1

# Testar RegraFiscal
try:
    r = RegraFiscal(
        pais='BR',
        tipo_ativo='ACAO',
        aliquota_ir=Decimal('15.0'),
        incide_sobre=IncidenciaImposto.LUCRO,
        descricao='IR sobre ganhos de capital',
        vigencia_inicio=date(2023, 1, 1),
        ativa=True
    )
    print('✓ RegraFiscal OK')
except Exception as e:
    print(f'✗ RegraFiscal ERRO: {e}')
    errors += 1

# Testar FeriadoMercado
try:
    fer = FeriadoMercado(
        pais='BR',
        mercado='B3',
        data_feriado=date(2025, 12, 25),
        tipo_feriado=TipoFeriado.NACIONAL,
        nome='Natal',
        recorrente=True
    )
    print('✓ FeriadoMercado OK')
except Exception as e:
    print(f'✗ FeriadoMercado ERRO: {e}')
    errors += 1

# Testar LogAuditoria
try:
    log = LogAuditoria(
        usuario_id=user.id,
        acao='LOGIN',
        ip_address='127.0.0.1',
        sucesso=True
    )
    print('✓ LogAuditoria OK')
except Exception as e:
    print(f'✗ LogAuditoria ERRO: {e}')
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
from app.models import (
    TipoProvento, TipoMovimentacao, TipoEventoCorporativo,
    TipoFonteDados, IncidenciaImposto, TipoFeriado
)
print(f'✓ TipoProvento: {[t.value for t in TipoProvento]}')
print(f'✓ TipoMovimentacao: {[t.value for t in TipoMovimentacao]}')
print(f'✓ TipoEventoCorporativo: {[t.value for t in TipoEventoCorporativo]}')
print(f'✓ TipoFonteDados: {[t.value for t in TipoFonteDados]}')
print(f'✓ IncidenciaImposto: {[i.value for i in IncidenciaImposto]}')
print(f'✓ TipoFeriado: {[t.value for t in TipoFeriado]}')
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Todos os enums funcionando"
else
    echo -e "${RED}✗${NC} Erro nos enums"
    ((ERRORS++))
fi
echo ""

echo "5. Testando métodos específicos..."
podman exec exitus-backend python3 << 'EOF'
from app.models import *
from decimal import Decimal
from datetime import date

errors = 0

# Testar cálculos de Provento
try:
    ativo = Ativo(ticker='TEST', nome='Test', tipo=TipoAtivo.ACAO, classe=ClasseAtivo.RENDA_VARIAVEL, mercado='BR', moeda='BRL', preco_atual=Decimal('40'))
    prov = Provento(
        ativo_id=ativo.id,
        tipo_provento=TipoProvento.DIVIDENDO,
        valor_por_acao=Decimal('2.00'),
        quantidade_ativos=Decimal('100'),
        imposto_retido=Decimal('0'),
        data_com=date(2025, 11, 20),
        data_pagamento=date(2025, 12, 5)
    )
    dy = prov.dividend_yield_efetivo(ativo.preco_atual)
    assert dy == 5.0, f"DY deveria ser 5.0, foi {dy}"
    print('✓ Provento.dividend_yield_efetivo() OK')
except Exception as e:
    print(f'✗ Provento métodos ERRO: {e}')
    errors += 1

# Testar cálculos de EventoCorporativo
try:
    evento = EventoCorporativo(
        ativo_id=ativo.id,
        tipo_evento=TipoEventoCorporativo.SPLIT,
        data_evento=date(2025, 12, 1),
        proporcao='2:1',
        descricao='Split'
    )
    fator = evento.calcular_fator_ajuste()
    assert fator == 2.0, f"Fator deveria ser 2.0, foi {fator}"
    print('✓ EventoCorporativo.calcular_fator_ajuste() OK')
except Exception as e:
    print(f'✗ EventoCorporativo métodos ERRO: {e}')
    errors += 1

# Testar estatísticas de FonteDados
try:
    fonte = FonteDados(nome='test', tipo_fonte=TipoFonteDados.API, ativa=True, prioridade=1)
    fonte.registrar_consulta_sucesso()
    fonte.registrar_consulta_sucesso()
    fonte.registrar_erro()
    taxa = fonte.taxa_sucesso()
    assert 66.0 <= taxa <= 67.0, f"Taxa sucesso deveria ser ~66.67%, foi {taxa}"
    print('✓ FonteDados.taxa_sucesso() OK')
except Exception as e:
    print(f'✗ FonteDados métodos ERRO: {e}')
    errors += 1

# Testar cálculo de imposto RegraFiscal
try:
    regra = RegraFiscal(
        pais='BR',
        aliquota_ir=Decimal('15.0'),
        valor_isencao=Decimal('20000'),
        incide_sobre=IncidenciaImposto.LUCRO,
        descricao='Test',
        vigencia_inicio=date(2023, 1, 1),
        ativa=True
    )
    imposto = regra.calcular_imposto(Decimal('30000'))
    assert imposto == 1500, f"Imposto deveria ser 1500, foi {imposto}"
    print('✓ RegraFiscal.calcular_imposto() OK')
except Exception as e:
    print(f'✗ RegraFiscal métodos ERRO: {e}')
    errors += 1

# Testar alterações LogAuditoria
try:
    log = LogAuditoria(
        acao='UPDATE',
        dados_antes={'nome': 'João', 'idade': 30},
        dados_depois={'nome': 'João Silva', 'idade': 30},
        sucesso=True
    )
    alteracoes = log.get_alteracoes()
    assert 'nome' in alteracoes, "Deveria detectar alteração em 'nome'"
    assert 'idade' not in alteracoes, "Não deveria detectar alteração em 'idade'"
    print('✓ LogAuditoria.get_alteracoes() OK')
except Exception as e:
    print(f'✗ LogAuditoria métodos ERRO: {e}')
    errors += 1

exit(errors)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Todos os métodos específicos funcionando"
else
    echo -e "${RED}✗${NC} Erros nos métodos específicos"
    ((ERRORS++))
fi
echo ""

echo "6. Resumo de models criados..."
echo -e "${YELLOW}Fase 2 (Core):${NC}"
echo "  1. Usuario"
echo "  2. Corretora"
echo "  3. Ativo"
echo "  4. Posicao"
echo "  5. Transacao"
echo ""
echo -e "${YELLOW}Fase 3 (Complementares):${NC}"
echo "  6. Provento"
echo "  7. MovimentacaoCaixa"
echo "  8. EventoCorporativo"
echo "  9. FonteDados"
echo "  10. RegraFiscal"
echo "  11. FeriadoMercado"
echo "  12. LogAuditoria"
echo ""

echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ FASE 3 VALIDADA COM SUCESSO!${NC}"
    echo "======================================"
    echo ""
    echo "📊 Total: 12 models criados"
    echo "✅ Próximo: Fase 4 - Migrations e Schema"
    echo ""
    exit 0
else
    echo -e "${RED}✗ FASE 3 COM $ERRORS ERRO(S)${NC}"
    echo "======================================"
    exit 1
fi
