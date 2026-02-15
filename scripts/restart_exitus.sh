#!/bin/bash
# Reinicia todos os serviços do Exitus chamando os scripts existentes

# Define o diretório onde os scripts estão (mesmo diretório deste arquivo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "    RESTARTING EXITUS SERVICES          "
echo "========================================"
echo ""

# 1. Parar os serviços
bash "$SCRIPT_DIR/stop_exitus.sh"

echo ""
echo "Aguardando 2 segundos para limpeza de sockets..."
sleep 2
echo ""

# 2. Iniciar os serviços
bash "$SCRIPT_DIR/start_exitus.sh"

echo ""
echo "========================================"
echo "    RESTART CONCLUÍDO COM SUCESSO!      "
echo "========================================"
