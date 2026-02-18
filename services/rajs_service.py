"""
Serviço de operações com Regiões Administrativas Judiciárias (RAJs).
"""
from config.rajs_config import RAJS, get_raj_nome_curto


# Lookup pré-normalizado: comarca.strip().lower() -> raj_nome
_COMARCA_RAJ_LOOKUP = {}
for _raj_nome, _raj_info in RAJS.items():
    for _c in _raj_info["comarcas"]:
        _COMARCA_RAJ_LOOKUP[_c.strip().lower()] = _raj_nome


def obter_raj_da_comarca(comarca, normalizar_func=None):
    """
    Identifica a RAJ de uma comarca.

    Args:
        comarca: Nome da comarca
        normalizar_func: Função opcional para normalizar nomes (ex: normalizar_comarca)

    Returns:
        Nome completo da RAJ ou "Não identificada" se não encontrada
    """
    if not comarca:
        return "Não identificada"

    if normalizar_func:
        comarca_busca = normalizar_func(comarca).lower()
    else:
        comarca_busca = comarca.strip().lower()

    # Lookup rápido (sem normalizar_func)
    if not normalizar_func:
        return _COMARCA_RAJ_LOOKUP.get(comarca_busca, "Não identificada")

    # Fallback: busca linear quando há função de normalização customizada
    for raj_nome, raj_info in RAJS.items():
        for c in raj_info["comarcas"]:
            c_normalizada = normalizar_func(c).lower()
            if comarca_busca == c_normalizada:
                return raj_nome

    return "Não identificada"
