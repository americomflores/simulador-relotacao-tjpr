"""
Serviço de busca e matching de nomes na lista classificatória.
"""
from fuzzywuzzy import fuzz
from lista_classificatoria import LISTA_CLASSIFICATORIA
from config.matricula_posicao_map import MATRICULA_POSICAO_MAP
from config.constants import FUZZY_MATCH_MEDIUM


# Cache de buscas recentes (LRU simples)
_search_cache = {}
_MAX_CACHE_SIZE = 100


def buscar_servidor_por_nome(nome_inscricao, threshold=FUZZY_MATCH_MEDIUM):
    """
    Busca posição na lista classificatória por nome usando fuzzy matching.

    Args:
        nome_inscricao: Nome do servidor a buscar
        threshold: Score mínimo de similaridade (0-100). Padrão: FUZZY_MATCH_MEDIUM (85)

    Returns:
        Tupla (posicao, score, nome_display) ou None se não encontrar match acima do threshold
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
