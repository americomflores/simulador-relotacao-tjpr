"""
Funções compartilhadas entre as páginas.
Carregamento de dados com cache e função de resultado cacheado.
"""
import streamlit as st
import pandas as pd
from services.sheets_service import conectar_sheets, carregar_inscricoes as _carregar_inscricoes
from services.simulacao_service import calcular_resultado, calcular_demanda


def get_sheet():
    """Retorna a conexão com Google Sheets (cacheada pelo @st.cache_resource do service)."""
    try:
        return conectar_sheets()
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        st.info("Verifique se o arquivo `.streamlit/secrets.toml` está configurado corretamente.")
        st.stop()


@st.cache_data(ttl=30)
def _carregar_inscricoes_cached(_sheet):
    """Carrega inscrições com cache de 30 segundos."""
    return _carregar_inscricoes(_sheet)


def get_inscricoes(sheet):
    """Carrega inscrições do sheet, com cache."""
    try:
        return _carregar_inscricoes_cached(sheet)
    except Exception as e:
        st.error(f"Erro ao carregar inscrições: {e}")
        return pd.DataFrame()


def invalidar_cache():
    """Limpa caches após salvar/excluir."""
    _carregar_inscricoes_cached.clear()


def _calcular_checksum(df):
    """Calcula checksum eficiente de um DataFrame."""
    return pd.util.hash_pandas_object(df).sum()


def get_resultado(df_inscricoes):
    """
    Retorna resultado da simulação com cache em session_state.
    Calcula apenas 1x por sessão (até dados mudarem).
    """
    if df_inscricoes.empty:
        return pd.DataFrame(), {}, {}, {}

    checksum = _calcular_checksum(df_inscricoes)
    if st.session_state.get("_resultado_checksum") != checksum or "_resultado_cache" not in st.session_state:
        st.session_state["_resultado_cache"] = calcular_resultado(df_inscricoes)
        st.session_state["_resultado_checksum"] = checksum
    return st.session_state["_resultado_cache"]


def get_demanda(df_inscricoes):
    """
    Retorna demanda com cache em session_state.
    """
    if df_inscricoes.empty:
        return {}, {}

    checksum = _calcular_checksum(df_inscricoes)
    if st.session_state.get("_demanda_checksum") != checksum or "_demanda_cache" not in st.session_state:
        st.session_state["_demanda_cache"] = calcular_demanda(df_inscricoes)
        st.session_state["_demanda_checksum"] = checksum
    return st.session_state["_demanda_cache"]


def footer():
    """Rodapé padrão."""
    st.divider()
    st.caption(
        "Este é um simulador não oficial, criado apenas para auxiliar na tomada de decisão. "
        "O resultado oficial depende exclusivamente da análise do TJPR conforme Edital nº 1/2026."
    )
