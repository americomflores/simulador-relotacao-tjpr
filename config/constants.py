"""
Constantes do sistema - valores fixos usados em múltiplos lugares.
"""

# =============================================================================
# THRESHOLDS DE FUZZY MATCHING
# =============================================================================

# Score para match de alta qualidade (95% ou mais de similaridade)
FUZZY_MATCH_HIGH = 95

# Score para match de qualidade média (85% ou mais de similaridade)
FUZZY_MATCH_MEDIUM = 85


# =============================================================================
# OPÇÕES DE SELEÇÃO
# =============================================================================

# Texto padrão para opção vazia em selectbox
OPCAO_NAO_ESCOLHEU = "(Não escolheu)"


# =============================================================================
# DATAS DO EDITAL 01/2026
# =============================================================================

from datetime import date

# Data de publicação do Edital 01/2026 (base para cálculo dos 2 anos do item 3.3)
DATA_PUBLICACAO_EDITAL = date(2026, 2, 10)
# Limite para relotação voluntária: 2 anos antes da publicação
DATA_LIMITE_RELOTACAO = date(2024, 2, 10)
