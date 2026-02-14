#!/usr/bin/env bash
set -euo pipefail

echo
echo "=== EXITUS - START SAFE ==="
echo

# --- Função genérica: verifica status + health, reinicia se necessário ---

check_or_restart() {
  local name="$1"
  local health_cmd="$2"    # comando que retorna 0 se saudável
  local timeout="${3:-30}" # segundos para timeout

  local status
  status=$(podman inspect --format '{{.State.Status}}' "$name" 2>/dev/null || echo "missing")

  echo "Container $name - status atual: $status"

  # Se já está rodando, primeiro testa health
  if [ "$status" = "running" ]; then
    if eval "$health_cmd"; then
      echo "→ $name já está rodando e saudável."
      echo
      return 0
    else
      echo "→ $name está rodando, mas health falhou. Reiniciando..."
      podman stop "$name" >/dev/null 2>&1 || true
    fi
  fi

  # Se chegou aqui, precisa iniciar (ou reiniciar)
  echo "→ Iniciando $name..."
  podman start "$name" >/dev/null 2>&1 || {
    echo "ERRO: falha ao iniciar $name."
    return 1
  }

  echo "→ Aguardando $name ficar saudável (timeout: ${timeout}s)..."
  local i=0
  while [ "$i" -lt "$timeout" ]; do
    if eval "$health_cmd"; then
      echo "→ $name OK."
      echo
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done

  echo "ERRO: $name não ficou saudável após ${timeout}s."
  echo
  return 1
}

# --- Health checks específicos (baseados no Runbook) ---

health_db() {
  podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1
}

health_backend() {
  curl -fsS http://localhost:5000/health >/dev/null 2>&1
}

health_frontend() {
  curl -fsS http://localhost:8080/health >/dev/null 2>&1
}

# --- Ordem: DB → Backend → Frontend ---

echo "[1/3] Verificando PostgreSQL (exitus-db)..."
check_or_restart "exitus-db" "health_db" 40

echo "[2/3] Verificando Backend (exitus-backend)..."
check_or_restart "exitus-backend" "health_backend" 40

echo "[3/3] Verificando Frontend (exitus-frontend)..."
check_or_restart "exitus-frontend" "health_frontend" 40

echo "=== STATUS FINAL DOS CONTAINERS EXITUS ==="
podman ps --filter name=exitus --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo
