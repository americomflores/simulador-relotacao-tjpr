"""
Página: Vagas após a simulação
"""
import streamlit as st
import pandas as pd
from data import ANEXO_I, ANEXO_II
from services.rajs_service import obter_raj_da_comarca
from utils.normalizers import normalizar_comarca
from pages._shared import get_sheet, get_inscricoes, get_resultado, footer

sheet = get_sheet()
df_inscricoes = get_inscricoes(sheet)

st.header("Vagas após a simulação")
st.caption("O que restou do Anexo I (não preenchidas) e o que abriu no Anexo II (vagas liberadas por quem saiu), agrupado por região")

if df_inscricoes.empty:
    st.info("Faça inscrições primeiro para poder ver esta análise.")
else:
    df_resultado, vagas_restantes_a1, vagas_disponiveis_a2, ajustes_lotacao = get_resultado(df_inscricoes)

    st.markdown("### Visão Geral")

    total_nao_preenchidas_a1 = sum(vagas_restantes_a1.values())
    total_disponiveis_a2 = sum(vagas_disponiveis_a2.values())

    col1, col2 = st.columns(2)
    col1.metric("Vagas não preenchidas (Anexo I)", total_nao_preenchidas_a1)
    col2.metric("Vagas abertas (Anexo II)", total_disponiveis_a2)

    st.divider()

    # Anexo I por RAJ
    st.markdown("### Anexo I - Vagas não preenchidas")
    st.caption("Vagas com déficit que continuam abertas porque ninguém as escolheu como 1ª opção")

    dados_raj_a1 = {}
    for codigo, qtd_restante in vagas_restantes_a1.items():
        if qtd_restante > 0:
            info = ANEXO_I[codigo]
            raj = obter_raj_da_comarca(info['comarca'], normalizar_func=normalizar_comarca)
            dados_raj_a1.setdefault(raj, []).append({
                'Comarca': info['comarca'], 'Unidade': info['unidade'],
                'Vagas não preenchidas': qtd_restante
            })

    if dados_raj_a1:
        for raj in sorted(dados_raj_a1.keys()):
            total_raj = sum(v['Vagas não preenchidas'] for v in dados_raj_a1[raj])
            with st.expander(f"**{raj}** ({total_raj} vagas não preenchidas)"):
                df_raj = pd.DataFrame(dados_raj_a1[raj]).sort_values('Comarca')
                st.dataframe(df_raj[['Comarca', 'Unidade', 'Vagas não preenchidas']],
                             hide_index=True, use_container_width=True)
    else:
        st.success("Todas as vagas do Anexo I foram preenchidas!")

    st.divider()

    # Anexo II por RAJ
    st.markdown("### Anexo II - Vagas abertas pela simulação")
    st.caption("Unidades que passaram a ter vaga porque servidores foram aprovados e saíram")

    dados_raj_a2 = {}
    for codigo, qtd_disponivel in vagas_disponiveis_a2.items():
        if qtd_disponivel > 0 and codigo in ANEXO_II:
            info = ANEXO_II[codigo]
            raj = obter_raj_da_comarca(info['comarca'], normalizar_func=normalizar_comarca)
            dados_raj_a2.setdefault(raj, []).append({
                'Comarca': info['comarca'], 'Unidade': info['unidade'],
                'Vagas Disponíveis': qtd_disponivel
            })

    if dados_raj_a2:
        for raj in sorted(dados_raj_a2.keys()):
            total_raj = sum(v['Vagas Disponíveis'] for v in dados_raj_a2[raj])
            with st.expander(f"**{raj}** ({total_raj} vagas disponíveis)"):
                df_raj = pd.DataFrame(dados_raj_a2[raj]).sort_values('Comarca')
                st.dataframe(df_raj[['Comarca', 'Unidade', 'Vagas Disponíveis']],
                             hide_index=True, use_container_width=True)
    else:
        st.info("Nenhuma vaga do Anexo II abriu ainda. Vagas só abrem quando servidores saem e deixam a unidade de origem precisando de gente.")

footer()
