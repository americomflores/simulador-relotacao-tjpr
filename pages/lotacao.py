"""
Página: Lotação das Unidades Judiciárias
"""
import streamlit as st
import pandas as pd
from lotacao_data import LOTACAO_POR_CODIGO, LOTACAO_COMPLETA
from config.theme import get_tema
from pages._shared import footer

st.header("Lotação das Unidades Judiciárias")
st.info("Dados oficiais do TJPR mostrando quantos servidores tem cada unidade (Lotação Real) e quantos deveriam ter pelo mínimo legal (Lotação Paradigma CNJ 219/2016).")

# Métricas gerais
col1, col2, col3, col4 = st.columns(4)

total_unidades = len(LOTACAO_COMPLETA)
superavit = len([u for u in LOTACAO_COMPLETA if u["status"] == "SUPERAVITÁRIA"])
equilibrada = len([u for u in LOTACAO_COMPLETA if u["status"] == "EQUILIBRADA"])
deficit = len([u for u in LOTACAO_COMPLETA if u["status"] == "DEFICITÁRIA"])

col1.metric("Total Unidades", total_unidades)
col2.metric("Acima do Mínimo", superavit, help="Unidades com mais servidores que o necessário")
col3.metric("No Mínimo", equilibrada, help="Unidades com exatamente o necessário")
col4.metric("Abaixo do Mínimo", deficit, help="Unidades com menos servidores que o necessário")

st.divider()

# Filtros
col1, col2, col3 = st.columns(3)

with col1:
    comarcas_lot = sorted(set(u["comarca"] for u in LOTACAO_COMPLETA))
    filtro_comarca_lot = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_lot, key="filtro_comarca_lot")

with col2:
    filtro_status_lot = st.selectbox("Filtrar por status:",
                                      ["Todos", "SUPERAVITÁRIA", "EQUILIBRADA", "DEFICITÁRIA"],
                                      key="filtro_status_lot")

with col3:
    busca_lot = st.text_input("Buscar:", key="busca_lot", placeholder="Nome da unidade...")

# Mapeamento reverso
mapa_codigo = {}
for codigo, dados in LOTACAO_POR_CODIGO.items():
    chave = (dados["comarca"].lower().strip(), dados["unidade"].lower().strip())
    mapa_codigo[chave] = codigo

dados_lotacao = []
for u in LOTACAO_COMPLETA:
    chave = (u["comarca"].lower().strip(), u["unidade"].lower().strip())
    codigo = mapa_codigo.get(chave, "-")
    dados_lotacao.append({
        "Código": codigo, "Comarca": u["comarca"], "Unidade": u["unidade"],
        "Lotação Real": u["lotacao_real"], "Lotação Paradigma": u["lotacao_paradigma"],
        "Diferença": u["diferenca"], "Status": u["status"]
    })

df_lotacao = pd.DataFrame(dados_lotacao)

if filtro_comarca_lot != "Todas":
    df_lotacao = df_lotacao[df_lotacao["Comarca"] == filtro_comarca_lot]
if filtro_status_lot != "Todos":
    df_lotacao = df_lotacao[df_lotacao["Status"] == filtro_status_lot]
if busca_lot:
    mask = df_lotacao.apply(lambda x: busca_lot.lower() in x["Comarca"].lower() or busca_lot.lower() in x["Unidade"].lower(), axis=1)
    df_lotacao = df_lotacao[mask]

tema_lot = get_tema()

def color_status_lot(val):
    if val == "SUPERAVITÁRIA":
        return f"background-color: {tema_lot['status_superavit']}"
    elif val == "EQUILIBRADA":
        return f"background-color: {tema_lot['status_equilibrada']}"
    elif val == "DEFICITÁRIA":
        return f"background-color: {tema_lot['status_deficitaria']}"
    return ""

def color_diferenca(val):
    try:
        if int(val) > 0:
            return f"color: {tema_lot['text_positive']}; font-weight: bold"
        elif int(val) < 0:
            return f"color: {tema_lot['text_negative']}; font-weight: bold"
    except (ValueError, TypeError):
        pass
    return ""

st.dataframe(
    df_lotacao.style.map(color_status_lot, subset=["Status"]).map(color_diferenca, subset=["Diferença"]),
    hide_index=True,
    height=500,
    use_container_width=True
)

st.caption(f"Exibindo: {len(df_lotacao)} de {total_unidades} unidades")

footer()
