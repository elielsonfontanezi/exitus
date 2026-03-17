"""
Middleware para logging de performance de requisições
"""
import time
import logging
from flask import g, request
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    """Middleware para medir performance de requisições"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o middleware no app Flask"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Adicionar decorator para medir performance de funções específicas
        app.measure_time = self.measure_time
    
    def _before_request(self):
        """Executado antes de cada requisição"""
        g.start_time = time.time()
        g.endpoint_name = request.endpoint or 'unknown'
        
    def _after_request(self, response):
        """Executado após cada requisição"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log em diferentes níveis baseado no tempo de resposta
            if duration > 2.0:
                logger.warning(
                    f"🐌 SLOW REQUEST: {request.method} {request.path} "
                    f"- {g.endpoint_name} - {duration:.3f}s - {response.status_code}"
                )
            elif duration > 1.0:
                logger.info(
                    f"⚠️  REQUEST: {request.method} {request.path} "
                    f"- {g.endpoint_name} - {duration:.3f}s - {response.status_code}"
                )
            elif duration > 0.5:
                logger.debug(
                    f"📊 REQUEST: {request.method} {request.path} "
                    f"- {g.endpoint_name} - {duration:.3f}s - {response.status_code}"
                )
            
            # Adicionar header de performance (debug only)
            if request.args.get('debug_perf'):
                response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    @staticmethod
    def measure_time(func):
        """Decorator para medir tempo de execução de funções"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                end = time.time()
                duration = end - start
                
                # Log apenas se for lento
                if duration > 0.5:
                    logger.info(
                        f"⏱️  {func.__name__}: {duration:.3f}s"
                    )
                
                return result
            except Exception as e:
                end = time.time()
                duration = end - start
                logger.error(
                    f"❌ {func.__name__}: {duration:.3f}s - ERROR: {str(e)}"
                )
                raise
        
        return wrapper


def log_slow_query(threshold=1.0):
    """Decorator para logar queries lentas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                end = time.time()
                duration = end - start
                
                if duration > threshold:
                    logger.warning(
                        f"🐌 SLOW QUERY: {func.__name__} - {duration:.3f}s"
                    )
                
                return result
            except Exception as e:
                end = time.time()
                duration = end - start
                logger.error(
                    f"❌ QUERY ERROR: {func.__name__} - {duration:.3f}s - {str(e)}"
                )
                raise
        
        return wrapper
    return decorator
