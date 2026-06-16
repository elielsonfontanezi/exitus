# -*- coding: utf-8 -*-
"""
EXITUS-EXPORT-001 — Testes de integração para exportação de dados.
Cobre os 3 endpoints: /api/export/transacoes, /api/export/proventos, /api/export/posicoes
Formatos: csv, excel, json, pdf
"""
import pytest


# ===========================================================================
# Helpers
# ===========================================================================

def _get(auth_client, url):
    return auth_client.get(url, headers=auth_client._auth_headers)


# ===========================================================================
# GET /api/export/transacoes
# ===========================================================================
class TestExportTransacoes:

    def test_sem_token_retorna_401(self, client):
        rv = client.get('/api/export/transacoes?formato=json')
        assert rv.status_code == 401

    def test_formato_json_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json')
        assert rv.status_code == 200
        assert 'application/json' in rv.content_type

    def test_formato_csv_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=csv')
        assert rv.status_code == 200
        assert 'text/csv' in rv.content_type

    def test_formato_excel_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=excel')
        assert rv.status_code == 200
        assert 'spreadsheetml' in rv.content_type

    def test_formato_pdf_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=pdf')
        assert rv.status_code == 200
        assert rv.content_type == 'application/pdf'

    def test_formato_invalido_retorna_422(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=xml')
        assert rv.status_code == 422

    def test_json_tem_estrutura_meta_dados(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json')
        data = rv.get_json()
        assert 'meta' in data
        assert 'dados' in data
        assert 'total' in data

    def test_json_meta_tem_campos_obrigatorios(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json')
        meta = rv.get_json()['meta']
        assert 'entidade' in meta
        assert 'formato' in meta
        assert 'gerado_em' in meta

    def test_json_entidade_correta(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json')
        assert rv.get_json()['meta']['entidade'] == 'transacoes'

    def test_content_disposition_tem_filename(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json')
        cd = rv.headers.get('Content-Disposition', '')
        assert 'attachment' in cd
        assert 'exitus_transacoes' in cd

    def test_filtro_data_inicio_invalida_retorna_422(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json&data_inicio=01-03-2025')
        assert rv.status_code == 422

    def test_filtro_data_valida_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json&data_inicio=2025-01-01&data_fim=2025-12-31')
        assert rv.status_code == 200

    def test_filtro_tipo_invalido_retorna_422(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json&tipo=invalido')
        assert rv.status_code == 422

    def test_filtro_tipo_valido_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=json&tipo=compra')
        assert rv.status_code == 200

    def test_csv_tem_cabecalho_metadados(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=csv')
        texto = rv.data.decode('utf-8-sig')
        assert '# Exitus' in texto

    def test_pdf_começa_com_signature(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=pdf')
        assert rv.data[:4] == b'%PDF'

    def test_excel_nao_esta_vazio(self, auth_client):
        rv = _get(auth_client, '/api/export/transacoes?formato=excel')
        assert len(rv.data) > 0

    def test_formato_default_e_json(self, auth_client):
        """Sem parâmetro formato → default json."""
        rv = _get(auth_client, '/api/export/transacoes')
        assert rv.status_code == 200
        assert 'application/json' in rv.content_type


# ===========================================================================
# GET /api/export/proventos
# ===========================================================================
class TestExportProventos:

    def test_sem_token_retorna_401(self, client):
        rv = client.get('/api/export/proventos?formato=json')
        assert rv.status_code == 401

    def test_formato_json_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/proventos?formato=json')
        assert rv.status_code == 200

    def test_formato_csv_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/proventos?formato=csv')
        assert rv.status_code == 200

    def test_formato_excel_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/proventos?formato=excel')
        assert rv.status_code == 200

    def test_formato_pdf_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/proventos?formato=pdf')
        assert rv.status_code == 200

    def test_json_entidade_correta(self, auth_client):
        rv = _get(auth_client, '/api/export/proventos?formato=json')
        assert rv.get_json()['meta']['entidade'] == 'proventos'

    def test_content_disposition_tem_filename(self, auth_client):
        rv = _get(auth_client, '/api/export/proventos?formato=csv')
        cd = rv.headers.get('Content-Disposition', '')
        assert 'exitus_proventos' in cd


# ===========================================================================
# GET /api/export/posicoes
# ===========================================================================
class TestExportPosicoes:

    def test_sem_token_retorna_401(self, client):
        rv = client.get('/api/export/posicoes?formato=json')
        assert rv.status_code == 401

    def test_formato_json_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/posicoes?formato=json')
        assert rv.status_code == 200

    def test_formato_csv_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/posicoes?formato=csv')
        assert rv.status_code == 200

    def test_formato_excel_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/posicoes?formato=excel')
        assert rv.status_code == 200

    def test_formato_pdf_retorna_200(self, auth_client):
        rv = _get(auth_client, '/api/export/posicoes?formato=pdf')
        assert rv.status_code == 200

    def test_json_entidade_correta(self, auth_client):
        rv = _get(auth_client, '/api/export/posicoes?formato=json')
        assert rv.get_json()['meta']['entidade'] == 'posicoes'

    def test_formato_invalido_retorna_422(self, auth_client):
        rv = _get(auth_client, '/api/export/posicoes?formato=docx')
        assert rv.status_code == 422
