"""
Funções de formatação de dados para exibição.
"""
from datetime import datetime, date


def formatar_data(data):
    """
    Formata data para exibição (DD/MM/YYYY).
    
    Args:
        data: datetime.date, datetime.datetime ou string
        
    Returns:
        String formatada ou string vazia se inválida
    """
    if not data:
        return ""
    
    if isinstance(data, str):
        try:
            # Tentar parsear string
            if " " in data:
                data = datetime.strptime(data, "%d/%m/%Y %H:%M")
            else:
                data = datetime.strptime(data, "%d/%m/%Y")
        except (ValueError, TypeError):
            return str(data)
    
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y")
    elif isinstance(data, date):
        return data.strftime("%d/%m/%Y")
    
    return str(data)


def formatar_data_hora(data_hora):
    """
    Formata data e hora para exibição (DD/MM/YYYY HH:MM).
    
    Args:
        data_hora: datetime.datetime ou string
        
    Returns:
        String formatada ou string vazia se inválida
    """
    if not data_hora:
        return ""
    
    if isinstance(data_hora, str):
        try:
            data_hora = datetime.strptime(data_hora, "%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            return str(data_hora)
    
    if isinstance(data_hora, datetime):
        return data_hora.strftime("%d/%m/%Y %H:%M")
    
    return str(data_hora)

