"""
Serviço de busca e matching de nomes na lista classificatória.
"""
from functools import lru_cache
from fuzzywuzzy import fuzz
from lista_classificatoria import LISTA_CLASSIFICATORIA
from config.matricula_posicao_map import MATRICULA_POSICAO_MAP
from config.constants import FUZZY_MATCH_MEDIUM


@lru_cache(maxsize=128)
def _buscar_nome_cached(nome_upper, threshold):
    """Busca cacheada por nome (LRU real)."""
    melhor_match = None
    melhor_score = 0
    melhor_nome = ""

    for posicao, dados in LISTA_CLASSIFICATORIA.items():
        score_original = fuzz.ratio(nome_upper, dados["nome_original"].upper())
        score_display = fuzz.ratio(nome_upper, dados["nome_display"].upper())
        score = max(score_original, score_display)

        if score > melhor_score:
            melhor_score = score
            melhor_match = posicao
            melhor_nome = dados["nome_display"]

    if melhor_score >= threshold:
        return (melhor_match, melhor_score, melhor_nome)
    return None


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

    return _buscar_nome_cached(nome_inscricao.upper().strip(), threshold)


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
