from app import create_app
from app.services.posicao_service import PosicaoService
from app.schemas.posicao_schema import PosicaoResponseSchema
import json

app = create_app()
with app.app_context():
    try:
        print("🔍 Buscando posições...")
        paginacao = PosicaoService.get_all("00000000-0000-0000-0000-000000000000", 1, 10) # ID fake ou pegar um real
        
        # Tenta pegar usuario real
        from app.models import Usuario
        user = Usuario.query.first()
        if user:
            print(f"👤 Usando usuario: {user.username}")
            paginacao = PosicaoService.get_all(user.id, 1, 10)
            
            items = paginacao.items
            print(f"📦 Encontrados: {len(items)} itens")
            
            schema = PosicaoResponseSchema(many=True)
            result = schema.dump(items)
            
            print("✅ Serialização SUCESSO:")
            print(json.dumps(result, indent=2))
        else:
            print("⚠️ Nenhum usuário encontrado para teste.")
            
    except Exception as e:
        print("\n❌ ERRO FATAL NO TESTE:")
        print(e)
        import traceback
        traceback.print_exc()
