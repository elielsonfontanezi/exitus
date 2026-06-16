#!/bin/bash
# Docker Entrypoint para Exitus Backend
# Ajusta UID/GID dinamicamente para match com host

set -e

# Se USER_UID/GID foram passados como env vars, ajusta o usuário
if [ -n "$USER_UID" ] && [ "$USER_UID" != "$(id -u exitus)" ]; then
    echo "🔧 Ajustando UID do usuário exitus: $(id -u exitus) -> $USER_UID"
    usermod -u $USER_UID exitus
fi

if [ -n "$USER_GID" ] && [ "$USER_GID" != "$(id -g exitus)" ]; then
    echo "🔧 Ajustando GID do usuário exitus: $(id -g exitus) -> $USER_GID"
    groupmod -g $USER_GID exitus
fi

# Garante permissões corretas nos diretórios de volume
echo "🔧 Ajustando permissões dos diretórios..."
chown -R exitus:exitus /app 2>/dev/null || true
chown -R exitus:exitus /app/logs 2>/dev/null || true
chown -R exitus:exitus /app/tmp 2>/dev/null || true

# Mostra informações de debug
echo "📊 Informações do usuário:"
echo "  UID: $(id -u exitus)"
echo "  GID: $(id -g exitus)"
echo "  HOME: $(getent passwd exitus | cut -d: -f6)"
echo ""

# Executa o comando original (CMD do Dockerfile)
exec "$@"
