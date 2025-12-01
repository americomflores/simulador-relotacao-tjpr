"""
Testes de integração para Google Sheets (com mocks).
"""
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from services.sheets_service import (
    carregar_inscricoes,
    salvar_inscricao,
    excluir_inscricao,
    buscar_inscricao,
    verificar_cabecalhos_log
)
from exceptions import SheetsError


class TestCarregarInscricoes:
    """Testes para carregar inscrições."""
    
    def test_carregar_sheet_none(self):
        """Testa carregar quando sheet é None."""
        df = carregar_inscricoes(None)
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    def test_carregar_sheet_vazio(self, mock_sheet):
        """Testa carregar quando sheet está vazio."""
        mock_sheet.get_all_records.return_value = []
        df = carregar_inscricoes(mock_sheet)
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    def test_carregar_com_dados(self, mock_sheet):
        """Testa carregar com dados válidos."""
        mock_sheet.get_all_records.return_value = [
            {
                "nome": "João Silva",
                "matricula": "1234",
                "data_admissao": "01/01/2020",
                "lotacao_atual": "A2-001",
                "escolha_anexo1": "A1-001",
                "escolha_anexo2": "A2-010",
                "data_inscricao": "01/01/2025 10:00",
                "registrado_por": "(41) 99999-9999",
                "alterado_por": "",
                "data_alteracao": ""
            }
        ]
        
        df = carregar_inscricoes(mock_sheet)
        assert len(df) == 1
        assert df.iloc[0]["nome"] == "João Silva"
        assert df.iloc[0]["matricula"] == "1234"
    
    def test_carregar_com_erro(self, mock_sheet):
        """Testa tratamento de erro ao carregar."""
        mock_sheet.get_all_records.side_effect = Exception("Erro de conexão")
        
        with pytest.raises(SheetsError):
            carregar_inscricoes(mock_sheet)


class TestSalvarInscricao:
    """Testes para salvar inscrição."""
    
    def test_salvar_nova_inscricao(self, mock_sheet):
        """Testa salvar nova inscrição."""
        mock_sheet.get_all_records.return_value = []
        
        dados = {
            "nome": "João Silva",
            "matricula": "1234",
            "data_admissao": "01/01/2020",
            "lotacao_atual": "A2-001",
            "escolha_anexo1": "A1-001",
            "escolha_anexo2": "A2-010",
            "data_inscricao": "01/01/2025 10:00"
        }
        
        resultado = salvar_inscricao(mock_sheet, dados, "41997813606")
        assert resultado is True
        mock_sheet.append_row.assert_called_once()
    
    def test_atualizar_inscricao_existente(self, mock_sheet):
        """Testa atualizar inscrição existente."""
        mock_sheet.get_all_records.return_value = [
            {
                "nome": "João Silva",
                "matricula": "1234",
                "data_admissao": "01/01/2020",
                "lotacao_atual": "A2-001",
                "escolha_anexo1": "A1-001",
                "escolha_anexo2": "A2-010",
                "data_inscricao": "01/01/2025 10:00",
                "registrado_por": "(41) 99999-9999",
                "alterado_por": "",
                "data_alteracao": ""
            }
        ]
        
        dados = {
            "nome": "João Silva Atualizado",
            "matricula": "1234",
            "data_admissao": "01/01/2020",
            "lotacao_atual": "A2-002",
            "escolha_anexo1": "A1-002",
            "escolha_anexo2": "A2-020",
            "data_inscricao": "01/01/2025 11:00"
        }
        
        resultado = salvar_inscricao(mock_sheet, dados, "41997813606")
        assert resultado is True
        mock_sheet.update.assert_called_once()
    
    def test_salvar_sheet_none(self):
        """Testa salvar quando sheet é None."""
        dados = {
            "nome": "João Silva",
            "matricula": "1234",
            "data_admissao": "01/01/2020",
            "lotacao_atual": "A2-001",
            "escolha_anexo1": "",
            "escolha_anexo2": "",
            "data_inscricao": "01/01/2025 10:00"
        }
        
        with pytest.raises(SheetsError):
            salvar_inscricao(None, dados, "41997813606")
    
    def test_salvar_com_erro(self, mock_sheet):
        """Testa tratamento de erro ao salvar."""
        mock_sheet.get_all_records.return_value = []
        mock_sheet.append_row.side_effect = Exception("Erro ao salvar")
        
        dados = {
            "nome": "João Silva",
            "matricula": "1234",
            "data_admissao": "01/01/2020",
            "lotacao_atual": "A2-001",
            "escolha_anexo1": "",
            "escolha_anexo2": "",
            "data_inscricao": "01/01/2025 10:00"
        }
        
        with pytest.raises(SheetsError):
            salvar_inscricao(mock_sheet, dados, "41997813606")


