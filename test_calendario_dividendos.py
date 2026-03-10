#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples do Calendário de Dividendos - DIVCALENDAR-001
"""

import requests
import json
from datetime import date, datetime

# Configuração
BASE_URL = "http://localhost:5000"
TOKEN = None

def login():
    """Faz login e obtém token JWT"""
    global TOKEN
    
    login_data = {
        "username": "admin",
        "password": "senha123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get("data", {}).get("access_token")
        print(f"✅ Login realizado com sucesso")
        print(f"🔑 Token: {TOKEN[:50]}..." if TOKEN else "❌ Token não encontrado")
        return True
    else:
        print(f"❌ Falha no login: {response.status_code} - {response.text}")
        return False

def test_listar_calendario():
    """Testa listagem de calendário"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.get(f"{BASE_URL}/api/calendario-dividendos/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Listar calendário: {data.get('data', {}).get('total', 0)} itens")
        return True
    else:
        print(f"❌ Falha ao listar: {response.status_code} - {response.text}")
        return False

def test_gerar_calendario():
    """Testa geração automática de calendário"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Extrair user_id do token (simplificado)
    import base64
    import json
    
    # Decodificar payload do JWT
    payload = TOKEN.split('.')[1]
    # Adicionar padding se necessário
    padding = '=' * (4 - len(payload) % 4)
    decoded = base64.b64decode(payload + padding)
    user_data = json.loads(decoded)
    usuario_id = user_data.get('sub')
    
    data = {
        "usuario_id": usuario_id,
        "meses_futuros": 6
    }
    
    response = requests.post(f"{BASE_URL}/api/calendario-dividendos/gerar", 
                           json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        total = result.get("data", {}).get("total", 0)
        print(f"✅ Gerar calendário: {total} itens gerados")
        return True
    else:
        print(f"❌ Falha ao gerar: {response.status_code} - {response.text}")
        return False

def test_resumo_calendario():
    """Testa resumo do calendário"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.get(f"{BASE_URL}/api/calendario-dividendos/resumo", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        total = data.get("data", {}).get("total_itens", 0)
        valor_estimado = data.get("data", {}).get("valor_total_estimado", 0)
        print(f"✅ Resumo: {total} itens, R$ {valor_estimado:.2f} estimado")
        return True
    else:
        print(f"❌ Falha no resumo: {response.status_code} - {response.text}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Testando Calendário de Dividendos - DIVCALENDAR-001")
    print("=" * 50)
    
    # Login
    if not login():
        return
    
    print()
    
    # Testes
    testes = [
        ("Listar Calendário", test_listar_calendario),
        ("Gerar Calendário", test_gerar_calendario),
        ("Resumo Calendário", test_resumo_calendario),
    ]
    
    resultados = []
    
    for nome, teste in testes:
        print(f"🧪 {nome}...")
        resultado = teste()
        resultados.append((nome, resultado))
        print()
    
    # Resumo final
    print("=" * 50)
    print("📊 Resultados:")
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {nome}: {status}")
    
    passaram = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    print(f"\n🎯 Total: {passaram}/{total} testes passaram")
    
    if passaram == total:
        print("🎉 Todos os testes passaram! DIVCALENDAR-001 funcionando!")
    else:
        print("⚠️ Alguns testes falharam. Verificar os logs.")

if __name__ == "__main__":
    main()
