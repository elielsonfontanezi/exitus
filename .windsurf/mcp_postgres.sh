#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use v20.19.5 >/dev/null 2>&1
exec npx -y @modelcontextprotocol/server-postgres "$@"
