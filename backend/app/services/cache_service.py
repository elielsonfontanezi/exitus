"""
Serviço de Cache Redis para performance
"""
import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheService:
    """Serviço de cache com Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        
        if REDIS_AVAILABLE:
            try:
                # Tentar conectar ao Redis
                self.redis_client = redis.Redis(
                    host='redis',  # Nome do serviço no docker-compose
                    port=6379,
                    db=0,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Testar conexão
                self.redis_client.ping()
                self.enabled = True
                logger.info("✅ Redis cache conectado com sucesso")
            except Exception as e:
                logger.warning(f"⚠️  Redis não disponível: {e}")
                self.redis_client = None
                self.enabled = False
        else:
            logger.warning("⚠️  Redis não instalado")
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                # Tentar desserializar JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Define valor no cache com TTL em segundos"""
        if not self.enabled:
            return False
        
        try:
            # Serializar valor se não for string
            if not isinstance(value, str):
                value = json.dumps(value, default=str)
            
            return self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Erro ao escrever cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove chave do cache"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Erro ao deletar cache: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Remove chaves que correspondem ao padrão"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Erro ao limpar padrão cache: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Erro ao verificar cache: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Incrementa valor numérico"""
        if not self.enabled:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Erro ao incrementar cache: {e}")
            return None
    
    def get_ttl(self, key: str) -> int:
        """Retorna TTL restante da chave"""
        if not self.enabled:
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Erro ao obter TTL: {e}")
            return -1


# Instância global do cache
cache = CacheService()

def cache_result(key_prefix: str, ttl: int = 300):
    """Decorator para cachear resultados de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Tentar obter do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"🎯 Cache HIT: {cache_key}")
                return cached_result
            
            # Executar função e cachear resultado
            logger.debug(f"💾 Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Import necessário para o decorator
from functools import wraps
