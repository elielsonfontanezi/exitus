# -*- coding: utf-8 -*-
"""
Exitus - Executar Todos os Seeds
Script master para popular o banco com dados iniciais
"""

import sys
from app.seeds.seed_usuarios import seed_usuarios
from app.seeds.seed_ativos_br import seed_ativos_br
from app.seeds.seed_regras_fiscais_br import seed_regras_fiscais_br
from app.seeds.seed_ativos_renda_fixa_br import seed_renda_fixa_br
from app.seeds.seed_feriados_b3 import seed_feriados_b3
from app.seeds.seed_fontes_dados import seed_fontes_dados


def run_all_seeds():
    """Executa todos os seeds em sequência"""
    
    print("\n" + "=" * 60)
    print("  EXITUS - EXECUTAR TODOS OS SEEDS")
    print("=" * 60)
    print("\nEste script irá popular o banco com dados iniciais:")
    print("  1. Usuários (4)")
    print("  2. Ativos BR (25)")
    print("  3. Regras Fiscais BR (6)")
    print("  4. Feriados B3 2025-2026 (30)")
    print("  5. Fontes de Dados (7)")
    print("\n⚠ ATENÇÃO: Seeds existentes serão solicitados para confirmação.\n")
    
    resposta = input("Deseja continuar? (s/N): ").lower()
    if resposta != 's':
        print("\n✗ Operação cancelada pelo usuário.\n")
        return
    
    seeds = [
        ("Usuários", seed_usuarios),
        ("Ativos BR", seed_ativos_br),
        ("Renda Fixa BR", seed_renda_fixa_br),
        ("Feriados B3", seed_feriados_b3),
        ("Fontes de Dados", seed_fontes_dados),
        ("Regras Fiscais BR", seed_regras_fiscais_br),
    ]
    
    sucessos = 0
    erros = 0
    
    for nome, seed_func in seeds:
        print("\n" + "=" * 60)
        try:
            seed_func()
            sucessos += 1
        except KeyboardInterrupt:
            print(f"\n\n⚠ Seed '{nome}' interrompido pelo usuário.")
            print("Processo de seeds cancelado.\n")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Erro ao executar seed '{nome}': {e}")
            erros += 1
            resposta = input("\nDeseja continuar com os próximos seeds? (s/N): ").lower()
            if resposta != 's':
                break
    
    # Resumo final
    print("\n" + "=" * 60)
    print("  RESUMO FINAL")
    print("=" * 60)
    print(f"✓ Seeds executados com sucesso: {sucessos}")
    if erros > 0:
        print(f"✗ Seeds com erro: {erros}")
    print("=" * 60 + "\n")
    
    if erros == 0:
        print("🎉 Todos os seeds foram executados com sucesso!")
        print("O banco de dados está pronto para uso.\n")
    else:
        print("⚠ Alguns seeds falharam. Verifique os erros acima.\n")


if __name__ == '__main__':
    run_all_seeds()
