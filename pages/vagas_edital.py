"""
Página: Vagas do Edital (Anexos I e II)
"""
import streamlit as st
import pandas as pd
from data import ANEXO_I, ANEXO_II
from config.theme import get_tema
from services.simulacao_service import obter_status_lotacao
from pages._shared import get_sheet, get_inscricoes, get_demanda, footer


@st.cache_data
def _build_df_a1_base():
    """Constrói DataFrame base do Anexo I (dados constantes)."""
    dados = []
    for codigo, info in ANEXO_I.items():
        dados.append({
            "Código": codigo, "Comarca": info["comarca"],
            "Unidade Judiciária": info["unidade"],
            "Vagas": info["quantidade"]
        })
    return pd.DataFrame(dados)


@st.cache_data
def _build_df_a2_base():
    """Constrói DataFrame base do Anexo II (dados constantes)."""
    dados = []
    for codigo, info in ANEXO_II.items():
        dados.append({
            "Código": codigo, "Comarca": info["comarca"],
            "Unidade Judiciária": info["unidade"],
            "Status Lotação": obter_status_lotacao(codigo)
        })
    return pd.DataFrame(dados)


sheet = get_sheet()
df_inscricoes = get_inscricoes(sheet)
demanda_a1, demanda_a2 = get_demanda(df_inscricoes)

st.header("Vagas do Edital")
st.caption("Catálogo de vagas com quantidade e demanda (quantos inscritos escolheram cada unidade)")

opcao_vagas = st.radio(
    "Escolha o anexo:",
    ["Anexo I (Vagas com Déficit)", "Anexo II (Todas as Unidades)"],
    horizontal=True, key="opcao_vagas"
)

st.divider()

if opcao_vagas == "Anexo I (Vagas com Déficit)":
    st.subheader("Vagas com Déficit (Anexo I)")
    st.info("**Anexo I** = 213 unidades com 435 vagas (unidades deficitárias). A coluna **Demanda** mostra quantos servidores querem ir para cada unidade.")

    df_a1 = _build_df_a1_base().copy()
    df_a1["Demanda"] = df_a1["Código"].map(demanda_a1).fillna(0).astype(int)
    df_a1["Concorrência"] = df_a1.apply(
        lambda r: "🟢 Sem demanda" if r["Demanda"] == 0
        else "🟡 Baixa" if r["Demanda"] < r["Vagas"]
        else "🟠 Equilibrada" if r["Demanda"] == r["Vagas"]
        else "🔴 Alta", axis=1
    )

    col1, col2 = st.columns(2)
    with col1:
        filtro_comarca_a1 = st.selectbox("Filtrar por comarca:", ["Todas"] + sorted(df_a1["Comarca"].unique()), key="filtro_a1")
    with col2:
        filtro_conc = st.selectbox("Filtrar por concorrência:",
                                    ["Todas", "🟢 Sem demanda", "🟡 Baixa", "🟠 Equilibrada", "🔴 Alta"],
                                    key="filtro_conc_a1")

    if filtro_comarca_a1 != "Todas":
        df_a1 = df_a1[df_a1["Comarca"] == filtro_comarca_a1]
    if filtro_conc != "Todas":
        df_a1 = df_a1[df_a1["Concorrência"] == filtro_conc]

    busca_a1 = st.text_input("Buscar:", key="busca_a1", placeholder="Nome da comarca ou unidade...")
    if busca_a1:
        mask = df_a1.apply(lambda x: busca_a1.lower() in x["Comarca"].lower() or busca_a1.lower() in x["Unidade Judiciária"].lower(), axis=1)
        df_a1 = df_a1[mask]

    st.dataframe(df_a1, hide_index=True, use_container_width=True)
    st.caption(f"Total: {len(df_a1)} unidades | {df_a1['Vagas'].sum()} vagas | {df_a1['Demanda'].sum()} servidores interessados")

else:
    st.subheader("Todas as Unidades (Anexo II)")
    st.info("**Anexo II** = Todas as 606 unidades judiciárias do TJPR. A coluna **Demanda** mostra quantos servidores querem ir para cada unidade (2ª opção).")

    df_a2 = _build_df_a2_base().copy()
    df_a2["Demanda"] = df_a2["Código"].map(demanda_a2).fillna(0).astype(int)

    col1, col2 = st.columns(2)
    with col1:
        filtro_comarca_a2 = st.selectbox("Filtrar por comarca:", ["Todas"] + sorted(df_a2["Comarca"].unique()), key="filtro_a2")
    with col2:
        filtro_status = st.selectbox("Filtrar por status de lotação:",
                                      ["Todos", "SUPERAVITÁRIA", "EQUILIBRADA", "DEFICITÁRIA", "NÃO IDENTIFICADA"],
                                      key="filtro_status_a2")

    if filtro_comarca_a2 != "Todas":
        df_a2 = df_a2[df_a2["Comarca"] == filtro_comarca_a2]
    if filtro_status != "Todos":
        df_a2 = df_a2[df_a2["Status Lotação"] == filtro_status]

    mostrar_com_demanda = st.checkbox("Mostrar apenas unidades com demanda", key="filtro_demanda_a2")
    if mostrar_com_demanda:
        df_a2 = df_a2[df_a2["Demanda"] > 0]

    busca_a2 = st.text_input("Buscar:", key="busca_a2", placeholder="Nome da comarca ou unidade...")
    if busca_a2:
        mask = df_a2.apply(lambda x: busca_a2.lower() in x["Comarca"].lower() or busca_a2.lower() in x["Unidade Judiciária"].lower(), axis=1)
        df_a2 = df_a2[mask]

    tema_vagas = get_tema()

    def color_status(val):
        if val == "SUPERAVITÁRIA":
            return f"background-color: {tema_vagas['status_superavit']}"
        elif val == "EQUILIBRADA":
            return f"background-color: {tema_vagas['status_equilibrada']}"
        elif val == "DEFICITÁRIA":
            return f"background-color: {tema_vagas['status_deficitaria']}"
        return ""

    st.dataframe(
        df_a2.style.map(color_status, subset=["Status Lotação"]),
        hide_index=True, use_container_width=True
    )
    st.caption(f"Total: {len(df_a2)} unidades | {df_a2['Demanda'].sum()} servidores interessados")

footer()
