"""
Página: Lista de Inscritos
"""
import streamlit as st
import pandas as pd
from data import ANEXO_I, ANEXO_II
from services.simulacao_service import obter_status_lotacao
from pages._shared import get_sheet, get_inscricoes, footer

sheet = get_sheet()
df_inscricoes = get_inscricoes(sheet)

st.header("Lista de Inscritos")
st.caption("Todos os servidores que se inscreveram na relotação")

if df_inscricoes.empty:
    st.info("Nenhum servidor inscrito ainda.")
else:
    df_display = df_inscricoes.copy()

    df_display["posicao_lista_classificatoria"] = pd.to_numeric(
        df_display["posicao_lista_classificatoria"], errors="coerce"
    ).astype("Int64")

    df_display = df_display.sort_values(
        "posicao_lista_classificatoria", ascending=True, na_position='last'
    ).reset_index(drop=True)

    df_display["posicao"] = df_display["posicao_lista_classificatoria"]

    df_display["data_admissao_fmt"] = df_display["data_admissao"].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
    )
    df_display["status_origem"] = df_display["lotacao_atual"].apply(obter_status_lotacao)
    df_display["lotacao_desc"] = df_display["lotacao_atual"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x in ANEXO_II else x
    )
    df_display["escolha_a1_desc"] = df_display["escolha_anexo1"].apply(
        lambda x: f"{ANEXO_I[x]['comarca']} - {ANEXO_I[x]['unidade']}" if x and x in ANEXO_I else "-"
    )
    df_display["escolha_a2_desc"] = df_display["escolha_anexo2"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
    )

    busca_servidor = st.text_input("Buscar servidor:", key="busca_servidor",
                                    placeholder="Digite nome ou matrícula...")

    df_filtrado = df_display.copy()
    if busca_servidor:
        termo = busca_servidor.lower()
        mask = (
            df_filtrado["nome"].astype(str).str.lower().str.contains(termo, na=False) |
            df_filtrado["matricula"].astype(str).str.lower().str.contains(termo, na=False)
        )
        df_filtrado = df_filtrado[mask]

    st.dataframe(
        df_filtrado[[
            "posicao", "nome", "matricula", "data_admissao_fmt",
            "status_origem", "lotacao_desc", "escolha_a1_desc", "escolha_a2_desc"
        ]].rename(columns={
            "posicao": "Pos.",
            "nome": "Nome",
            "matricula": "Matrícula",
            "data_admissao_fmt": "Data Admissão",
            "status_origem": "Status Origem",
            "lotacao_desc": "Lotação Atual",
            "escolha_a1_desc": "Escolha Anexo I",
            "escolha_a2_desc": "Escolha Anexo II"
        }),
        hide_index=True,
        use_container_width=True
    )

    st.caption(f"Exibindo: {len(df_filtrado)} de {len(df_display)} servidores inscritos")

    with st.expander("Histórico de Registros/Alterações"):
        st.markdown("**Quem cadastrou ou alterou cada inscrição:**")
        tem_log = "registrado_por" in df_display.columns and "alterado_por" in df_display.columns
        if tem_log:
            df_log = df_display[["nome", "matricula", "registrado_por", "alterado_por", "data_alteracao"]].copy()
            df_log["registrado_por"] = df_log["registrado_por"].fillna("-")
            df_log["alterado_por"] = df_log["alterado_por"].fillna("-")
            df_log["data_alteracao"] = df_log["data_alteracao"].fillna("-")
            st.dataframe(
                df_log.rename(columns={
                    "nome": "Nome", "matricula": "Matrícula",
                    "registrado_por": "Registrado Por",
                    "alterado_por": "Última Alteração Por",
                    "data_alteracao": "Data/Hora Alteração"
                }),
                hide_index=True, use_container_width=True
            )
        else:
            st.info("Registros antigos não possuem informações de log.")

footer()
