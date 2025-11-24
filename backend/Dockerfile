FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
# Instala dependências do sistema (incluindo ping e curl)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Expõe porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "run.py"]