class TestExcluirInscricao:
    """Testes para excluir inscrição."""
    
    def test_excluir_inscricao_existente(self, mock_sheet):
        """Testa excluir inscrição existente."""
        mock_sheet.get_all_records.return_value = [
            {
                "nome": "João Silva",
                "matricula": "1234",
                "data_admissao": "01/01/2020",
                "lotacao_atual": "A2-001",
                "escolha_anexo1": "A1-001",
                "escolha_anexo2": "A2-010",
                "data_inscricao": "01/01/2025 10:00"
            }
        ]
        
        sucesso, nome = excluir_inscricao(mock_sheet, "1234", "41997813606")
        assert sucesso is True
        assert nome == "João Silva"
        mock_sheet.delete_rows.assert_called_once()
    
    def test_excluir_inscricao_inexistente(self, mock_sheet):
        """Testa excluir inscrição inexistente."""
        mock_sheet.get_all_records.return_value = []
        
        sucesso, nome = excluir_inscricao(mock_sheet, "9999", "41997813606")
        assert sucesso is False
        assert nome is None
    
    def test_excluir_sheet_none(self):
        """Testa excluir quando sheet é None."""
        with pytest.raises(SheetsError):
            excluir_inscricao(None, "1234", "41997813606")


class TestBuscarInscricao:
    """Testes para buscar inscrição."""
    
    def test_buscar_inscricao_existente(self, mock_sheet):
        """Testa buscar inscrição existente."""
        mock_sheet.get_all_records.return_value = [
            {
                "nome": "João Silva",
                "matricula": "1234",
                "data_admissao": "01/01/2020",
                "lotacao_atual": "A2-001"
            }
        ]
        
        resultado = buscar_inscricao(mock_sheet, "1234")
        assert resultado is not None
        assert resultado["nome"] == "João Silva"
    
    def test_buscar_inscricao_inexistente(self, mock_sheet):
        """Testa buscar inscrição inexistente."""
        mock_sheet.get_all_records.return_value = []
        
        resultado = buscar_inscricao(mock_sheet, "9999")
        assert resultado is None
    
    def test_buscar_sheet_none(self):
        """Testa buscar quando sheet é None."""
        resultado = buscar_inscricao(None, "1234")
        assert resultado is None


class TestVerificarCabecalhosLog:
    """Testes para verificação de cabeçalhos de log."""
    
    def test_cabecalhos_ja_existem(self, mock_sheet):
        """Testa quando cabeçalhos já existem."""
        mock_sheet.row_values.return_value = [
            "nome", "matricula", "data_admissao", "lotacao_atual",
            "escolha_anexo1", "escolha_anexo2", "data_inscricao",
            "registrado_por", "alterado_por", "data_alteracao"
        ]
        
        # Não deve lançar exceção
        verificar_cabecalhos_log(mock_sheet)
    
    def test_cabecalhos_faltando(self, mock_sheet):
        """Testa quando cabeçalhos estão faltando."""
        mock_sheet.row_values.return_value = [
            "nome", "matricula", "data_admissao", "lotacao_atual",
            "escolha_anexo1", "escolha_anexo2", "data_inscricao"
        ]
        
        # Deve adicionar cabeçalhos faltantes
        verificar_cabecalhos_log(mock_sheet)
        mock_sheet.update.assert_called()
    
    def test_planilha_vazia(self, mock_sheet):
        """Testa quando planilha está vazia."""
        mock_sheet.row_values.return_value = []
        
        verificar_cabecalhos_log(mock_sheet)
        mock_sheet.update.assert_called()

