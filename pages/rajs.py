"""
Página: Regiões Administrativas Judiciárias (RAJs)
"""
import streamlit as st
import pandas as pd
from data import ANEXO_II
from config.rajs_config import RAJS
from services.rajs_service import obter_raj_da_comarca
from pages._shared import get_sheet, get_inscricoes, get_resultado, footer

sheet = get_sheet()
df_inscricoes = get_inscricoes(sheet)

st.header("Regiões Administrativas Judiciárias (RAJs)")
st.info("Veja quantos servidores **aprovados** existem em cada região geográfica do Paraná (baseado na unidade onde trabalham atualmente).")

if df_inscricoes.empty:
    st.warning("Nenhum servidor inscrito ainda.")
else:
    df_resultado, _, _, _ = get_resultado(df_inscricoes)
    df_aprovados = df_resultado[df_resultado["status"] == "APROVADO"].copy()

    if df_aprovados.empty:
        st.warning("Nenhum candidato aprovado ainda para análise por RAJ.")
    else:
        def get_comarca_origem(codigo_lotacao):
            if codigo_lotacao and codigo_lotacao in ANEXO_II:
                return ANEXO_II[codigo_lotacao]["comarca"]
            return "Não identificada"

        df_aprovados["comarca_origem"] = df_aprovados["lotacao_atual"].apply(get_comarca_origem)
        df_aprovados["raj_origem"] = df_aprovados["comarca_origem"].apply(obter_raj_da_comarca)

        contagem_raj = df_aprovados["raj_origem"].value_counts().reset_index()
        contagem_raj.columns = ["RAJ", "Quantidade de Aprovados"]
        contagem_raj = contagem_raj.sort_values("RAJ").reset_index(drop=True)

        # Mapa visual
        st.subheader("Mapa das RAJs do Paraná")
        contagem_dict = dict(zip(contagem_raj["RAJ"], contagem_raj["Quantidade de Aprovados"]))

        def get_raj_qtd(raj_num):
            for raj, qtd in contagem_dict.items():
                if f"RAJ {raj_num}" in raj:
                    return qtd
            return 0

        st.markdown("**Norte do Paraná:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        for col, num, sede in [(col1, 10, "Jacarezinho"), (col2, 9, "Londrina"),
                                (col3, 8, "Maringá"), (col4, 7, "Umuarama")]:
            with col:
                qtd = get_raj_qtd(num)
                cor = "🟢" if qtd > 0 else "⚪"
                st.markdown(f"**RAJ {num}** {cor}  \n{sede}  \n{qtd} aprovados")
        with col5:
            st.markdown("")

        st.markdown("**Centro-Oeste:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        for col, num, sede in [(col1, 2, "Ponta Grossa"), (col2, 3, "Guarapuava"),
                                (col3, 6, "Cascavel"), (col4, 5, "Foz do Iguaçu")]:
            with col:
                qtd = get_raj_qtd(num)
                cor = "🟢" if qtd > 0 else "⚪"
                st.markdown(f"**RAJ {num}** {cor}  \n{sede}  \n{qtd} aprovados")
        with col5:
            st.markdown("")

        st.markdown("**Sul e Litoral:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        for col, num, sede in [(col1, 1, "Curitiba/Litoral"), (col2, 4, "Francisco Beltrão")]:
            with col:
                qtd = get_raj_qtd(num)
                cor = "🟢" if qtd > 0 else "⚪"
                st.markdown(f"**RAJ {num}** {cor}  \n{sede}  \n{qtd} aprovados")
        for col in [col3, col4, col5]:
            with col:
                st.markdown("")

        st.divider()

        st.subheader("Resumo por RAJ")
        cols = st.columns(5)
        for i, (_, row) in enumerate(contagem_raj.iterrows()):
            col_idx = i % 5
            raj_nome_curto = row["RAJ"].replace("RAJ ", "").replace("Região Administrativa ", "")
            if len(raj_nome_curto) > 25:
                raj_nome_curto = raj_nome_curto[:22] + "..."
            cols[col_idx].metric(raj_nome_curto, row["Quantidade de Aprovados"])

        st.divider()

        st.subheader("Detalhamento por RAJ")
        dados_raj_detalhado = []
        for raj_nome in sorted(RAJS.keys()):
            raj_info = RAJS[raj_nome]
            qtd = len(df_aprovados[df_aprovados["raj_origem"] == raj_nome])
            comarcas_str = ", ".join(sorted(raj_info["comarcas"]))
            dados_raj_detalhado.append({
                "RAJ": raj_nome, "Sede": raj_info["sede"],
                "Aprovados": qtd, "Comarcas": comarcas_str
            })

        st.dataframe(
            pd.DataFrame(dados_raj_detalhado),
            hide_index=True, use_container_width=True,
            column_config={
                "RAJ": st.column_config.TextColumn("Região Administrativa", width="medium"),
                "Sede": st.column_config.TextColumn("Sede", width="small"),
                "Aprovados": st.column_config.NumberColumn("Aprovados", width="small"),
                "Comarcas": st.column_config.TextColumn("Comarcas Abrangidas", width="large")
            }
        )

        st.divider()

        st.subheader("Lista de Aprovados por RAJ")
        rajs_com_aprovados = sorted(df_aprovados["raj_origem"].unique())
        raj_selecionada = st.selectbox("Selecione uma RAJ:", ["Todas"] + rajs_com_aprovados)

        df_filtrado = df_aprovados.copy() if raj_selecionada == "Todas" else df_aprovados[df_aprovados["raj_origem"] == raj_selecionada].copy()

        df_filtrado["data_admissao_fmt"] = df_filtrado["data_admissao"].apply(
            lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
        )

        st.dataframe(
            df_filtrado[[
                "posicao_antiguidade", "nome", "matricula", "data_admissao_fmt",
                "comarca_origem", "raj_origem", "resultado", "vaga_obtida", "designacao_origem"
            ]].rename(columns={
                "posicao_antiguidade": "Pos.",
                "nome": "Nome", "matricula": "Matrícula",
                "data_admissao_fmt": "Data Admissão",
                "comarca_origem": "Comarca Origem", "raj_origem": "RAJ Origem",
                "resultado": "Resultado", "vaga_obtida": "Vaga Obtida",
                "designacao_origem": "Designação Origem"
            }),
            hide_index=True, use_container_width=True
        )
        st.caption(f"Total de aprovados exibidos: {len(df_filtrado)}")

footer()
