FROM python:3.11-slim

WORKDIR /app

# Instala ferramentas úteis de diagnóstico
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Se não existir .env dentro da imagem, cria a partir do exemplo (útil para dev)
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Criar diretório de logs
RUN mkdir -p /app/logs

# Expõe porta
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Comando com gunicorn (hot reload em dev)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app", "--reload", "--access-logfile", "-", "--error-logfile", "-"]
