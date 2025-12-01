"""
Testes para validadores.
"""
import pytest
from datetime import date
from utils.validators import (
    validar_telefone,
    validar_matricula,
    validar_data_admissao,
    validar_codigo_unidade,
    validar_inscricao
)


class TestValidarTelefone:
    """Testes para validação de telefone."""
    
    def test_telefone_valido_11_digitos(self):
        """Testa telefone válido com 11 dígitos."""
        assert validar_telefone("41997813606") is True
    
    def test_telefone_valido_10_digitos(self):
        """Testa telefone válido com 10 dígitos."""
        assert validar_telefone("4197813606") is True
    
    def test_telefone_com_formatacao(self):
        """Testa telefone com formatação."""
        assert validar_telefone("(41) 99781-3606") is True
    
    def test_telefone_invalido_curto(self):
        """Testa telefone muito curto."""
        assert validar_telefone("123") is False
    
    def test_telefone_vazio(self):
        """Testa telefone vazio."""
        assert validar_telefone("") is False


class TestValidarMatricula:
    """Testes para validação de matrícula."""
    
    def test_matricula_valida(self):
        """Testa matrícula válida."""
        assert validar_matricula("1234") is True
        assert validar_matricula("12345") is True
    
    def test_matricula_invalida_curta(self):
        """Testa matrícula muito curta."""
        assert validar_matricula("123") is False
    
    def test_matricula_invalida_nao_numerica(self):
        """Testa matrícula não numérica."""
        assert validar_matricula("ABC") is False
    
    def test_matricula_vazia(self):
        """Testa matrícula vazia."""
        assert validar_matricula("") is False


class TestValidarDataAdmissao:
    """Testes para validação de data de admissão."""
    
    def test_data_valida(self):
        """Testa data válida."""
        is_valid, error = validar_data_admissao(date(2020, 1, 1))
        assert is_valid is True
        assert error == ""
    
    def test_data_string_valida(self):
        """Testa data em formato string válida."""
        is_valid, error = validar_data_admissao("01/01/2020")
        assert is_valid is True
    
    def test_data_futuro(self):
        """Testa data no futuro (inválida)."""
        data_futura = date.today().replace(year=date.today().year + 1)
        is_valid, error = validar_data_admissao(data_futura)
        assert is_valid is False
        assert "futuro" in error.lower()
    
    def test_data_muito_antiga(self):
        """Testa data muito antiga (inválida)."""
        is_valid, error = validar_data_admissao(date(1940, 1, 1))
        assert is_valid is False
        assert "1950" in error
    
    def test_data_vazia(self):
        """Testa data vazia."""
        is_valid, error = validar_data_admissao(None)
        assert is_valid is False
        assert "obrigatória" in error.lower()


class TestValidarCodigoUnidade:
    """Testes para validação de código de unidade."""
    
    def test_codigo_anexo1_valido(self):
        """Testa código válido do Anexo I."""
        # Assumindo que A1-001 existe em ANEXO_I
        is_valid, error = validar_codigo_unidade("A1-001", "I")
        assert is_valid is True
    
    def test_codigo_anexo2_valido(self):
        """Testa código válido do Anexo II."""
        # Assumindo que A2-001 existe em ANEXO_II
        is_valid, error = validar_codigo_unidade("A2-001", "II")
        assert is_valid is True
    
    def test_codigo_invalido(self):
        """Testa código inválido."""
        is_valid, error = validar_codigo_unidade("INVALIDO", "I")
        assert is_valid is False
        assert "não encontrado" in error.lower()
    
    def test_codigo_vazio(self):
        """Testa código vazio (válido, pois é opcional)."""
        is_valid, error = validar_codigo_unidade("", None)
        assert is_valid is True


class TestValidarInscricao:
    """Testes para validação completa de inscrição."""
    
    def test_inscricao_valida(self):
        """Testa inscrição válida."""
        is_valid, errors = validar_inscricao(
            nome="João Silva",
            matricula="1234",
            data_admissao=date(2020, 1, 1),
            lotacao_atual="A2-001",
            escolha_anexo1="A1-001",
            escolha_anexo2="A2-010"
        )
        assert is_valid is True
        assert len(errors) == 0
    
    def test_inscricao_nome_vazio(self):
        """Testa inscrição com nome vazio."""
        is_valid, errors = validar_inscricao(
            nome="",
            matricula="1234",
            data_admissao=date(2020, 1, 1),
            lotacao_atual="A2-001"
        )
        assert is_valid is False
        assert any("nome" in e.lower() for e in errors)
    
    def test_inscricao_origem_destino_iguais(self):
        """Testa inscrição com origem e destino iguais."""
        is_valid, errors = validar_inscricao(
            nome="João Silva",
            matricula="1234",
            data_admissao=date(2020, 1, 1),
            lotacao_atual="A2-001",
            escolha_anexo2="A2-001"  # Mesmo código
        )
        assert is_valid is False
        assert any("iguais" in e.lower() for e in errors)

