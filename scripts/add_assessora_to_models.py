#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar assessora_id aos models restantes
Parte do MULTICLIENTE-001 - Multi-tenancy
"""

import os
import re

# Models que precisam de assessora_id (já atualizados: usuario, portfolio, plano_venda, plano_compra)
MODELS_TO_UPDATE = [
    ('posicao', 'Posicao'),
    ('transacao', 'Transacao'),
    ('movimentacao_caixa', 'MovimentacaoCaixa'),
    ('provento', 'Provento'),
    ('saldo_prejuizo', 'SaldoPrejuizo'),
    ('saldo_darf_acumulado', 'SaldoDarfAcumulado'),
    ('configuracao_alerta', 'ConfiguracaoAlerta'),
    ('alerta', 'Alerta'),
    ('relatorio_performance', 'RelatorioPerformance'),
    ('auditoria_relatorio', 'AuditoriaRelatorio'),
    ('projecao_renda', 'ProjecaoRenda'),
    ('log_auditoria', 'LogAuditoria'),
    ('evento_custodia', 'EventoCustodia'),
    ('historico_preco', 'HistoricoPreco'),
    ('calendario_dividendo', 'CalendarioDividendo'),
    ('evento_corporativo', 'EventoCorporativo'),
]

BASE_PATH = '/home/p016525/elielson/exitus/backend/app/models'

def add_assessora_to_model(filename, classname):
    """Adiciona assessora_id a um model"""
    filepath = os.path.join(BASE_PATH, f'{filename}.py')
    
    if not os.path.exists(filepath):
        print(f"⚠️  Arquivo não encontrado: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica se já tem assessora_id
    if 'assessora_id' in content:
        print(f"✅ {classname}: já tem assessora_id")
        return True
    
    # 1. Adicionar import de ForeignKey se não existir
    if 'ForeignKey' not in content:
        content = content.replace(
            'from sqlalchemy import ',
            'from sqlalchemy import ForeignKey, '
        )
    
    # 2. Adicionar coluna assessora_id após a primeira ForeignKey encontrada
    # Procura por padrão de ForeignKey
    fk_pattern = r"(    \w+_id = (?:db\.)?Column\(UUID\(as_uuid=True\), ForeignKey\([^)]+\)[^)]*\))"
    
    if re.search(fk_pattern, content):
        # Adiciona após a primeira FK
        assessora_column = """
    assessora_id = Column(UUID(as_uuid=True), ForeignKey('assessora.id', ondelete='CASCADE'), nullable=True, index=True)"""
        
        content = re.sub(
            fk_pattern,
            r'\1' + assessora_column,
            content,
            count=1
        )
    else:
        print(f"⚠️  {classname}: Não encontrou padrão de ForeignKey")
        return False
    
    # 3. Adicionar relacionamento assessora
    # Procura por seção de relacionamentos
    rel_pattern = r"(    # Relacionamentos?\n)"
    
    if re.search(rel_pattern, content):
        assessora_rel = "    assessora = relationship('Assessora', back_populates='{}s')\n".format(filename)
        content = re.sub(rel_pattern, r'\1' + assessora_rel, content)
    else:
        print(f"⚠️  {classname}: Não encontrou seção de relacionamentos")
    
    # Salva arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {classname}: assessora_id adicionado")
    return True

def main():
    """Executa atualização em todos os models"""
    print("🚀 Adicionando assessora_id aos models...")
    print(f"📂 Base path: {BASE_PATH}\n")
    
    success = 0
    failed = 0
    
    for filename, classname in MODELS_TO_UPDATE:
        try:
            if add_assessora_to_model(filename, classname):
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {classname}: Erro - {e}")
            failed += 1
    
    print(f"\n📊 Resultado:")
    print(f"   ✅ Sucesso: {success}")
    print(f"   ❌ Falhou: {failed}")
    print(f"   📝 Total: {len(MODELS_TO_UPDATE)}")

if __name__ == '__main__':
    main()
