"""
Handlers de erro padronizados para a aplicação.

Fornece funções para tratamento consistente de erros em toda a aplicação,
incluindo logging automático e exibição amigável ao usuário.
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

    Registra o erro no log e opcionalmente exibe mensagem ao usuário.

    Args:
        error: Exceção capturada
        context: Contexto onde ocorreu o erro (nome da função, operação, etc)
        show_to_user: Se deve mostrar erro ao usuário via st.error()

    Example:
        >>> try:
        ...     resultado = calcular_resultado(df)
        ... except Exception as e:
        ...     handle_error(e, "calcular_resultado")
    """
    # Log sempre
    log_error(error, context)

    # Determinar mensagem para usuário
    mensagem = _determinar_mensagem_usuario(error)

    # Mostrar ao usuário
    if show_to_user:
        st.error(mensagem)


def handle_success(mensagem, show_balloons=False):
    """
    Handler de sucesso padronizado.

    Args:
        mensagem: Mensagem de sucesso a exibir
        show_balloons: Se deve mostrar animação de comemoração

    Example:
        >>> handle_success("✅ Inscrição salva com sucesso!", show_balloons=True)
    """
    st.success(mensagem)
    if show_balloons:
        st.balloons()


def handle_warning(mensagem):
    """
    Handler de aviso padronizado.

    Args:
        mensagem: Mensagem de aviso a exibir

    Example:
        >>> handle_warning("⚠️ Servidor em estágio probatório")
    """
    st.warning(mensagem)


def handle_info(mensagem):
    """
    Handler de informação padronizado.

    Args:
        mensagem: Mensagem informativa a exibir

    Example:
        >>> handle_info("ℹ️ Dados carregados com sucesso")
    """
    st.info(mensagem)


def safe_execute(func, *args, context="", show_error=True, default_return=None, **kwargs):
    """
    Executa uma função com tratamento de erros automático.

    Args:
        func: Função a executar
        *args: Argumentos posicionais para a função
        context: Contexto da operação
        show_error: Se deve mostrar erro ao usuário
        default_return: Valor padrão a retornar em caso de erro
        **kwargs: Argumentos nomeados para a função

    Returns:
        Resultado da função ou default_return em caso de erro

    Example:
        >>> df = safe_execute(
        ...     carregar_inscricoes,
        ...     sheet,
        ...     context="carregar_inscricoes",
        ...     default_return=pd.DataFrame()
        ... )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context, show_to_user=show_error)
        return default_return


def _determinar_mensagem_usuario(error):
    """
    Determina mensagem amigável baseada no tipo de erro.

    Args:
        error: Exceção capturada

    Returns:
        Mensagem formatada para o usuário
    """
    # Exceções customizadas
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

    # Exceções comuns do Python
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

    # Erro genérico
    else:
        return f"❌ **Erro inesperado**\n\n{type(error).__name__}: {str(error)}\n\nSe o problema persistir, contate o suporte."


def with_error_handling(context=""):
    """
    Decorator para adicionar tratamento de erros a funções.

    Args:
        context: Contexto da operação

    Example:
        >>> @with_error_handling(context="calcular_resultado")
        ... def calcular_resultado(df):
        ...     return processar(df)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ctx = context or func.__name__
                handle_error(e, ctx)
                return None
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


def validate_input(value, field_name, validation_func, error_message=None):
    """
    Valida um input e lança ValidationError se inválido.

    Args:
        value: Valor a validar
        field_name: Nome do campo (para mensagem de erro)
        validation_func: Função que retorna True se válido
        error_message: Mensagem de erro customizada

    Raises:
        ValidationError: Se validação falhar

    Example:
        >>> validate_input(
        ...     nome,
        ...     "Nome",
        ...     lambda x: len(x) >= 3,
        ...     "Nome deve ter pelo menos 3 caracteres"
        ... )
    """
    if not validation_func(value):
        msg = error_message or f"Valor inválido para {field_name}"
        raise ValidationError(msg)


def require_authentication(telefone):
    """
    Verifica se usuário está autenticado.

    Args:
        telefone: Telefone do usuário

    Raises:
        AuthenticationError: Se não autenticado

    Example:
        >>> require_authentication(st.session_state.get("telefone_usuario"))
    """
    if not telefone:
        raise AuthenticationError("Usuário não autenticado")
