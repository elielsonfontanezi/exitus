# -*- coding: utf-8 -*-
"""
EXITUS-CIRCUITBREAKER-001 — Circuit Breaker para APIs externas.

Implementação leve sem dependências externas. Estado mantido em memória
de processo (suficiente para single-instance dev/prod).

Estados:
  CLOSED   → funcionando normalmente, requests passam
  OPEN     → falhou N vezes consecutivas, requests bloqueadas por X segundos
  HALF_OPEN → período de espera expirou, tenta 1 request para verificar
"""
import time
import logging
import functools
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Estados
# ---------------------------------------------------------------------------
STATE_CLOSED = 'CLOSED'
STATE_OPEN = 'OPEN'
STATE_HALF_OPEN = 'HALF_OPEN'


class CircuitBreaker:
    """
    Circuit breaker por provider de API externa.

    Parâmetros:
        name             — nome do provider (para logging)
        failure_threshold — número de falhas consecutivas para abrir o circuito
        recovery_timeout  — segundos antes de tentar novamente (HALF_OPEN)
    """

    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self._state = STATE_CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None

    @property
    def state(self) -> str:
        if self._state == STATE_OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                logger.info(f"[CircuitBreaker:{self.name}] OPEN → HALF_OPEN (recovery timeout expirou)")
                self._state = STATE_HALF_OPEN
        return self._state

    @property
    def is_open(self) -> bool:
        return self.state == STATE_OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == STATE_CLOSED

    @property
    def is_half_open(self) -> bool:
        return self.state == STATE_HALF_OPEN

    def call_allowed(self) -> bool:
        """Retorna True se o circuito permite uma chamada agora."""
        s = self.state
        return s in (STATE_CLOSED, STATE_HALF_OPEN)

    def record_success(self):
        """Registra chamada bem-sucedida — fecha o circuito."""
        if self._state != STATE_CLOSED:
            logger.info(f"[CircuitBreaker:{self.name}] {self._state} → CLOSED (sucesso)")
        self._state = STATE_CLOSED
        self._failure_count = 0
        self._last_failure_time = None

    def record_failure(self):
        """Registra falha — incrementa contador e abre o circuito se necessário."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == STATE_HALF_OPEN or self._failure_count >= self.failure_threshold:
            logger.warning(
                f"[CircuitBreaker:{self.name}] OPEN "
                f"(falhas={self._failure_count}, threshold={self.failure_threshold})"
            )
            self._state = STATE_OPEN
        else:
            logger.debug(
                f"[CircuitBreaker:{self.name}] falha {self._failure_count}/{self.failure_threshold}"
            )

    def reset(self):
        """Reseta manualmente o estado para CLOSED."""
        self._state = STATE_CLOSED
        self._failure_count = 0
        self._last_failure_time = None

    def __repr__(self):
        return (
            f"CircuitBreaker(name={self.name!r}, state={self._state}, "
            f"failures={self._failure_count}/{self.failure_threshold})"
        )


# ---------------------------------------------------------------------------
# Retry com backoff exponencial
# ---------------------------------------------------------------------------

def with_retry(
    func: Callable,
    max_attempts: int = 2,
    backoff_base: float = 0.5,
    circuit_breaker: Optional[CircuitBreaker] = None,
    *args,
    **kwargs,
) -> Any:
    """
    Executa func com retry e backoff exponencial.

    Args:
        func           — callable a executar
        max_attempts   — número máximo de tentativas (default: 2)
        backoff_base   — base para backoff em segundos (default: 0.5)
        circuit_breaker — se fornecido, verifica estado antes de cada tentativa
        *args, **kwargs — passados para func

    Returns:
        Resultado de func em caso de sucesso.

    Raises:
        Última exceção capturada se todas as tentativas falharem.
    """
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        if circuit_breaker and not circuit_breaker.call_allowed():
            raise RuntimeError(
                f"Circuit breaker '{circuit_breaker.name}' está OPEN — "
                f"provider bloqueado por {circuit_breaker.recovery_timeout}s"
            )

        try:
            result = func(*args, **kwargs)
            if circuit_breaker:
                circuit_breaker.record_success()
            return result

        except Exception as e:
            last_exc = e
            if circuit_breaker:
                circuit_breaker.record_failure()

            if attempt < max_attempts:
                wait = backoff_base * (2 ** (attempt - 1))
                logger.debug(
                    f"[Retry] tentativa {attempt}/{max_attempts} falhou: {e} "
                    f"— aguardando {wait:.1f}s"
                )
                time.sleep(wait)

    raise last_exc


# ---------------------------------------------------------------------------
# Registro global de circuit breakers (um por provider)
# ---------------------------------------------------------------------------

_registry: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, failure_threshold: int = 3, recovery_timeout: int = 60) -> CircuitBreaker:
    """
    Retorna (ou cria) o circuit breaker para o provider informado.
    Garante instância única por nome no processo.
    """
    if name not in _registry:
        _registry[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
    return _registry[name]


def reset_all():
    """Reseta todos os circuit breakers — útil em testes."""
    for cb in _registry.values():
        cb.reset()
