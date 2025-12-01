"""
Testes para o serviço de autenticação.
"""
import pytest
from services.auth_service import (
    formatar_telefone_display,
    limpar_telefone,
    verificar_login,
    verificar_admin,
    is_admin
)
from config.auth_config import AUTH_CODES, ADMIN_TELEFONES, ADMIN_SENHA


class TestFormatarTelefone:
    """Testes para formatação de telefone."""
    
    def test_formatar_telefone_completo(self):
        """Testa formatação de telefone completo."""
        telefone = "41997813606"
        resultado = formatar_telefone_display(telefone)
        assert resultado == "(41) 99781-3606"
    
    def test_formatar_telefone_com_formatacao(self):
        """Testa formatação de telefone já formatado."""
        telefone = "(41) 99781-3606"
        resultado = formatar_telefone_display(telefone)
        assert resultado == "(41) 99781-3606"
    
    def test_formatar_telefone_vazio(self):
        """Testa formatação de telefone vazio."""
        resultado = formatar_telefone_display("")
        assert resultado == ""
    
    def test_limpar_telefone(self):
        """Testa limpeza de telefone."""
        telefone = "(41) 99781-3606"
        resultado = limpar_telefone(telefone)
        assert resultado == "41997813606"


class TestVerificarLogin:
    """Testes para verificação de login."""
    
    def test_login_valido(self):
        """Testa login com credenciais válidas."""
        # Usar primeiro telefone do AUTH_CODES
        telefone = list(AUTH_CODES.keys())[0]
        codigo = AUTH_CODES[telefone]
        assert verificar_login(telefone, codigo) is True
    
    def test_login_codigo_invalido(self):
        """Testa login com código inválido."""
        telefone = list(AUTH_CODES.keys())[0]
        codigo = "INVALIDO"
        assert verificar_login(telefone, codigo) is False
    
    def test_login_telefone_invalido(self):
        """Testa login com telefone não cadastrado."""
        telefone = "00000000000"
        codigo = "TJPR-TEST"
        assert verificar_login(telefone, codigo) is False
    
    def test_login_case_insensitive(self):
        """Testa que código é case-insensitive."""
        telefone = list(AUTH_CODES.keys())[0]
        codigo = AUTH_CODES[telefone].lower()
        assert verificar_login(telefone, codigo) is True


class TestVerificarAdmin:
    """Testes para verificação de admin."""
    
    def test_admin_valido(self):
        """Testa login de admin válido."""
        telefone = ADMIN_TELEFONES[0]
        senha = ADMIN_SENHA
        assert verificar_admin(telefone, senha) is True
    
    def test_admin_senha_invalida(self):
        """Testa login de admin com senha inválida."""
        telefone = ADMIN_TELEFONES[0]
        senha = "senha_errada"
        assert verificar_admin(telefone, senha) is False
    
    def test_admin_telefone_invalido(self):
        """Testa login de admin com telefone inválido."""
        telefone = "00000000000"
        senha = ADMIN_SENHA
        assert verificar_admin(telefone, senha) is False

