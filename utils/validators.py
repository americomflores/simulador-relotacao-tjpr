"""
Validações centralizadas de dados.
"""
import re
from datetime import date
from data import ANEXO_I, ANEXO_II
from exceptions import ValidationError
# DATA_LIMITE_ESTAGIO removido - Edital 01/2026 permite servidores em estágio probatório


def validar_telefone(telefone):
    """
    Valida formato de telefone.
    
    Args:
        telefone: Telefone a validar
        
    Returns:
        True se válido, False caso contrário
    """
    if not telefone:
        return False
    
    numeros = re.sub(r'\D', '', str(telefone))
    # Telefone deve ter 10 ou 11 dígitos (com DDD)
    return 10 <= len(numeros) <= 11


def validar_matricula(matricula):
    """
    Valida formato de matrícula.
    
    Args:
        matricula: Matrícula a validar
        
    Returns:
        True se válido, False caso contrário
    """
    if not matricula:
        return False
    
    # Matrícula deve ser numérica e ter pelo menos 4 dígitos
    matricula_str = str(matricula).strip()
    return matricula_str.isdigit() and len(matricula_str) >= 4


def validar_data_admissao(data_admissao):
    """
    Valida data de admissão.
    
    Args:
        data_admissao: datetime.date ou string
        
    Returns:
        Tupla (is_valid, error_message)
    """
    if not data_admissao:
        return False, "Data de admissão é obrigatória"
    
    if isinstance(data_admissao, str):
        try:
            from datetime import datetime
            data_admissao = datetime.strptime(data_admissao, "%d/%m/%Y").date()
        except ValueError:
            return False, "Formato de data inválido (use DD/MM/YYYY)"
    
    if not isinstance(data_admissao, date):
        return False, "Data de admissão deve ser uma data válida"
    
    # Data não pode ser no futuro
    if data_admissao > date.today():
        return False, "Data de admissão não pode ser no futuro"
    
    # Data não pode ser muito antiga (antes de 1950)
    if data_admissao < date(1950, 1, 1):
        return False, "Data de admissão muito antiga (antes de 1950)"
    
    return True, ""


def validar_codigo_unidade(codigo, anexo=None):
    """
    Valida se código de unidade existe no Anexo I ou II.
    
    Args:
        codigo: Código da unidade (ex: "A1-001", "A2-001")
        anexo: "I" para Anexo I, "II" para Anexo II, None para ambos
        
    Returns:
        Tupla (is_valid, error_message)
    """
    if not codigo:
        return True, ""  # Código vazio é válido (opcional)
    
    codigo = str(codigo).strip()
    
    if anexo == "I":
        if codigo not in ANEXO_I:
            return False, f"Código {codigo} não encontrado no Anexo I"
    elif anexo == "II":
        if codigo not in ANEXO_II:
            return False, f"Código {codigo} não encontrado no Anexo II"
    else:
        # Verificar em ambos
        if codigo not in ANEXO_I and codigo not in ANEXO_II:
            return False, f"Código {codigo} não encontrado nos Anexos I ou II"
    
    return True, ""


def validar_inscricao(nome, matricula, data_admissao, lotacao_atual, escolha_anexo1="", escolha_anexo2=""):
    """
    Valida todos os campos de uma inscrição.
    
    Args:
        nome: Nome do servidor
        matricula: Matrícula
        data_admissao: Data de admissão
        lotacao_atual: Código da lotação atual
        escolha_anexo1: Código da escolha Anexo I (opcional)
        escolha_anexo2: Código da escolha Anexo II (opcional)
        
    Returns:
        Tupla (is_valid, error_messages)
    """
    errors = []
    
    # Validar nome
    if not nome or not nome.strip():
        errors.append("Nome é obrigatório")
    
    # Validar matrícula
    if not validar_matricula(matricula):
        errors.append("Matrícula inválida (deve ter pelo menos 4 dígitos numéricos)")
    
    # Validar data de admissão
    is_valid_date, date_error = validar_data_admissao(data_admissao)
    if not is_valid_date:
        errors.append(date_error)
    
    # Validar lotação atual
    is_valid_lotacao, lotacao_error = validar_codigo_unidade(lotacao_atual, "II")
    if not is_valid_lotacao:
        errors.append(f"Lotação atual: {lotacao_error}")
    
    # Validar escolha Anexo I (se preenchida)
    if escolha_anexo1:
        is_valid_a1, a1_error = validar_codigo_unidade(escolha_anexo1, "I")
        if not is_valid_a1:
            errors.append(f"Escolha Anexo I: {a1_error}")
    
    # Validar escolha Anexo II (se preenchida)
    if escolha_anexo2:
        is_valid_a2, a2_error = validar_codigo_unidade(escolha_anexo2, "II")
        if not is_valid_a2:
            errors.append(f"Escolha Anexo II: {a2_error}")
    
    # Validar que origem e destino não são iguais
    if lotacao_atual and escolha_anexo2 and lotacao_atual == escolha_anexo2:
        errors.append("Lotações de origem e destino não podem ser iguais")
    
    return len(errors) == 0, errors

