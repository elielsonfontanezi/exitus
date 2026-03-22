def _seed_historico_patrimonio(self):
    """Seed de histórico patrimonial"""
    if 'historico_patrimonio' not in self.scenario_data:
        return
    
    from decimal import Decimal
    from datetime import datetime
    from app.models.historico_patrimonio import HistoricoPatrimonio
    
    historico_data = self.scenario_data['historico_patrimonio']
    print(f'📊 Criando {len(historico_data)} registros de histórico patrimonial...')
    
    for hist_data in historico_data:
        usuario_id = self.references['usuarios'].get(hist_data['usuario'])
        
        if not usuario_id:
            print(f"⚠️  Usuário não encontrado: {hist_data['usuario']}")
            continue
        
        data_snapshot = datetime.strptime(hist_data['data'], '%Y-%m-%d').date()
        
        existing = HistoricoPatrimonio.query.filter_by(
            usuario_id=usuario_id,
            data=data_snapshot
        ).first()
        
        if existing:
            print(f"⚠️  Histórico já existe para {hist_data['usuario']} em {hist_data['data']}, pulando...")
            continue
        
        historico = HistoricoPatrimonio(
            usuario_id=usuario_id,
            data=data_snapshot,
            patrimonio_total=Decimal(str(hist_data['patrimonio_total'])),
            patrimonio_renda_variavel=Decimal(str(hist_data.get('patrimonio_renda_variavel', 0))),
            patrimonio_renda_fixa=Decimal(str(hist_data.get('patrimonio_renda_fixa', 0))),
            saldo_caixa=Decimal(str(hist_data.get('saldo_caixa', 0))),
            observacoes=hist_data.get('observacoes')
        )
        
        from app.database import db
        db.session.add(historico)
        print(f"✅ Histórico criado: {hist_data['usuario']} - {hist_data['data']} - R$ {hist_data['patrimonio_total']}")
    
    from app.database import db
    db.session.flush()
