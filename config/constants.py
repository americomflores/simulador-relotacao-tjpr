"""
Constantes do sistema - valores fixos usados em múltiplos lugares.

Este arquivo centraliza magic numbers, strings e thresholds para facilitar
manutenção e garantir consistência em toda a aplicação.
"""

# =============================================================================
# THRESHOLDS DE FUZZY MATCHING
# =============================================================================

# Score para match de alta qualidade (95% ou mais de similaridade)
FUZZY_MATCH_HIGH = 95

# Score para match de qualidade média (85% ou mais de similaridade)
FUZZY_MATCH_MEDIUM = 85

# Score mínimo considerado aceitável para match
FUZZY_MATCH_LOW = 70


# =============================================================================
# LISTA CLASSIFICATÓRIA
# =============================================================================

# Tamanho da lista classificatória do Edital 04/2025
LISTA_SIZE = 1268

# Posição mínima válida na lista
LISTA_MIN_POSICAO = 1

# Posição máxima válida na lista
LISTA_MAX_POSICAO = 1268


# =============================================================================
# STATUS DE RESULTADOS
# =============================================================================

# Status possíveis para um servidor na simulação
STATUS_APROVADO = "APROVADO"
STATUS_DESCLASSIFICADO = "DESCLASSIFICADO"
STATUS_NAO_OBTEVE = "NÃO OBTEVE VAGA"


# =============================================================================
# RESULTADOS POSSÍVEIS
# =============================================================================

# Tipos de resultado que um servidor pode obter
RESULTADO_ANEXO_I = "ANEXO I"
RESULTADO_ANEXO_II = "ANEXO II"
RESULTADO_ANEXO_I_VIA_A2 = "ANEXO I (via A2)"
RESULTADO_SEM_VAGA = "Sem vaga"
RESULTADO_ESTAGIO = "Estágio Probatório"


# =============================================================================
# STATUS DE LOTAÇÃO
# =============================================================================

# Status possíveis para unidades judiciárias
STATUS_LOTACAO_SUPERAVITARIA = "SUPERAVITÁRIA"
STATUS_LOTACAO_EQUILIBRADA = "EQUILIBRADA"
STATUS_LOTACAO_DEFICITARIA = "DEFICITÁRIA"
STATUS_LOTACAO_NAO_IDENTIFICADA = "NÃO IDENTIFICADA"


# =============================================================================
# VALIDAÇÃO DE NOMES
# =============================================================================

# Comprimento mínimo para busca de nomes
NOME_MIN_LENGTH = 3


# =============================================================================
# DESIGNAÇÃO NA ORIGEM
# =============================================================================

# Valores possíveis para designação na origem
DESIGNACAO_SIM = "SIM"
DESIGNACAO_NAO = "NÃO"
DESIGNACAO_NAO_APLICAVEL = "-"


# =============================================================================
# OPÇÕES DE SELEÇÃO
# =============================================================================

# Texto padrão para opção vazia em selectbox
OPCAO_NAO_ESCOLHEU = "(Não escolheu)"
OPCAO_VAZIA = ""
