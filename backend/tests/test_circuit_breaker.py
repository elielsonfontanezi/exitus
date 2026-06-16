# -*- coding: utf-8 -*-
"""
Testes — EXITUS-CIRCUITBREAKER-001
Cobre CircuitBreaker, get_circuit_breaker e with_retry.
"""
import time
import pytest
from unittest.mock import patch, MagicMock
from app.utils.circuit_breaker import (
    CircuitBreaker,
    get_circuit_breaker,
    with_retry,
    reset_all,
    STATE_CLOSED,
    STATE_OPEN,
    STATE_HALF_OPEN,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpar_registry():
    """Reseta todos os circuit breakers antes de cada teste."""
    reset_all()
    yield
    reset_all()


# ---------------------------------------------------------------------------
# Testes: estados básicos
# ---------------------------------------------------------------------------

class TestCircuitBreakerEstados:
    def test_estado_inicial_closed(self):
        cb = CircuitBreaker('test', failure_threshold=3)
        assert cb.state == STATE_CLOSED
        assert cb.is_closed
        assert not cb.is_open

    def test_call_allowed_quando_closed(self):
        cb = CircuitBreaker('test', failure_threshold=3)
        assert cb.call_allowed() is True

    def test_abre_apos_threshold_falhas(self):
        cb = CircuitBreaker('test', failure_threshold=3, recovery_timeout=60)
        cb.record_failure()
        assert cb.state == STATE_CLOSED
        cb.record_failure()
        assert cb.state == STATE_CLOSED
        cb.record_failure()
        assert cb.state == STATE_OPEN
        assert cb.is_open
        assert not cb.call_allowed()

    def test_sucesso_fecha_circuito(self):
        cb = CircuitBreaker('test', failure_threshold=2, recovery_timeout=60)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open
        cb.record_success()
        assert cb.is_closed
        assert cb._failure_count == 0

    def test_reset_manual(self):
        cb = CircuitBreaker('test', failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open
        cb.reset()
        assert cb.is_closed
        assert cb._failure_count == 0

    def test_repr(self):
        cb = CircuitBreaker('brapi.dev', failure_threshold=3)
        assert 'brapi.dev' in repr(cb)
        assert 'CLOSED' in repr(cb)


# ---------------------------------------------------------------------------
# Testes: transição OPEN → HALF_OPEN
# ---------------------------------------------------------------------------

class TestCircuitBreakerHalfOpen:
    def test_transicao_para_half_open_apos_timeout(self):
        cb = CircuitBreaker('test', failure_threshold=2, recovery_timeout=0)
        cb.record_failure()
        cb.record_failure()
        assert cb._state == STATE_OPEN

        # recovery_timeout=0: já expirou
        assert cb.state == STATE_HALF_OPEN
        assert cb.is_half_open
        assert cb.call_allowed()

    def test_half_open_volta_a_open_se_falhar(self):
        cb = CircuitBreaker('test', failure_threshold=2, recovery_timeout=0)
        cb.record_failure()
        cb.record_failure()
        _ = cb.state  # trigger HALF_OPEN

        # Com recovery_timeout=0, após record_failure o _state interno vai para OPEN
        # mas state property imediatamente re-transiciona para HALF_OPEN.
        # Verificamos o _state interno para confirmar que record_failure abriu o circuito.
        cb.record_failure()
        assert cb._state == STATE_OPEN  # internamente aberto

    def test_half_open_fecha_se_sucesso(self):
        cb = CircuitBreaker('test', failure_threshold=2, recovery_timeout=0)
        cb.record_failure()
        cb.record_failure()
        _ = cb.state  # trigger HALF_OPEN

        cb.record_success()
        assert cb.is_closed

    def test_nao_transiciona_antes_do_timeout(self):
        cb = CircuitBreaker('test', failure_threshold=2, recovery_timeout=9999)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == STATE_OPEN


# ---------------------------------------------------------------------------
# Testes: get_circuit_breaker (registry)
# ---------------------------------------------------------------------------

class TestGetCircuitBreaker:
    def test_retorna_mesma_instancia(self):
        cb1 = get_circuit_breaker('brapi.dev')
        cb2 = get_circuit_breaker('brapi.dev')
        assert cb1 is cb2

    def test_providers_distintos_sao_instancias_distintas(self):
        cb_brapi = get_circuit_breaker('brapi.dev')
        cb_yf = get_circuit_breaker('yfinance.BR')
        assert cb_brapi is not cb_yf

    def test_threshold_e_timeout_configurados(self):
        cb = get_circuit_breaker('finnhub', failure_threshold=5, recovery_timeout=120)
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 120

    def test_reset_all_limpa_estados(self):
        cb = get_circuit_breaker('alphavantage', failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open

        reset_all()
        assert cb.is_closed


# ---------------------------------------------------------------------------
# Testes: with_retry
# ---------------------------------------------------------------------------

class TestWithRetry:
    def test_sucesso_na_primeira_tentativa(self):
        func = MagicMock(return_value=42)
        result = with_retry(func, max_attempts=3)
        assert result == 42
        assert func.call_count == 1

    def test_sucesso_na_segunda_tentativa(self):
        func = MagicMock(side_effect=[ValueError("falha"), 99])
        result = with_retry(func, max_attempts=3, backoff_base=0)
        assert result == 99
        assert func.call_count == 2

    def test_levanta_excecao_apos_max_tentativas(self):
        func = MagicMock(side_effect=ConnectionError("sem rede"))
        with pytest.raises(ConnectionError):
            with_retry(func, max_attempts=3, backoff_base=0)
        assert func.call_count == 3

    def test_circuit_breaker_bloqueado_levanta_runtime(self):
        cb = CircuitBreaker('test_retry', failure_threshold=1, recovery_timeout=9999)
        cb.record_failure()
        assert cb.is_open

        func = MagicMock(return_value=1)
        with pytest.raises(RuntimeError, match="OPEN"):
            with_retry(func, max_attempts=2, circuit_breaker=cb)

        assert func.call_count == 0  # nunca chamado

    def test_circuit_breaker_recebe_sucesso_apos_chamada_ok(self):
        cb = CircuitBreaker('test_success_cb', failure_threshold=3)
        func = MagicMock(return_value='ok')
        with_retry(func, max_attempts=1, circuit_breaker=cb)
        assert cb.is_closed
        assert cb._failure_count == 0

    def test_circuit_breaker_recebe_falha_apos_excecao(self):
        cb = CircuitBreaker('test_fail_cb', failure_threshold=5)
        func = MagicMock(side_effect=Exception("erro"))
        with pytest.raises(Exception):
            with_retry(func, max_attempts=1, backoff_base=0, circuit_breaker=cb)
        assert cb._failure_count == 1

    def test_sem_sleep_quando_backoff_zero(self):
        """with_retry não deve demorar com backoff_base=0."""
        func = MagicMock(side_effect=[Exception("err"), "ok"])
        inicio = time.time()
        result = with_retry(func, max_attempts=2, backoff_base=0)
        elapsed = time.time() - inicio
        assert result == "ok"
        assert elapsed < 0.5  # deve ser instantâneo


# ---------------------------------------------------------------------------
# Testes: integração com get_circuit_breaker + with_retry
# ---------------------------------------------------------------------------

class TestCircuitBreakerIntegrado:
    def test_provider_abre_apos_threshold_e_pula(self):
        """Simula provider brapi que falha 3x — circuito abre — 4a call retorna imediatamente."""
        cb = get_circuit_breaker('brapi_integrado', failure_threshold=3, recovery_timeout=9999)

        for _ in range(3):
            cb.record_failure()

        assert cb.is_open
        assert not cb.call_allowed()

    def test_dois_providers_independentes(self):
        """Falha em brapi não afeta yfinance."""
        cb_brapi = get_circuit_breaker('brapi_ind', failure_threshold=2)
        cb_yf = get_circuit_breaker('yfinance_ind', failure_threshold=2)

        cb_brapi.record_failure()
        cb_brapi.record_failure()

        assert cb_brapi.is_open
        assert cb_yf.is_closed
        assert cb_yf.call_allowed()
