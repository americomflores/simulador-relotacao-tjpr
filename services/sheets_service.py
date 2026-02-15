"""
Serviço para operações com Google Sheets.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from exceptions import SheetsError, ConfigurationError
from utils.logger import log_operation, log_error
from services.auth_service import formatar_telefone_display


@st.cache_resource
def conectar_sheets():
    """
    Conecta ao Google Sheets usando credenciais do secrets.
    
    Returns:
        Sheet object ou None em caso de erro
    """
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        if "gcp_service_account" not in st.secrets:
            raise ConfigurationError("Credenciais do Google Cloud não encontradas em secrets.toml")
        
        if "spreadsheet_name" not in st.secrets:
            raise ConfigurationError("Nome da planilha não encontrado em secrets.toml")
        
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open(st.secrets["spreadsheet_name"])
        sheet = spreadsheet.sheet1
        
        # Verificar e adicionar cabeçalhos de log se necessário
        verificar_cabecalhos_log(sheet)
        
        return sheet
    except ConfigurationError:
        raise
    except Exception as e:
        log_error(e, "conectar_sheets")
        raise SheetsError(f"Erro ao conectar com Google Sheets: {e}")


def verificar_cabecalhos_log(sheet):
    """
    Verifica se os cabeçalhos de log existem e adiciona se necessário.
    
    Args:
        sheet: Sheet object do gspread
    """
    try:
        # Pegar primeira linha (cabeçalhos)
        cabecalhos = sheet.row_values(1)
        
        # Cabeçalhos esperados
        cabecalhos_necessarios = ["nome", "matricula", "data_admissao", "lotacao_atual",
                                   "escolha_anexo1", "escolha_anexo2", "data_inscricao",
                                   "registrado_por", "alterado_por", "data_alteracao",
                                   "posicao_lista_classificatoria"]

        # Se planilha vazia, criar todos os cabeçalhos
        if not cabecalhos:
            sheet.update('A1:K1', [cabecalhos_necessarios])
            return
        
        # Verificar se cabeçalhos de log existem (colunas H, I, J)
        cabecalhos_log = ["registrado_por", "alterado_por", "data_alteracao"]
        
        for i, cab in enumerate(cabecalhos_log):
            col_idx = 7 + i  # H=7, I=8, J=9 (0-indexed)
            if len(cabecalhos) <= col_idx or cabecalhos[col_idx] != cab:
                # Adicionar cabeçalho na posição correta
                col_letra = chr(ord('H') + i)  # H, I, J
                sheet.update(f'{col_letra}1', [[cab]])
    except Exception as e:
        # Não falhar silenciosamente, mas também não travar o app
        log_error(e, "verificar_cabecalhos_log")


def carregar_inscricoes(sheet):
    """
    Carrega todas as inscrições do Google Sheets.
    
    Args:
        sheet: Sheet object do gspread ou None
        
    Returns:
        DataFrame com as inscrições
    """
    colunas_base = ["nome", "matricula", "data_admissao", "lotacao_atual",
                    "escolha_anexo1", "escolha_anexo2", "data_inscricao"]
    colunas_log = ["registrado_por", "alterado_por", "data_alteracao"]
    colunas_classificacao = ["posicao_lista_classificatoria"]
    todas_colunas = colunas_base + colunas_log + colunas_classificacao
    
    if sheet is None:
        return pd.DataFrame(columns=todas_colunas)
    
    try:
        dados = sheet.get_all_records()
        if not dados:
            return pd.DataFrame(columns=todas_colunas)
        
        df = pd.DataFrame(dados)
        df["data_admissao"] = pd.to_datetime(df["data_admissao"], format="%d/%m/%Y", errors="coerce").dt.date

        # Garantir que colunas de log existam (para compatibilidade com dados antigos)
        for col in colunas_log:
            if col not in df.columns:
                df[col] = ""

        # Garantir que coluna de posição existe e converter para int
        if "posicao_lista_classificatoria" not in df.columns:
            df["posicao_lista_classificatoria"] = pd.NA
        else:
            # Substituir strings vazias por NA antes da conversão
            df["posicao_lista_classificatoria"] = df["posicao_lista_classificatoria"].replace("", pd.NA)
            df["posicao_lista_classificatoria"] = df["posicao_lista_classificatoria"].replace(" ", pd.NA)

        # Converter para numérico e depois para Int64 (nullable integer)
        df["posicao_lista_classificatoria"] = pd.to_numeric(
            df["posicao_lista_classificatoria"],
            errors="coerce"
        ).astype("Int64")
        
        log_operation("carregar_inscricoes", "system", f"{len(df)} registros")
        return df
    except Exception as e:
        log_error(e, "carregar_inscricoes")
        raise SheetsError(f"Erro ao carregar dados: {e}")


def salvar_inscricao(sheet, dados, telefone_usuario="Público"):
    """
    Salva ou atualiza uma inscrição, registrando quem fez a operação.
    
    Args:
        sheet: Sheet object do gspread
        dados: Dicionário com dados da inscrição
        telefone_usuario: Telefone do usuário que está salvando
        
    Returns:
        True se sucesso, False caso contrário
    """
    if sheet is None:
        raise SheetsError("Conexão com Google Sheets não disponível")
    
    try:
        registros = sheet.get_all_records()
        linha_existente = None
        registro_antigo = None
        
        for i, reg in enumerate(registros, start=2):
            if str(reg.get("matricula", "")) == str(dados["matricula"]):
                linha_existente = i
                registro_antigo = reg
                break
        
        # Formatar telefone do usuário para o log
        telefone_formatado = formatar_telefone_display(telefone_usuario) if telefone_usuario else "Desconhecido"
        data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        if linha_existente and registro_antigo:
            # Atualização - manter registrado_por original, atualizar alterado_por
            registrado_por = registro_antigo.get("registrado_por", telefone_formatado) or telefone_formatado
            valores = [
                dados["nome"],
                dados["matricula"],
                dados["data_admissao"],
                dados["lotacao_atual"],
                dados["escolha_anexo1"],
                dados["escolha_anexo2"],
                dados["data_inscricao"],
                registrado_por,                              # H: manter original
                telefone_formatado,                          # I: quem alterou
                data_hora_atual,                             # J: quando alterou
                dados.get("posicao_lista_classificatoria", "")  # K: posição
            ]
            sheet.update(f"A{linha_existente}:K{linha_existente}", [valores])
            log_operation("atualizar_inscricao", telefone_usuario, f"matrícula {dados['matricula']}")
        else:
            # Nova inscrição
            valores = [
                dados["nome"],
                dados["matricula"],
                dados["data_admissao"],
                dados["lotacao_atual"],
                dados["escolha_anexo1"],
                dados["escolha_anexo2"],
                dados["data_inscricao"],
                telefone_formatado,                          # H: quem registrou
                telefone_formatado,                          # I: quem alterou (mesmo, pois é novo)
                data_hora_atual,                             # J: quando
                dados.get("posicao_lista_classificatoria", "")  # K: posição
            ]
            sheet.append_row(valores)
            log_operation("criar_inscricao", telefone_usuario, f"matrícula {dados['matricula']}")
        
        return True
    except Exception as e:
        log_error(e, "salvar_inscricao")
        raise SheetsError(f"Erro ao salvar: {e}")


def excluir_inscricao(sheet, matricula, telefone_usuario="Público"):
    """
    Exclui uma inscrição pela matrícula.
    
    Args:
        sheet: Sheet object do gspread
        matricula: Matrícula da inscrição a excluir
        telefone_usuario: Telefone do usuário que está excluindo
        
    Returns:
        Tupla (sucesso, nome_excluido)
    """
    if sheet is None:
        raise SheetsError("Conexão com Google Sheets não disponível")
    
    try:
        registros = sheet.get_all_records()
        for i, reg in enumerate(registros, start=2):
            if str(reg.get("matricula", "")) == str(matricula):
                nome_excluido = reg.get("nome", "")
                sheet.delete_rows(i)
                log_operation("excluir_inscricao", telefone_usuario, f"matrícula {matricula} - {nome_excluido}")
                return True, nome_excluido
        return False, None
    except Exception as e:
        log_error(e, "excluir_inscricao")
        raise SheetsError(f"Erro ao excluir: {e}")


def buscar_inscricao(sheet, matricula):
    """
    Busca inscrição por matrícula.
    
    Args:
        sheet: Sheet object do gspread
        matricula: Matrícula a buscar
        
    Returns:
        Dicionário com dados da inscrição ou None
    """
    if sheet is None:
        return None
    
    try:
        registros = sheet.get_all_records()
        for reg in registros:
            if str(reg.get("matricula", "")) == str(matricula):
                return reg
        return None
    except Exception as e:
        log_error(e, "buscar_inscricao")
        return None

