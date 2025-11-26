# No HOST Ubuntu
echo "=== Validação Fase 1 ==="
echo "1. Containers:"
#podman ps --format "{{.Names}}" | grep exitus
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "2. Estrutura:"
ls -la backend/app/models/ backend/app/seeds/ backend/alembic/
echo ""
echo "3. Conexão DB:"
podman exec exitus-backend python3 -c "from app import create_app; app=create_app(); print('✓ App inicializada')"
