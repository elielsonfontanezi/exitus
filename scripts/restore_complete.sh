#!/bin/bash
echo "🔄 Exitus - Restore COMPLETO (DB + Seeds)"

# 1. Parar serviços
./scripts/stop_services.sh

# 2. Restore banco
./scripts/restore_db.sh

# 3. Recriar containers
./scripts/setup_containers.sh

# 4. Popular seeds
./scripts/populate_seeds.sh

echo "✅ Restore completo concluído!"
