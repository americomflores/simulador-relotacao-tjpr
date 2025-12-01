"""
Configurações e constantes do sistema.
"""
from datetime import date

# Data limite para estágio probatório (3 anos antes de 26/11/2025)
DATA_LIMITE_ESTAGIO = date(2022, 11, 26)

# Configurações de cookies e sessão
COOKIE_EXPIRATION_DAYS = 30  # Dias para expiração do cookie "manter logado"
COOKIE_SECRET_KEY = "tjpr-simulador-2025-secret-key-change-in-production"  # Chave secreta para tokens (alterar em produção)

