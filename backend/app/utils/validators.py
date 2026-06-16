# -*- coding: utf-8 -*-
"""
Exitus - Validators
Funções de validação utilitárias
"""

import re
from uuid import UUID
from typing import Optional


def validate_uuid(uuid_string: str) -> bool:
    """
    Valida se uma string é um UUID válido
    
    Args:
        uuid_string (str): String a validar
        
    Returns:
        bool: True se for UUID válido, False caso contrário
    """
    if not uuid_string or not isinstance(uuid_string, str):
        return False
    
    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """
    Valida se um email está em formato válido
    
    Args:
        email (str): Email a validar
        
    Returns:
        bool: True se for email válido, False caso contrário
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_ticker_b3(ticker: str) -> bool:
    """
    Valida se um ticker segue o padrão B3
    
    Args:
        ticker (str): Ticker a validar
        
    Returns:
        bool: True se for ticker válido, False caso contrário
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Padrão B3: 4-5 letras + opcional FII (11) ou BDR (34, 35)
    pattern = r'^[A-Z]{4}[A-Z0-9]?[F0-9]?$'
    return re.match(pattern, ticker.upper()) is not None


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida se um CNPJ está em formato válido
    
    Args:
        cnpj (str): CNPJ a validar
        
    Returns:
        bool: True se for CNPJ válido, False caso contrário
    """
    if not cnpj or not isinstance(cnpj, str):
        return False
    
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # CNPJ deve ter 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Não pode ser uma sequência de dígitos iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Cálculo dos dígitos verificadores
    def calculate_digit(cnpj, weight):
        sum = 0
        for i in range(len(weight)):
            sum += int(cnpj[i]) * weight[i]
        remainder = sum % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Primeiro dígito verificador
    weight1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = calculate_digit(cnpj, weight1)
    
    # Segundo dígito verificador
    weight2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit2 = calculate_digit(cnpj, weight2)
    
    return int(cnpj[12]) == digit1 and int(cnpj[13]) == digit2


def validate_positive_number(value: any, allow_zero: bool = False) -> bool:
    """
    Valida se um valor é um número positivo
    
    Args:
        value: Valor a validar
        allow_zero (bool): Se True, permite zero como válido
        
    Returns:
        bool: True se for positivo, False caso contrário
    """
    try:
        num_value = float(value)
        if allow_zero:
            return num_value >= 0
        return num_value > 0
    except (ValueError, TypeError):
        return False


def validate_date_string(date_string: str, date_format: str = '%Y-%m-%d') -> bool:
    """
    Valida se uma string está em formato de data válido
    
    Args:
        date_string (str): String a validar
        date_format (str): Formato esperado da data
        
    Returns:
        bool: True se for data válida, False caso contrário
    """
    if not date_string or not isinstance(date_string, str):
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def validate_password_strength(password: str) -> dict:
    """
    Valida a força de uma senha
    
    Args:
        password (str): Senha a validar
        
    Returns:
        dict: Resultado da validação com detalhes
    """
    result = {
        'is_valid': False,
        'score': 0,
        'errors': []
    }
    
    if not password or not isinstance(password, str):
        result['errors'].append('Senha é obrigatória')
        return result
    
    if len(password) < 8:
        result['errors'].append('Senha deve ter pelo menos 8 caracteres')
    else:
        result['score'] += 1
    
    if not re.search(r'[a-z]', password):
        result['errors'].append('Senha deve ter pelo menos uma letra minúscula')
    else:
        result['score'] += 1
    
    if not re.search(r'[A-Z]', password):
        result['errors'].append('Senha deve ter pelo menos uma letra maiúscula')
    else:
        result['score'] += 1
    
    if not re.search(r'\d', password):
        result['errors'].append('Senha deve ter pelo menos um número')
    else:
        result['score'] += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['errors'].append('Senha deve ter pelo menos um caractere especial')
    else:
        result['score'] += 1
    
    result['is_valid'] = len(result['errors']) == 0
    return result
