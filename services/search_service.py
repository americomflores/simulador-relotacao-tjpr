"""
Serviço de busca e matching de nomes na lista classificatória.
"""
from fuzzywuzzy import fuzz
from lista_classificatoria import LISTA_CLASSIFICATORIA
from config.matricula_posicao_map import MATRICULA_POSICAO_MAP
from config.constants import FUZZY_MATCH_HIGH, FUZZY_MATCH_MEDIUM


# Cache de buscas recentes (LRU simples)
_search_cache = {}
_MAX_CACHE_SIZE = 100


def buscar_servidor_por_nome(nome_inscricao, threshold=FUZZY_MATCH_MEDIUM):
    """
    Busca posição na lista classificatória por nome usando fuzzy matching.

    Utiliza algoritmo de fuzzy matching (fuzzywuzzy) para encontrar o servidor
    na LISTA_CLASSIFICATORIA mesmo com pequenas variações de digitação.
    Testa tanto o nome_original quanto o nome_display para maximizar chances de match.
    Inclui cache para otimizar buscas repetidas.

    Args:
        nome_inscricao: Nome do servidor a buscar
        threshold: Score mínimo de similaridade (0-100). Padrão: FUZZY_MATCH_MEDIUM (85)

    Returns:
        Tupla (posicao, score, nome_display) ou None se não encontrar match acima do threshold

    Example:
        >>> buscar_servidor_por_nome("JOAO DA SILVA")
        (42, 95, "JOÃO DA SILVA")
        >>> buscar_servidor_por_nome("X", threshold=85)
        None  # Nome muito curto
    """
    if not nome_inscricao or len(nome_inscricao.strip()) < 3:
        return None

    # Verificar cache
    cache_key = f"{nome_inscricao.upper().strip()}:{threshold}"
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    melhor_match = None
    melhor_score = 0
    melhor_nome = ""

    nome_busca = nome_inscricao.upper().strip()

    for posicao, dados in LISTA_CLASSIFICATORIA.items():
        # Tenta match com nome original (sem numeração)
        score_original = fuzz.ratio(nome_busca, dados["nome_original"].upper())

        # Tenta match com nome display (com numeração se houver)
        score_display = fuzz.ratio(nome_busca, dados["nome_display"].upper())

        # Usa o melhor score
        score = max(score_original, score_display)

        if score > melhor_score:
            melhor_score = score
            melhor_match = posicao
            melhor_nome = dados["nome_display"]

    resultado = None
    if melhor_score >= threshold:
        resultado = (melhor_match, melhor_score, melhor_nome)

    # Cachear resultado (limpar cache se ficar muito grande)
    if len(_search_cache) >= _MAX_CACHE_SIZE:
        # Remove 20% dos itens mais antigos
        items_to_remove = list(_search_cache.keys())[:(_MAX_CACHE_SIZE // 5)]
        for key in items_to_remove:
            del _search_cache[key]

    _search_cache[cache_key] = resultado
    return resultado


def buscar_servidor_por_matricula(matricula):
    """
    Busca servidor por matrícula.

    Args:
        matricula: Matrícula do servidor

    Returns:
        Dict com dados do servidor ou None se não encontrado

    Example:
        >>> buscar_servidor_por_matricula("123456")
        {'posicao': 42, 'nome_original': 'JOAO DA SILVA', 'nome_display': 'JOÃO DA SILVA'}
    """
    if not matricula:
        return None

    matricula_str = str(matricula).strip()

    if matricula_str in MATRICULA_POSICAO_MAP:
        posicao = MATRICULA_POSICAO_MAP[matricula_str]
        if posicao in LISTA_CLASSIFICATORIA:
            return {
                "posicao": posicao,
                **LISTA_CLASSIFICATORIA[posicao]
            }

    return None


def buscar_servidor_por_posicao(posicao):
    """
    Busca servidor pela posição na lista classificatória.

    Args:
        posicao: Posição na lista (1-1268)

    Returns:
        Dict com dados do servidor ou None se não encontrado

    Example:
        >>> buscar_servidor_por_posicao(1)
        {'posicao': 1, 'nome_original': 'FULANO DE TAL', 'nome_display': 'FULANO DE TAL'}
    """
    if not posicao or not isinstance(posicao, int):
        return None

    if posicao in LISTA_CLASSIFICATORIA:
        return {
            "posicao": posicao,
            **LISTA_CLASSIFICATORIA[posicao]
        }

    return None


def buscar_multiplos_servidores(lista_nomes, threshold=FUZZY_MATCH_MEDIUM):
    """
    Busca múltiplos servidores de uma vez.

    Args:
        lista_nomes: Lista de nomes para buscar
        threshold: Score mínimo de similaridade

    Returns:
        Lista de tuplas (nome_buscado, resultado_busca)

    Example:
        >>> buscar_multiplos_servidores(["JOAO SILVA", "MARIA SANTOS"])
        [
            ("JOAO SILVA", (42, 95, "JOÃO DA SILVA")),
            ("MARIA SANTOS", (108, 92, "MARIA DOS SANTOS"))
        ]
    """
    resultados = []
    for nome in lista_nomes:
        resultado = buscar_servidor_por_nome(nome, threshold)
        resultados.append((nome, resultado))

    return resultados


def determinar_qualidade_match(score):
    """
    Determina qualidade do match baseado no score.

    Args:
        score: Score de fuzzy matching (0-100)

    Returns:
        str: "EXATA", "ALTA" ou "MÉDIA"

    Example:
        >>> determinar_qualidade_match(100)
        'EXATA'
        >>> determinar_qualidade_match(95)
        'ALTA'
        >>> determinar_qualidade_match(85)
        'MÉDIA'
    """
    if score == 100:
        return "EXATA"
    elif score >= FUZZY_MATCH_HIGH:
        return "ALTA"
    else:
        return "MÉDIA"


def limpar_cache_busca():
    """
    Limpa cache de buscas.

    Útil para liberar memória ou forçar novas buscas.
    """
    global _search_cache
    _search_cache = {}


def estatisticas_cache():
    """
    Retorna estatísticas do cache de buscas.

    Returns:
        Dict com estatísticas

    Example:
        >>> estatisticas_cache()
        {'tamanho': 45, 'capacidade': 100, 'utilizacao': '45%'}
    """
    tamanho = len(_search_cache)
    utilizacao = (tamanho / _MAX_CACHE_SIZE) * 100

    return {
        "tamanho": tamanho,
        "capacidade": _MAX_CACHE_SIZE,
        "utilizacao": f"{utilizacao:.1f}%"
    }
