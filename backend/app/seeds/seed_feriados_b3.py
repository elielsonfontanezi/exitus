# -*- coding: utf-8 -*-
"""
Exitus - Seed de Feriados B3
Popular tabela feriado_mercado com feriados da B3
"""

from app import create_app
from app.database import db
from app.models import FeriadoMercado, TipoFeriado
from datetime import date


def seed_feriados_b3():
    """Cria feriados da B3 para 2025 e 2026"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Feriados B3 (2025-2026)")
        print("=" * 50)
        
        # Verificar se já existem feriados B3
        count = FeriadoMercado.query.filter_by(pais='BR', mercado='B3').count()
        if count > 0:
            print(f"⚠ Já existem {count} feriados B3 cadastrados.")
            resposta = input("Deseja recriar os feriados? (s/N): ").lower()
            if resposta != 's':
                print("✗ Seed cancelado pelo usuário.")
                return
            
            # Limpar feriados B3 existentes
            FeriadoMercado.query.filter_by(pais='BR', mercado='B3').delete()
            db.session.commit()
            print("✓ Feriados B3 anteriores removidos.")
        
        # Feriados B3 2025
        feriados_2025 = [
            (date(2025, 1, 1), 'Confraternização Universal', TipoFeriado.NACIONAL, True),
            (date(2025, 3, 3), 'Carnaval', TipoFeriado.NACIONAL, False),
            (date(2025, 3, 4), 'Carnaval (Quarta de Cinzas - meio período)', TipoFeriado.NACIONAL, False),
            (date(2025, 4, 18), 'Sexta-feira Santa', TipoFeriado.NACIONAL, True),
            (date(2025, 4, 21), 'Tiradentes', TipoFeriado.NACIONAL, True),
            (date(2025, 5, 1), 'Dia do Trabalho', TipoFeriado.NACIONAL, True),
            (date(2025, 6, 19), 'Corpus Christi', TipoFeriado.NACIONAL, False),
            (date(2025, 9, 7), 'Independência do Brasil', TipoFeriado.NACIONAL, True),
            (date(2025, 10, 12), 'Nossa Senhora Aparecida', TipoFeriado.NACIONAL, True),
            (date(2025, 11, 2), 'Finados', TipoFeriado.NACIONAL, True),
            (date(2025, 11, 15), 'Proclamação da República', TipoFeriado.NACIONAL, True),
            (date(2025, 11, 20), 'Dia da Consciência Negra', TipoFeriado.NACIONAL, True),
            (date(2025, 12, 24), 'Véspera de Natal (meio período)', TipoFeriado.FECHAMENTO_ANTECIPADO, False),
            (date(2025, 12, 25), 'Natal', TipoFeriado.NACIONAL, True),
            (date(2025, 12, 31), 'Véspera de Ano Novo (meio período)', TipoFeriado.FECHAMENTO_ANTECIPADO, False),
        ]
        
        # Feriados B3 2026
        feriados_2026 = [
            (date(2026, 1, 1), 'Confraternização Universal', TipoFeriado.NACIONAL, True),
            (date(2026, 2, 16), 'Carnaval', TipoFeriado.NACIONAL, False),
            (date(2026, 2, 17), 'Carnaval (Quarta de Cinzas - meio período)', TipoFeriado.NACIONAL, False),
            (date(2026, 4, 3), 'Sexta-feira Santa', TipoFeriado.NACIONAL, True),
            (date(2026, 4, 21), 'Tiradentes', TipoFeriado.NACIONAL, True),
            (date(2026, 5, 1), 'Dia do Trabalho', TipoFeriado.NACIONAL, True),
            (date(2026, 6, 4), 'Corpus Christi', TipoFeriado.NACIONAL, False),
            (date(2026, 9, 7), 'Independência do Brasil', TipoFeriado.NACIONAL, True),
            (date(2026, 10, 12), 'Nossa Senhora Aparecida', TipoFeriado.NACIONAL, True),
            (date(2026, 11, 2), 'Finados', TipoFeriado.NACIONAL, True),
            (date(2026, 11, 15), 'Proclamação da República', TipoFeriado.NACIONAL, True),
            (date(2026, 11, 20), 'Dia da Consciência Negra', TipoFeriado.NACIONAL, True),
            (date(2026, 12, 24), 'Véspera de Natal (meio período)', TipoFeriado.FECHAMENTO_ANTECIPADO, False),
            (date(2026, 12, 25), 'Natal', TipoFeriado.NACIONAL, True),
            (date(2026, 12, 31), 'Véspera de Ano Novo (meio período)', TipoFeriado.FECHAMENTO_ANTECIPADO, False),
        ]
        
        todos_feriados = feriados_2025 + feriados_2026
        created_feriados = []
        
        print("\n📅 Criando Feriados 2025...")
        for data_feriado, nome, tipo, recorrente in feriados_2025:
            feriado = FeriadoMercado(
                pais='BR',
                mercado='B3',
                data_feriado=data_feriado,
                tipo_feriado=tipo,
                nome=nome,
                recorrente=recorrente
            )
            db.session.add(feriado)
            created_feriados.append(feriado)
            tipo_icon = "🚫" if tipo == TipoFeriado.NACIONAL else "⏰"
            print(f"  {tipo_icon} {data_feriado.strftime('%d/%m/%Y')} - {nome}")
        
        print("\n📅 Criando Feriados 2026...")
        for data_feriado, nome, tipo, recorrente in feriados_2026:
            feriado = FeriadoMercado(
                pais='BR',
                mercado='B3',
                data_feriado=data_feriado,
                tipo_feriado=tipo,
                nome=nome,
                recorrente=recorrente
            )
            db.session.add(feriado)
            created_feriados.append(feriado)
            tipo_icon = "🚫" if tipo == TipoFeriado.NACIONAL else "⏰"
            print(f"  {tipo_icon} {data_feriado.strftime('%d/%m/%Y')} - {nome}")
        
        # Commit no banco
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print(f"✓ {len(created_feriados)} feriados criados!")
            print(f"  - 2025: {len(feriados_2025)} feriados")
            print(f"  - 2026: {len(feriados_2026)} feriados")
            print("=" * 50)
            print("\n📌 LEGENDA:")
            print("  🚫 = Fechamento total (sem pregão)")
            print("  ⏰ = Fechamento antecipado (meio período)\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao criar feriados: {e}")
            raise


if __name__ == '__main__':
    seed_feriados_b3()
