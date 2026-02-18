"""
Configuração e fixtures para testes.
"""
import pytest
import pandas as pd
from datetime import date
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_inscricoes():
    """Fixture com dados de exemplo de inscrições."""
    return pd.DataFrame({
        "nome": ["João Silva", "Maria Santos", "Pedro Costa"],
        "matricula": ["1234", "5678", "9012"],
        "data_admissao": [
            date(2020, 1, 15),
            date(2021, 3, 20),
            date(2022, 12, 1)  # Edital 01/2026: estágio probatório não é mais restrição
        ],
        "lotacao_atual": ["A2-001", "A2-002", "A2-003"],
        "escolha_anexo1": ["A1-001", "A1-002", ""],
        "escolha_anexo2": ["A2-010", "A2-020", "A2-030"],
        "data_inscricao": ["01/01/2025 10:00", "01/01/2025 11:00", "01/01/2025 12:00"],
        "registrado_por": ["(41) 99999-9999", "(41) 99999-9999", "(41) 99999-9999"],
        "alterado_por": ["", "", ""],
        "data_alteracao": ["", "", ""],
        "posicao_lista_classificatoria": [1, 2, 3]
    })


@pytest.fixture
def mock_sheet():
    """Fixture com mock do Google Sheets."""
    sheet = Mock()
    sheet.get_all_records.return_value = []
    sheet.row_values.return_value = []
    sheet.update.return_value = None
    sheet.append_row.return_value = None
    sheet.delete_rows.return_value = None
    return sheet


@pytest.fixture
def mock_streamlit_secrets():
    """Fixture para mockar st.secrets."""
    return {
        "spreadsheet_name": "Test Spreadsheet",
        "gcp_service_account": {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test"
        }
    }

