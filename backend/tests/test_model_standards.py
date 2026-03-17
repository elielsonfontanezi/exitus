# -*- coding: utf-8 -*-
"""
EXITUS-ENUMFIX-002 — Teste de padrões de código nos models SQLAlchemy.

Verifica que toda coluna Enum() usa values_callable para garantir que
os valores lowercase do Python Enum sejam usados no PostgreSQL.

Falha automaticamente se um novo model adicionar Enum() sem values_callable.
"""

import ast
import os
import pytest

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')


def _listar_arquivos_models():
    """Retorna lista de arquivos .py no diretório de models (exceto __init__ e __pycache__)."""
    arquivos = []
    for nome in os.listdir(MODELS_DIR):
        if nome.endswith('.py') and not nome.startswith('__'):
            arquivos.append(os.path.join(MODELS_DIR, nome))
    return arquivos


def _verificar_enum_sem_values_callable(filepath: str) -> list:
    """
    Analisa o AST do arquivo e retorna lista de violações:
    chamadas Enum(...) sem argumento values_callable.

    Retorna lista de strings no formato 'arquivo:linha — descrição'.
    """
    violacoes = []
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    nome_arquivo = os.path.basename(filepath)

    for node in ast.walk(tree):
        # Procura por chamadas do tipo Column(Enum(...), ...)
        if not isinstance(node, ast.Call):
            continue

        # Verifica se é Column(...)
        func_name = ''
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name != 'Column':
            continue

        # Dentro dos args do Column, procura Enum(...)
        for arg in node.args:
            if not isinstance(arg, ast.Call):
                continue

            enum_func = ''
            if isinstance(arg.func, ast.Name):
                enum_func = arg.func.id
            elif isinstance(arg.func, ast.Attribute):
                enum_func = arg.func.attr

            if enum_func != 'Enum':
                continue

            # Verifica se o primeiro argumento do Enum é um tipo Python Enum
            # (se for apenas strings, é um Enum nativo SQL — não precisa values_callable)
            tem_tipo_python = False
            for enum_arg in arg.args:
                if isinstance(enum_arg, ast.Name):
                    # Nome em PascalCase provavelmente é um Python Enum
                    if enum_arg.id[0].isupper():
                        tem_tipo_python = True
                        break

            if not tem_tipo_python:
                continue

            # Verifica se values_callable está nos kwargs
            tem_values_callable = any(
                kw.arg == 'values_callable'
                for kw in arg.keywords
            )

            if not tem_values_callable:
                violacoes.append(
                    f'{nome_arquivo}:{node.lineno} — '
                    f'Enum({", ".join(ast.unparse(a) for a in arg.args)}) '
                    f'sem values_callable'
                )

    return violacoes


class TestModelStandards:
    """Testes de conformidade de padrões nos models SQLAlchemy."""

    def test_enum_columns_tem_values_callable(self):
        """
        EXITUS-ENUMFIX-002: toda coluna Column(Enum(PythonEnum)) deve usar
        values_callable=lambda x: [e.value for e in x].

        Isso garante que o SQLAlchemy use os .value lowercase do Enum Python
        em vez dos nomes dos membros (UPPERCASE), mantendo paridade com o banco.
        """
        arquivos = _listar_arquivos_models()
        assert arquivos, f"Nenhum model encontrado em {MODELS_DIR}"

        todas_violacoes = []
        for filepath in sorted(arquivos):
            violacoes = _verificar_enum_sem_values_callable(filepath)
            todas_violacoes.extend(violacoes)

        if todas_violacoes:
            mensagem = (
                "\n\nViolações EXITUS-ENUMFIX-002 — Enum sem values_callable:\n"
                + "\n".join(f"  ❌ {v}" for v in todas_violacoes)
                + "\n\nCorreção obrigatória (CODING_STANDARDS.md §ENUM):\n"
                + "  tipo = Column(Enum(MeuEnum, values_callable=lambda x: [e.value for e in x]), ...)\n"
            )
            pytest.fail(mensagem)
