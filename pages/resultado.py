"""
Página: Resultado da Simulação
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from data import ANEXO_I, ANEXO_II
from config.theme import get_tema
from utils.ui_components import (
    empty_state, loading_spinner, metric_card
)
from utils.ui_helpers import extrair_comarca_da_string
from pages._shared import get_sheet, get_inscricoes, get_resultado, footer

sheet = get_sheet()
df_inscricoes = get_inscricoes(sheet)

st.header("Resultado da Simulação")
st.caption("Edital nº 01/2026 - Técnico Judiciário")

if df_inscricoes.empty:
    empty_state(
        "Nenhum servidor inscrito ainda",
        icon="📭",
        suggestion="O resultado aparecerá quando houver inscrições. Faça sua inscrição na página Inscrição"
    )
else:
    with loading_spinner("Calculando resultado da simulação..."):
        df_resultado, vagas_restantes_a1, vagas_disponiveis_a2, ajustes_lotacao = get_resultado(df_inscricoes)

    total = len(df_resultado)
    df_aprovados = df_resultado[df_resultado["status"] == "APROVADO"]
    aprovados_a1 = len(df_aprovados[df_aprovados["resultado"].str.startswith("Anexo I", na=False)])
    aprovados_a2 = len(df_aprovados[df_aprovados["resultado"].str.startswith("Anexo II", na=False)])
    desclass = len(df_resultado[df_resultado["status"] == "DESCLASSIFICADO"])
    com_designacao = len(df_resultado[df_resultado["designacao_origem"] == "SIM"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Inscritos", str(total), icon="👥", color="blue")
    with col2:
        metric_card("Aprovados Anexo I", str(aprovados_a1),
                    delta="Inclui direto e via item 3.13", icon="✅", color="green")
    with col3:
        metric_card("Aprovados Anexo II", str(aprovados_a2), icon="✅", color="green")
    with col4:
        metric_card("Com Designação", str(com_designacao),
                    delta="Aguardam substituição", icon="⏳", color="orange")

    st.divider()

    st.subheader("Resultado por Ordem da Lista Classificatória")

    df_resultado["data_admissao_fmt"] = df_resultado["data_admissao"].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
    )
    df_resultado["unidade_origem"] = df_resultado["lotacao_atual"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
    )

    col_busca, col_filtro = st.columns([3, 1])
    with col_busca:
        busca_resultado = st.text_input(
            "Buscar no resultado:",
            placeholder="Digite nome ou matrícula...",
            key="busca_resultado"
        )
    with col_filtro:
        filtro_status = st.selectbox(
            "Filtrar por status:",
            ["Todos", "APROVADO", "DESCLASSIFICADO", "NÃO OBTEVE VAGA"],
            key="filtro_status_resultado"
        )

    df_filtrado = df_resultado.copy()

    if busca_resultado:
        termo = busca_resultado.lower()
        mask = (
            df_filtrado["nome"].astype(str).str.lower().str.contains(termo, na=False) |
            df_filtrado["matricula"].astype(str).str.lower().str.contains(termo, na=False)
        )
        df_filtrado = df_filtrado[mask]

    if filtro_status != "Todos":
        df_filtrado = df_filtrado[df_filtrado["status"] == filtro_status]

    df_exibir = df_filtrado[[
        "posicao_antiguidade", "nome", "matricula", "unidade_origem", "status",
        "vaga_obtida", "resultado", "designacao_origem"
    ]].copy()

    df_exibir = df_exibir.rename(columns={
        "posicao_antiguidade": "Pos.",
        "nome": "Nome",
        "matricula": "Matrícula",
        "unidade_origem": "Origem",
        "status": "Status",
        "vaga_obtida": "Vaga Obtida",
        "resultado": "Resultado",
        "designacao_origem": "Designação"
    })

    tema = get_tema()

    def highlight_row(row):
        if row["Status"] == "APROVADO":
            color = tema["row_waiting"] if row["Designação"] == "SIM" else tema["row_approved"]
        elif row["Status"] == "DESCLASSIFICADO":
            color = tema["row_rejected"]
        elif row["Status"] == "NÃO OBTEVE VAGA":
            color = tema["row_no_vacancy"]
        else:
            color = ""
        return [f"background-color: {color}" if color else ""] * len(row)

    st.dataframe(
        df_exibir.style.apply(highlight_row, axis=1),
        hide_index=True,
        height=500,
        use_container_width=True,
        column_config={
            "Origem": st.column_config.TextColumn("Origem", width="medium"),
            "Vaga Obtida": st.column_config.TextColumn("Vaga Obtida", width="medium"),
        }
    )

    st.caption(f"Exibindo: {len(df_filtrado)} de {len(df_resultado)} servidores")

    st.markdown("""
    **Legenda:**
    - 🟢 Aprovado (designação = NÃO) - pode sair imediatamente
    - 🟡 Aprovado (designação = SIM) - fica na origem até substituição
    - ⚪ Não obteve vaga
    """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vagas Restantes - Anexo I")
        vagas_rest = [
            {"Código": c, "Comarca": ANEXO_I[c]["comarca"], "Unidade": ANEXO_I[c]["unidade"], "Restantes": q}
            for c, q in vagas_restantes_a1.items() if q > 0
        ]
        if vagas_rest:
            st.dataframe(pd.DataFrame(vagas_rest), hide_index=True, use_container_width=True)
        else:
            st.success("Todas as vagas do Anexo I foram preenchidas!")

    with col2:
        st.subheader("Vagas Disponíveis - Anexo II")
        vagas_disp = [
            {"Código": c, "Comarca": ANEXO_II[c]["comarca"], "Unidade": ANEXO_II[c]["unidade"], "Disponíveis": q}
            for c, q in vagas_disponiveis_a2.items() if q > 0 and c in ANEXO_II
        ]
        if vagas_disp:
            st.dataframe(pd.DataFrame(vagas_disp), hide_index=True, use_container_width=True)
        else:
            st.info("Nenhuma vaga liberada no Anexo II ainda.")

    # Dashboard
    st.divider()
    st.subheader("Dashboard - Estatísticas")

    aprovados = len(df_resultado[df_resultado["status"] == "APROVADO"])
    sem_vaga = len(df_resultado[df_resultado["status"] == "NÃO OBTEVE VAGA"])
    sem_designacao = len(df_resultado[df_resultado["designacao_origem"] == "NÃO"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Aprovados", aprovados, f"{100*aprovados/total:.1f}%" if total > 0 else "0%")
    col2.metric("Anexo I", aprovados_a1)
    col3.metric("Anexo II", aprovados_a2)
    col4.metric("Desclassificados", desclass)
    col5.metric("Sem Vaga", sem_vaga)

    st.divider()
    st.subheader("Visualização Gráfica")

    tema_graf = get_tema()

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("**Distribuição de Resultados**")
        df_grafico = pd.DataFrame({
            'Status': ['Aprovados', 'Desclassificados', 'Sem Vaga'],
            'Quantidade': [aprovados, desclass, sem_vaga],
        })
        fig_pizza = px.pie(
            df_grafico, values='Quantidade', names='Status',
            color='Status',
            color_discrete_map={
                'Aprovados': tema_graf["chart_green"],
                'Desclassificados': tema_graf["chart_red"],
                'Sem Vaga': tema_graf["chart_gray"]
            },
            hole=0.4
        )
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_pizza.update_layout(
            showlegend=True, height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            template=tema_graf["plotly_template"]
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_graf2:
        st.markdown("**Aprovados por Anexo**")
        df_anexo = pd.DataFrame({
            'Anexo': ['Anexo I', 'Anexo II'],
            'Quantidade': [aprovados_a1, aprovados_a2],
        })
        fig_barras = px.bar(
            df_anexo, x='Anexo', y='Quantidade', color='Anexo',
            color_discrete_map={'Anexo I': tema_graf["chart_blue"], 'Anexo II': tema_graf["chart_green2"]},
            text='Quantidade'
        )
        fig_barras.update_traces(textposition='outside')
        fig_barras.update_layout(
            showlegend=False, height=350,
            yaxis_title="Servidores Aprovados", xaxis_title="",
            margin=dict(t=20, b=20, l=20, r=20),
            template=tema_graf["plotly_template"]
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        st.markdown("**Designação na Origem**")
        com_desig = len(df_resultado[df_resultado["designacao_origem"] == "SIM"])
        sem_desig = len(df_resultado[df_resultado["designacao_origem"] == "NÃO"])
        df_desig = pd.DataFrame({
            'Situação': ['Podem sair\nimediatamente', 'Aguardam\nsubstituição'],
            'Quantidade': [sem_desig, com_desig]
        })
        fig_desig = px.bar(
            df_desig, x='Situação', y='Quantidade', color='Situação',
            color_discrete_map={
                'Podem sair\nimediatamente': tema_graf["chart_green"],
                'Aguardam\nsubstituição': tema_graf["chart_yellow"]
            },
            text='Quantidade'
        )
        fig_desig.update_traces(textposition='outside')
        fig_desig.update_layout(
            showlegend=False, height=350,
            yaxis_title="Servidores Aprovados", xaxis_title="",
            margin=dict(t=20, b=20, l=20, r=20),
            template=tema_graf["plotly_template"]
        )
        st.plotly_chart(fig_desig, use_container_width=True)

    with col_graf4:
        st.markdown("**Top 5 Comarcas Mais Procuradas**")
        df_aprov = df_resultado[
            (df_resultado['status'] == 'APROVADO') &
            (df_resultado['vaga_obtida'].fillna('').ne('')) &
            (df_resultado['vaga_obtida'].ne('-'))
        ]
        comarcas_series = df_aprov['vaga_obtida'].apply(extrair_comarca_da_string)
        comarcas_count = comarcas_series.dropna().value_counts().to_dict()

        if comarcas_count:
            top_comarcas = sorted(comarcas_count.items(), key=lambda x: x[1], reverse=True)[:5]
            df_comarcas = pd.DataFrame(top_comarcas, columns=['Comarca', 'Servidores'])
            fig_comarcas = px.bar(
                df_comarcas, y='Comarca', x='Servidores', orientation='h',
                text='Servidores', color='Servidores',
                color_continuous_scale=tema_graf["chart_scale"]
            )
            fig_comarcas.update_traces(textposition='outside')
            fig_comarcas.update_layout(
                showlegend=False, height=350,
                xaxis_title="Servidores Aprovados", yaxis_title="",
                margin=dict(t=20, b=20, l=20, r=20),
                template=tema_graf["plotly_template"]
            )
            st.plotly_chart(fig_comarcas, use_container_width=True)
        else:
            st.info("Nenhum servidor aprovado ainda.")

footer()
