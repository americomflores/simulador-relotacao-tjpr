"""
Handlers de erro padronizados para a aplicação.
"""
import streamlit as st
from utils.logger import log_error
from exceptions import (
    AuthenticationError,
    SheetsError,
    SimulationError,
    ValidationError,
    ConfigurationError
)


def handle_error(error, context="", show_to_user=True):
    """
    Handler universal de erros.

    Args:
        error: Exceção capturada
        context: Contexto onde ocorreu o erro
        show_to_user: Se deve mostrar erro ao usuário via st.error()
    """
    log_error(error, context)
    mensagem = _determinar_mensagem_usuario(error)
    if show_to_user:
        st.error(mensagem)


def handle_success(mensagem, show_balloons=False):
    """
    Handler de sucesso padronizado.

    Args:
        mensagem: Mensagem de sucesso a exibir
        show_balloons: Se deve mostrar animação de comemoração
    """
    st.success(mensagem)
    if show_balloons:
        st.balloons()


def _determinar_mensagem_usuario(error):
    """
    Determina mensagem amigável baseada no tipo de erro.

    Args:
        error: Exceção capturada

    Returns:
        Mensagem formatada para o usuário
    """
    if isinstance(error, AuthenticationError):
        return "❌ **Erro de autenticação**\n\nVerifique suas credenciais e tente novamente."
    elif isinstance(error, SheetsError):
        return "❌ **Erro ao acessar dados**\n\nNão foi possível conectar com o banco de dados. Tente novamente em alguns instantes."
    elif isinstance(error, SimulationError):
        return f"❌ **Erro no cálculo da simulação**\n\n{str(error)}\n\nVerifique os dados e tente novamente."
    elif isinstance(error, ValidationError):
        return f"⚠️ **Erro de validação**\n\n{str(error)}"
    elif isinstance(error, ConfigurationError):
        return f"❌ **Erro de configuração**\n\n{str(error)}\n\nContate o administrador do sistema."
    elif isinstance(error, KeyError):
        return f"❌ **Erro de dados**\n\nChave não encontrada: {str(error)}\n\nOs dados podem estar incompletos ou corrompidos."
    elif isinstance(error, ValueError):
        return f"❌ **Erro de valor**\n\n{str(error)}\n\nVerifique se os dados estão no formato correto."
    elif isinstance(error, TypeError):
        return f"❌ **Erro de tipo**\n\n{str(error)}\n\nO tipo de dado fornecido não é compatível."
    elif isinstance(error, FileNotFoundError):
        return f"❌ **Arquivo não encontrado**\n\n{str(error)}"
    elif isinstance(error, PermissionError):
        return "❌ **Erro de permissão**\n\nVocê não tem permissão para realizar esta operação."
    else:
        return f"❌ **Erro inesperado**\n\n{type(error).__name__}: {str(error)}\n\nSe o problema persistir, contate o suporte."
