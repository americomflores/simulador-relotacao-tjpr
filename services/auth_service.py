"""
Serviço de autenticação e autorização.
"""
import re
import streamlit as st
from config.auth_config import AUTH_CODES, ADMIN_TELEFONES, ADMIN_SENHA
from exceptions import AuthenticationError
from utils.logger import log_operation, log_error


def formatar_telefone_display(telefone):
    """
    Formata telefone para exibição: (XX) XXXXX-XXXX.
    
    Args:
        telefone: Telefone em qualquer formato
        
    Returns:
        Telefone formatado para exibição
    """
    numeros = re.sub(r'\D', '', str(telefone))
    if len(numeros) == 0:
        return ""
    elif len(numeros) <= 2:
        return f"({numeros}"
    elif len(numeros) <= 7:
        return f"({numeros[:2]}) {numeros[2:]}"
    elif len(numeros) <= 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    else:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:11]}"


def limpar_telefone(telefone):
    """
    Remove tudo que não for número do telefone.
    
    Args:
        telefone: Telefone em qualquer formato
        
    Returns:
        Telefone apenas com números
    """
    return re.sub(r'\D', '', str(telefone))


def verificar_login(telefone, codigo):
    """
    Verifica se telefone e código são válidos.
    
    Args:
        telefone: Telefone do usuário
        codigo: Código de acesso
        
    Returns:
        True se credenciais são válidas, False caso contrário
    """
    try:
        telefone_limpo = limpar_telefone(telefone)
        codigo_upper = codigo.upper().strip()
        
        if telefone_limpo in AUTH_CODES:
            is_valid = AUTH_CODES[telefone_limpo] == codigo_upper
            if is_valid:
                log_operation("login_success", telefone_limpo)
            else:
                log_operation("login_failed", telefone_limpo, f"código inválido")
            return is_valid
        
        log_operation("login_failed", telefone_limpo, "telefone não encontrado")
        return False
    except Exception as e:
        log_error(e, "verificar_login")
        return False


def verificar_admin(telefone, senha):
    """
    Verifica se o usuário é administrador.
    
    Args:
        telefone: Telefone do usuário
        senha: Senha de administrador
        
    Returns:
        True se é admin, False caso contrário
    """
    try:
        telefone_limpo = limpar_telefone(telefone)
        is_admin = telefone_limpo in ADMIN_TELEFONES and senha == ADMIN_SENHA
        
        if is_admin:
            log_operation("admin_login", telefone_limpo)
        else:
            log_operation("admin_login_failed", telefone_limpo)
        
        return is_admin
    except Exception as e:
        log_error(e, "verificar_admin")
        return False


def is_admin():
    """
    Verifica se o usuário logado é administrador.
    
    Returns:
        True se é admin, False caso contrário
    """
    if "telefone_usuario" not in st.session_state:
        return False
    
    telefone = st.session_state.telefone_usuario
    return limpar_telefone(telefone) in ADMIN_TELEFONES


def get_usuario_logado():
    """
    Retorna o telefone formatado do usuário logado.
    
    Returns:
        Telefone formatado ou "Desconhecido"
    """
    if "telefone_usuario" in st.session_state and st.session_state.telefone_usuario:
        return formatar_telefone_display(st.session_state.telefone_usuario)
    return "Desconhecido"

