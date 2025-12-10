"""
Serviço de operações com Regiões Administrativas Judiciárias (RAJs).
"""
from config.rajs_config import RAJS, get_raj_nome_curto, get_raj_numero


def obter_raj_da_comarca(comarca, normalizar_func=None):
    """
    Identifica a RAJ de uma comarca.

    Args:
        comarca: Nome da comarca
        normalizar_func: Função opcional para normalizar nomes (ex: normalizar_comarca)

    Returns:
        Nome completo da RAJ ou "Não identificada" se não encontrada

    Example:
        >>> obter_raj_da_comarca("Curitiba")
        'RAJ 1 - Região Metropolitana de Curitiba e Litoral'
        >>> obter_raj_da_comarca("Foz do Iguaçu")
        'RAJ 5 - Foz do Iguaçu'
    """
    if not comarca:
        return "Não identificada"

    # Se foi passada uma função de normalização, usar ela
    if normalizar_func:
        comarca_busca = normalizar_func(comarca).lower()
    else:
        comarca_busca = comarca.strip().lower()

    for raj_nome, raj_info in RAJS.items():
        for c in raj_info["comarcas"]:
            # Normalizar comarca da lista também
            if normalizar_func:
                c_normalizada = normalizar_func(c).lower()
            else:
                c_normalizada = c.strip().lower()

            if comarca_busca == c_normalizada:
                return raj_nome

    return "Não identificada"


def obter_numero_raj(comarca, normalizar_func=None):
    """
    Retorna o número da RAJ de uma comarca.

    Args:
        comarca: Nome da comarca
        normalizar_func: Função opcional para normalizar nomes

    Returns:
        Número da RAJ (1-10) ou None

    Example:
        >>> obter_numero_raj("Curitiba")
        1
        >>> obter_numero_raj("Londrina")
        9
    """
    raj_nome = obter_raj_da_comarca(comarca, normalizar_func)
    if raj_nome and raj_nome != "Não identificada":
        return RAJS[raj_nome]["numero"]
    return None


def obter_comarcas_da_raj(raj_numero=None, raj_nome=None):
    """
    Retorna lista de comarcas de uma RAJ.

    Args:
        raj_numero: Número da RAJ (1-10)
        raj_nome: Nome completo da RAJ

    Returns:
        Lista de comarcas ou lista vazia se RAJ não encontrada

    Example:
        >>> obter_comarcas_da_raj(raj_numero=1)
        ['Curitiba', 'Almirante Tamandaré', ...]
        >>> obter_comarcas_da_raj(raj_nome="RAJ 5 - Foz do Iguaçu")
        ['Foz do Iguaçu', 'Matelândia', ...]
    """
    # Buscar por nome
    if raj_nome and raj_nome in RAJS:
        return RAJS[raj_nome]["comarcas"]

    # Buscar por número
    if raj_numero:
        for raj_nome, raj_info in RAJS.items():
            if raj_info["numero"] == raj_numero:
                return raj_info["comarcas"]

    return []


def obter_sede_da_raj(raj_numero=None, raj_nome=None):
    """
    Retorna a cidade-sede de uma RAJ.

    Args:
        raj_numero: Número da RAJ (1-10)
        raj_nome: Nome completo da RAJ

    Returns:
        Nome da cidade-sede ou None

    Example:
        >>> obter_sede_da_raj(raj_numero=1)
        'Curitiba'
        >>> obter_sede_da_raj(raj_numero=5)
        'Foz do Iguaçu'
    """
    # Buscar por nome
    if raj_nome and raj_nome in RAJS:
        return RAJS[raj_nome]["sede"]

    # Buscar por número
    if raj_numero:
        for raj_nome, raj_info in RAJS.items():
            if raj_info["numero"] == raj_numero:
                return raj_info["sede"]

    return None


def listar_todas_rajs():
    """
    Retorna lista de todas as RAJs.

    Returns:
        Lista de dicts com informações de cada RAJ

    Example:
        >>> rajs = listar_todas_rajs()
        >>> print(rajs[0])
        {'numero': 1, 'nome': 'RAJ 1 - ...', 'sede': 'Curitiba', 'qtd_comarcas': 20}
    """
    resultado = []
    for raj_nome, raj_info in RAJS.items():
        resultado.append({
            "numero": raj_info["numero"],
            "nome": raj_nome,
            "nome_curto": get_raj_nome_curto(raj_nome),
            "sede": raj_info["sede"],
            "qtd_comarcas": len(raj_info["comarcas"]),
            "comarcas": raj_info["comarcas"]
        })

    # Ordenar por número
    resultado.sort(key=lambda x: x["numero"])
    return resultado


def contar_servidores_por_raj(df_resultado):
    """
    Conta quantos servidores aprovados foram para cada RAJ.

    Args:
        df_resultado: DataFrame com resultado da simulação

    Returns:
        Dict com contagem por RAJ

    Example:
        >>> contagem = contar_servidores_por_raj(df_resultado)
        >>> print(contagem['RAJ 1 - Região Metropolitana de Curitiba e Litoral'])
        45
    """
    from utils.ui_helpers import extrair_comarca_da_string

    contagem = {raj_nome: 0 for raj_nome in RAJS.keys()}

    for _, row in df_resultado.iterrows():
        if row.get('status') == 'APROVADO' and row.get('vaga_obtida'):
            comarca = extrair_comarca_da_string(row['vaga_obtida'])
            if comarca:
                raj = obter_raj_da_comarca(comarca)
                if raj in contagem:
                    contagem[raj] += 1

    return contagem
