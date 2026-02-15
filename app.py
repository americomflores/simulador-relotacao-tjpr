"""
Simulador de Relotação - TJPR
Edital nº 01/2026 - Técnico Judiciário

Entry point — cada página é independente via st.navigation().
"""

import streamlit as st
from config.theme import inject_css

st.set_page_config(
    page_title="Simulador Relotação TJPR",
    page_icon="⚖️",
    layout="wide"
)

inject_css()

paginas = st.navigation([
    st.Page("pages/como_usar.py", title="Como Usar", icon="❓", default=True),
    st.Page("pages/resultado.py", title="Resultado", icon="🏆"),
    st.Page("pages/inscricao.py", title="Inscrição", icon="✍️"),
    st.Page("pages/inscritos.py", title="Inscritos", icon="👥"),
    st.Page("pages/vagas_edital.py", title="Vagas do Edital", icon="📋"),
    st.Page("pages/vagas_simulacao.py", title="Vagas após Simulação", icon="📊"),
    st.Page("pages/lotacao.py", title="Lotação", icon="📈"),
    st.Page("pages/rajs.py", title="Regiões (RAJs)", icon="🗺️"),
])

paginas.run()
