# -*- coding: utf-8 -*-
"""
Exitus - Seed de Regras Fiscais Brasileiras
Popular tabela regra_fiscal com regras de IR do Brasil
"""

from app import create_app
from app.database import db
from app.models import RegraFiscal, IncidenciaImposto
from decimal import Decimal
from datetime import date


def seed_regras_fiscais_br():
    """Cria regras fiscais brasileiras"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Regras Fiscais Brasileiras")
        print("=" * 50)
        
        # Verificar se já existem regras BR
        count = RegraFiscal.query.filter_by(pais='BR').count()
        if count > 0:
            print(f"⚠ Já existem {count} regras fiscais brasileiras.")
            resposta = input("Deseja recriar as regras BR? (s/N): ").lower()
            if resposta != 's':
                print("✗ Seed cancelado pelo usuário.")
                return
            
            # Limpar regras BR existentes
            RegraFiscal.query.filter_by(pais='BR').delete()
            db.session.commit()
            print("✓ Regras fiscais brasileiras anteriores removidas.")
        
        # Regras fiscais brasileiras
        regras = [
            {
                'tipo_ativo': 'ACAO',
                'tipo_operacao': 'SWING_TRADE',
                'aliquota_ir': Decimal('15.0000'),
                'valor_isencao': Decimal('20000.00'),
                'incide_sobre': IncidenciaImposto.LUCRO,
                'descricao': 'IR sobre ganho de capital em ações - Swing Trade. Isenção para vendas até R$ 20.000,00 por mês.'
            },
            {
                'tipo_ativo': 'ACAO',
                'tipo_operacao': 'DAY_TRADE',
                'aliquota_ir': Decimal('20.0000'),
                'valor_isencao': None,
                'incide_sobre': IncidenciaImposto.LUCRO,
                'descricao': 'IR sobre ganho de capital em Day Trade. SEM isenção, alíquota de 20%.'
            },
            {
                'tipo_ativo': 'FII',
                'tipo_operacao': 'SWING_TRADE',
                'aliquota_ir': Decimal('20.0000'),
                'valor_isencao': None,
                'incide_sobre': IncidenciaImposto.LUCRO,
                'descricao': 'IR sobre ganho de capital em FIIs. SEM isenção, alíquota de 20%.'
            },
            {
                'tipo_ativo': None,  # Aplica a todos
                'tipo_operacao': None,
                'aliquota_ir': Decimal('15.0000'),
                'valor_isencao': None,
                'incide_sobre': IncidenciaImposto.PROVENTO,
                'descricao': 'IR sobre JCP (Juros sobre Capital Próprio). Retido na fonte, alíquota de 15%.'
            },
            {
                'tipo_ativo': 'FII',
                'tipo_operacao': None,
                'aliquota_ir': Decimal('0.0000'),
                'valor_isencao': None,
                'incide_sobre': IncidenciaImposto.PROVENTO,
                'descricao': 'Rendimentos de FII são ISENTOS de IR para pessoa física (requisitos: FII com +50 cotistas, cotas negociadas em bolsa, investidor com <10% das cotas).'
            },
            {
                'tipo_ativo': 'ACAO',
                'tipo_operacao': None,
                'aliquota_ir': Decimal('0.0000'),
                'valor_isencao': None,
                'incide_sobre': IncidenciaImposto.PROVENTO,
                'descricao': 'Dividendos de ações são ISENTOS de IR para pessoa física no Brasil.'
            },
        ]
        
        created_regras = []
        
        print("\n📋 Criando Regras...")
        for regra_data in regras:
            regra = RegraFiscal(
                pais='BR',
                tipo_ativo=regra_data['tipo_ativo'],
                tipo_operacao=regra_data['tipo_operacao'],
                aliquota_ir=regra_data['aliquota_ir'],
                valor_isencao=regra_data['valor_isencao'],
                incide_sobre=regra_data['incide_sobre'],
                descricao=regra_data['descricao'],
                vigencia_inicio=date(2024, 1, 1),
                ativa=True
            )
            db.session.add(regra)
            created_regras.append(regra)
            
            tipo_str = regra_data['tipo_ativo'] or 'TODOS'
            op_str = regra_data['tipo_operacao'] or 'TODAS'
            isencao_str = f"R$ {regra_data['valor_isencao']}" if regra_data['valor_isencao'] else "SEM"
            
            print(f"  ✓ {tipo_str:10} | {op_str:12} | IR: {regra_data['aliquota_ir']:6}% | Isenção: {isencao_str}")
        
        # Commit no banco
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print(f"✓ {len(created_regras)} regras fiscais criadas!")
            print("=" * 50)
            print("\n📌 RESUMO DAS REGRAS:")
            print("-" * 50)
            print("• Ações Swing Trade: 15% IR (isenção até R$ 20k/mês)")
            print("• Ações Day Trade: 20% IR (sem isenção)")
            print("• FII Swing Trade: 20% IR (sem isenção)")
            print("• Dividendos de Ações: ISENTO")
            print("• Rendimentos de FII: ISENTO*")
            print("• JCP: 15% IR retido na fonte")
            print("-" * 50)
            print("* Requisitos para isenção de FII aplicam-se\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao criar regras fiscais: {e}")
            raise


if __name__ == '__main__':
    seed_regras_fiscais_br()
