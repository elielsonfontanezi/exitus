#!/bin/bash
# Configura ambiente (development, staging, production)

ENV=${1:-development}

echo "Configurando ambiente: $ENV"

case $ENV in
  development)
    echo "Usando configurações de desenvolvimento..."
    cp backend/.env.example backend/.env
    cp frontend/.env.example frontend/.env
    ;;

  staging)
    echo "Usando configurações de staging..."
    if [ -f backend/.env.staging ]; then
      cp backend/.env.staging backend/.env
    else
      echo "ERRO: backend/.env.staging não encontrado"; exit 1
    fi
    if [ -f frontend/.env.staging ]; then
      cp frontend/.env.staging frontend/.env
    else
      echo "ERRO: frontend/.env.staging não encontrado"; exit 1
    fi
    ;;

  production)
    echo "Usando configurações de produção..."
    if [ -f backend/.env.production ]; then
      cp backend/.env.production backend/.env
    else
      echo "ERRO: backend/.env.production não encontrado"; exit 1
    fi
    if [ -f frontend/.env.production ]; then
      cp frontend/.env.production frontend/.env
    else
      echo "ERRO: frontend/.env.production não encontrado"; exit 1
    fi
    ;;

  *)
    echo "Ambiente inválido. Use: development, staging ou production"; exit 1;;
esac

echo "Ambiente $ENV configurado com sucesso!"
