FROM python:3.11-slim

# Metadados
LABEL maintainer="Exitus Team"
LABEL version="1.0"
LABEL description="Exitus Backend - Secure Multi-stage Build"

# Argumentos de build
ARG APP_USER=exitus
ARG APP_UID=1000
ARG APP_GID=1000

WORKDIR /app

# 1️⃣ Instalar dependências sistema + ferramentas essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    iputils-ping \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ Criar usuário não-root dedicado
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -m -s /bin/bash ${APP_USER} && \
    chown -R ${APP_USER}:${APP_USER} /app

# 3️⃣ Copiar requirements e instalar dependências Python (como root)
COPY --chown=${APP_USER}:${APP_USER} requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copiar código da aplicação
COPY --chown=${APP_USER}:${APP_USER} . .

# 5️⃣ Criar .env se não existir
RUN if [ ! -f .env ]; then cp .env.example .env; fi && \
    chown ${APP_USER}:${APP_USER} .env

# 6️⃣ Criar diretórios necessários com permissões corretas
RUN mkdir -p /app/logs /app/tmp && \
    chown -R ${APP_USER}:${APP_USER} /app/logs /app/tmp

# 7️⃣ Trocar para usuário não-root
USER ${APP_USER}

# 8️⃣ Expor porta
EXPOSE 5000

# 9️⃣ Healthcheck robusto
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 🔟 Comando com gunicorn (production ready)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
