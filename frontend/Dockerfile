FROM python:3.11-slim

WORKDIR /app

# Instala ferramentas úteis de diagnóstico
RUN apt-get update && apt-get install -y     curl     && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Se não existir .env dentro da imagem, cria a partir do exemplo (útil para dev)
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Expõe porta
EXPOSE 8080

# Comando de inicialização
CMD ["python", "run.py"]
