"""
Exceções customizadas para o sistema.
"""


class SimuladorError(Exception):
    """Exceção base para erros do simulador."""
    pass


class AuthenticationError(SimuladorError):
    """Erro de autenticação."""
    pass


class ValidationError(SimuladorError):
    """Erro de validação de dados."""
    pass


class SheetsError(SimuladorError):
    """Erro ao acessar Google Sheets."""
    pass


class SimulationError(SimuladorError):
    """Erro durante cálculo de simulação."""
    pass


class ConfigurationError(SimuladorError):
    """Erro de configuração do sistema."""
    pass

