"""
Sistema de logging estruturado.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Criar diretório de logs se não existir
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configurar formato de log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configurar logger
logger = logging.getLogger("simulador_tjpr")
logger.setLevel(logging.INFO)

# Evitar duplicação de handlers
if not logger.handlers:
    # Handler para arquivo
    log_file = LOG_DIR / f"simulador_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    
    # Handler para console (apenas erros e warnings)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_operation(operation: str, user: str, details: str = ""):
    """
    Registra uma operação importante no sistema.
    
    Args:
        operation: Nome da operação (ex: "salvar_inscricao")
        user: Telefone do usuário que executou a operação
        details: Detalhes adicionais da operação
    """
    message = f"OPERATION: {operation} | USER: {user}"
    if details:
        message += f" | DETAILS: {details}"
    logger.info(message)


def log_error(error: Exception, context: str = ""):
    """
    Registra um erro com contexto.
    
    Args:
        error: Exceção ocorrida
        context: Contexto adicional do erro
    """
    message = f"ERROR: {type(error).__name__}: {str(error)}"
    if context:
        message += f" | CONTEXT: {context}"
    logger.error(message, exc_info=True)

