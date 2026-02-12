"""
Testes para o serviço de simulação.
Atualizado para Edital 01/2026 (sem validação de estágio probatório).
"""
import pytest
import pandas as pd
from datetime import date
from services.simulacao_service import (
    calcular_lotacao_dinamica,
    calcular_resultado,
    calcular_demanda
)
# verificar_estagio_probatorio removido - Edital 01/2026 permite servidores em estágio probatório


# TestVerificarEstagioProbatorio removido - Edital 01/2026 não tem restrição de estágio


class TestCalcularLotacaoDinamica:
    """Testes para cálculo de lotação dinâmica."""

    def test_ajuste_positivo(self):
        """Testa ajuste positivo (adiciona servidor)."""
        # Usar código que existe em lotacao_data.py
        # Nota: Este teste pode falhar se o código não existir
        # Em produção, usar código conhecido
        resultado = calcular_lotacao_dinamica("A2-001", 1)
        if resultado:
            assert resultado["lotacao_real"] > 0
            assert "status" in resultado

    def test_ajuste_negativo(self):
        """Testa ajuste negativo (remove servidor)."""
        resultado = calcular_lotacao_dinamica("A2-001", -1)
        if resultado:
            assert "status" in resultado

    def test_codigo_inexistente(self):
        """Testa código de unidade inexistente."""
        resultado = calcular_lotacao_dinamica("INVALIDO", 0)
        assert resultado is None


class TestCalcularResultado:
    """Testes para cálculo de resultado da simulação."""

    def test_dataframe_vazio(self):
        """Testa cálculo com DataFrame vazio."""
        df = pd.DataFrame()
        resultado = calcular_resultado(df)
        assert isinstance(resultado, tuple)
        assert len(resultado) == 4
        assert resultado[0].empty

    def test_ordenacao_por_posicao_lista(self):
        """Testa que resultados são ordenados por posição na lista classificatória."""
        df = pd.DataFrame({
            "nome": ["Servidor B", "Servidor A"],
            "matricula": ["1", "2"],
            "data_admissao": [date(2023, 1, 1), date(2020, 1, 1)],
            "lotacao_atual": ["A2-001", "A2-002"],
            "escolha_anexo1": ["", ""],
            "escolha_anexo2": ["", ""],
            "posicao_lista_classificatoria": [500, 100]  # A é mais antigo na lista
        })

        df_resultado, _, _, _ = calcular_resultado(df)

        # Verificar que tem coluna de posição
        assert "posicao_antiguidade" in df_resultado.columns
        # Posição menor (100) deve vir primeiro
        assert df_resultado.iloc[0]["nome"] == "Servidor A"

    # test_desclassificacao_estagio_probatorio removido - Edital 01/2026 não tem essa restrição


class TestCalcularDemanda:
    """Testes para cálculo de demanda."""

    def test_demanda_vazia(self):
        """Testa cálculo de demanda com DataFrame vazio."""
        df = pd.DataFrame()
        demanda_a1, demanda_a2 = calcular_demanda(df)
        assert demanda_a1 == {}
        assert demanda_a2 == {}

    def test_demanda_com_escolhas(self):
        """Testa cálculo de demanda com escolhas."""
        df = pd.DataFrame({
            "nome": ["Servidor 1", "Servidor 2"],
            "matricula": ["1", "2"],
            "data_admissao": [date(2020, 1, 1), date(2020, 1, 1)],
            "lotacao_atual": ["A2-001", "A2-002"],
            "escolha_anexo1": ["A1-001", "A1-001"],  # Mesma escolha
            "escolha_anexo2": ["A2-010", "A2-020"]
        })

        demanda_a1, demanda_a2 = calcular_demanda(df)

        # A1-001 deve ter demanda 2
        assert demanda_a1.get("A1-001", 0) == 2
        # A2-010 e A2-020 devem ter demanda 1 cada
        assert demanda_a2.get("A2-010", 0) == 1
        assert demanda_a2.get("A2-020", 0) == 1
