"""
Página: Inscrição / Edição
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from data import ANEXO_I, ANEXO_II
from lista_classificatoria import LISTA_CLASSIFICATORIA
from config.matricula_posicao_map import MATRICULA_POSICAO_MAP
from config.constants import OPCAO_NAO_ESCOLHEU
from services.sheets_service import salvar_inscricao, excluir_inscricao, buscar_inscricao
from services.search_service import buscar_servidor_por_nome
from utils.ui_helpers import (
    construir_opcoes_selectbox, extrair_codigo_da_opcao, encontrar_indice_opcao
)
from utils.ui_components import alert_box
from utils.error_handlers import handle_success
from pages._shared import get_sheet, get_inscricoes, invalidar_cache, footer

sheet = get_sheet()
df_inscricoes = get_inscricoes(sheet)

st.header("Inscrição / Edição")


# ---- Busca isolada com @st.fragment para não causar rerun da página inteira ----
@st.fragment
def busca_servidor():
    """Fragmento de busca — reruns ficam isolados aqui."""
    matricula_busca = st.text_input(
        "Matrícula (para nova inscrição ou editar existente):", key="mat_busca"
    )

    inscricao_existente = None
    posicao_por_matricula = None
    posicao_sugerida = None
    nome_encontrado = ""

    if matricula_busca:
        inscricao_existente = buscar_inscricao(sheet, matricula_busca)
        if inscricao_existente:
            st.info("Inscrição encontrada! Os dados serão carregados para edição.")

        if matricula_busca in MATRICULA_POSICAO_MAP:
            posicao_por_matricula = MATRICULA_POSICAO_MAP[matricula_busca]
            st.success(f"Matrícula mapeada! Posição na lista: **{posicao_por_matricula}**")

        # Fallback: usar dados da inscrição existente se disponíveis
        if inscricao_existente and not posicao_por_matricula:
            pos_existente = inscricao_existente.get("posicao_lista_classificatoria")
            if pos_existente:
                try:
                    posicao_sugerida = int(pos_existente)
                    if posicao_sugerida in LISTA_CLASSIFICATORIA:
                        nome_encontrado = LISTA_CLASSIFICATORIA[posicao_sugerida]['nome_display']
                except (ValueError, TypeError):
                    pass

    st.subheader("Buscar Servidor na Lista Classificatória")

    # Preencher nome quando inscricao_existente vem da busca por matrícula
    default_nome = ""
    if matricula_busca and inscricao_existente:
        default_nome = inscricao_existente.get("nome", "")

    nome_busca_auto = st.text_input(
        "Digite o nome completo do servidor:",
        value=default_nome,
        help="A busca é feita automaticamente conforme você digita",
        key="nome_busca_auto"
    )

    # Prioridade: posicao_por_matricula > busca por nome
    if posicao_por_matricula:
        posicao_sugerida = posicao_por_matricula
        if posicao_sugerida in LISTA_CLASSIFICATORIA:
            nome_encontrado = LISTA_CLASSIFICATORIA[posicao_sugerida]['nome_display']
    elif nome_busca_auto and len(nome_busca_auto.strip()) >= 3:
        resultado = buscar_servidor_por_nome(nome_busca_auto)
        if resultado:
            posicao_sugerida, score, nome_lista = resultado
            if score >= 95:
                st.success(f"**Servidor encontrado na Lista Classificatória!**\n\n**Posição: {posicao_sugerida}**\n\nNome na lista: {nome_lista}")
                nome_encontrado = nome_lista
            elif score >= 85:
                st.warning(f"**Servidor possivelmente encontrado** (similaridade: {score}%)\n\n**Posição: {posicao_sugerida}**\n\nNome na lista: {nome_lista}\n\nVerifique se está correto ou informe a posição manualmente abaixo!")
                nome_encontrado = nome_lista
        else:
            st.error("**Servidor NÃO encontrado automaticamente!**\n\nInforme a posição manualmente no formulário abaixo.")

    # Buscar inscrição existente por nome (evitar duplicidade)
    if posicao_sugerida and nome_encontrado and inscricao_existente is None:
        nome_lista_normalizado = nome_encontrado.strip().lower()
        if not df_inscricoes.empty and "nome" in df_inscricoes.columns:
            df_match = df_inscricoes[df_inscricoes["nome"].astype(str).str.strip().str.lower() == nome_lista_normalizado]
            if not df_match.empty:
                row = df_match.iloc[0]
                inscricao_existente = {}
                for col in df_inscricoes.columns:
                    val = row[col]
                    if isinstance(val, date):
                        inscricao_existente[col] = val.strftime("%d/%m/%Y")
                    elif pd.notna(val):
                        inscricao_existente[col] = str(val)
                    else:
                        inscricao_existente[col] = ""
                st.info(f"**Inscrição existente encontrada pelo nome!** Matrícula: **{inscricao_existente.get('matricula', '')}** — dados carregados para edição.")

    # Salvar no session_state para o form usar
    st.session_state["_inscricao_existente"] = inscricao_existente
    st.session_state["_posicao_sugerida"] = posicao_sugerida
    st.session_state["_nome_encontrado"] = nome_encontrado
    st.session_state["_matricula_busca"] = matricula_busca

    if posicao_sugerida and nome_encontrado:
        if st.button("✅ Preencher formulário com os dados encontrados", type="primary"):
            st.rerun()
    elif inscricao_existente and not posicao_sugerida:
        # Inscrição existe mas sem posição mapeada — permitir carregar dados mesmo assim
        if st.button("✅ Carregar dados da inscrição existente", type="primary"):
            st.rerun()


busca_servidor()

# ---- Formulário de inscrição (fora do fragment) ----
st.divider()
st.warning("**Antes de inscrever**, verifique os requisitos do edital. Consulte a página **Como Usar** para detalhes.")

inscricao_existente = st.session_state.get("_inscricao_existente")
posicao_sugerida = st.session_state.get("_posicao_sugerida")
nome_encontrado = st.session_state.get("_nome_encontrado", "")
matricula_busca = st.session_state.get("_matricula_busca", "")

matricula_valor = matricula_busca
if not matricula_valor and inscricao_existente:
    matricula_valor = str(inscricao_existente.get("matricula", ""))

with st.form("form_inscricao"):
    nome = st.text_input(
        "Nome completo:",
        value=nome_encontrado if nome_encontrado else (inscricao_existente.get("nome", "") if inscricao_existente else ""),
        help="Nome do servidor (preenchido automaticamente se encontrado acima)"
    )

    posicao_default = posicao_sugerida if posicao_sugerida else (
        inscricao_existente.get("posicao_lista_classificatoria") if inscricao_existente else None
    )

    posicao_lista = st.number_input(
        "Posição na Lista Classificatória:",
        min_value=1, max_value=1291,
        value=int(posicao_default) if posicao_default else 1,
        step=1,
        help="Posição do servidor na Lista Classificatória do Edital 01/2026 (1 a 1291)"
    )

    if posicao_lista and posicao_lista in LISTA_CLASSIFICATORIA:
        dados_posicao = LISTA_CLASSIFICATORIA[posicao_lista]
        st.info(f"**Posição {posicao_lista}:** {dados_posicao['nome_display']}")

    matricula = st.text_input(
        "Matrícula:",
        value=matricula_valor,
        disabled=True if matricula_valor else False
    )

    data_default = None
    if inscricao_existente and inscricao_existente.get("data_admissao"):
        try:
            data_default = datetime.strptime(inscricao_existente["data_admissao"], "%d/%m/%Y").date()
        except (ValueError, TypeError):
            pass

    if data_default is None and posicao_sugerida and posicao_sugerida in LISTA_CLASSIFICATORIA:
        try:
            inicio_cargo = LISTA_CLASSIFICATORIA[posicao_sugerida].get("inicio_cargo", "")
            if inicio_cargo:
                data_default = datetime.strptime(inicio_cargo, "%d/%m/%Y").date()
        except (ValueError, TypeError, KeyError):
            pass

    data_admissao = st.date_input(
        "Data de início do exercício:",
        value=data_default,
        min_value=date(1980, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY"
    )

    opcoes_lotacao = construir_opcoes_selectbox(ANEXO_II, default_text="", incluir_vazio=True)
    lotacao_default = 0
    if inscricao_existente and inscricao_existente.get("lotacao_atual"):
        lotacao_default = encontrar_indice_opcao(opcoes_lotacao, inscricao_existente["lotacao_atual"])

    lotacao_atual = st.selectbox("Lotação Atual:", opcoes_lotacao, index=lotacao_default,
                                  help="Unidade judiciária onde você está lotado atualmente")

    opcoes_a1 = construir_opcoes_selectbox(ANEXO_I, default_text=OPCAO_NAO_ESCOLHEU, incluir_vazio=True, mostrar_quantidade=True)
    escolha_a1_default = 0
    if inscricao_existente and inscricao_existente.get("escolha_anexo1"):
        escolha_a1_default = encontrar_indice_opcao(opcoes_a1, inscricao_existente["escolha_anexo1"])

    escolha_a1 = st.selectbox("1ª Escolha - Anexo I (Vagas Prioritárias com Déficit):", opcoes_a1,
                               index=escolha_a1_default,
                               help="213 unidades judiciárias com 435 vagas. Opcional.")

    opcoes_a2 = construir_opcoes_selectbox(ANEXO_II, default_text=OPCAO_NAO_ESCOLHEU, incluir_vazio=True)
    escolha_a2_default = 0
    if inscricao_existente and inscricao_existente.get("escolha_anexo2"):
        escolha_a2_default = encontrar_indice_opcao(opcoes_a2, inscricao_existente["escolha_anexo2"])

    escolha_a2 = st.selectbox("2ª Escolha - Anexo II (Todas as Unidades Judiciárias):", opcoes_a2,
                               index=escolha_a2_default,
                               help="Mais de 300 unidades judiciárias.")

    st.divider()
    st.markdown("**Relotação nos últimos 2 anos (Item 3.3):**")

    relotado_existente = (inscricao_existente or {}).get("relotado_menos_2_anos", "N")
    relotado_idx = 1 if str(relotado_existente).upper() == "S" else 0

    relotado_opcao = st.radio(
        "Você foi relotado(a) **a pedido** nos últimos 2 anos (após 10/02/2024)?",
        ["Não", "Sim"],
        index=relotado_idx,
        help=(
            "Item 3.3 do Edital: servidores relotados a pedido após 10/02/2024 "
            "podem ser desclassificados, exceto se todos os concorrentes da unidade "
            "estiverem na mesma situação (item 3.3.1)."
        )
    )

    data_rel = None
    if relotado_opcao == "Sim":
        data_rel_existente = None
        if inscricao_existente and inscricao_existente.get("data_ultima_relotacao"):
            try:
                data_rel_existente = datetime.strptime(
                    inscricao_existente["data_ultima_relotacao"], "%d/%m/%Y"
                ).date()
            except (ValueError, TypeError):
                pass
        data_rel = st.date_input(
            "Data da última relotação a pedido:",
            value=data_rel_existente if data_rel_existente else date(2024, 2, 10),
            min_value=date(2024, 2, 10),
            max_value=date(2026, 2, 10),
            format="DD/MM/YYYY",
            help="Deve estar entre 10/02/2024 e 10/02/2026."
        )

    codigo_lotacao_temp = extrair_codigo_da_opcao(lotacao_atual, default_vazio="")
    codigo_escolha_a2_temp = extrair_codigo_da_opcao(escolha_a2, default_vazio=OPCAO_NAO_ESCOLHEU)

    if codigo_lotacao_temp and codigo_escolha_a2_temp and codigo_lotacao_temp == codigo_escolha_a2_temp:
        alert_box("CONFLITO: Você escolheu a mesma unidade como origem e destino no Anexo II.", alert_type="error")

    st.divider()
    st.markdown("**Resumo da Inscrição:**")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown(f"**Nome:** {nome if nome else '-'}")
        st.markdown(f"**Matrícula:** {matricula if matricula else '-'}")
        st.markdown(f"**Data Admissão:** {data_admissao.strftime('%d/%m/%Y') if data_admissao else '-'}")
        st.markdown(f"**Relotado < 2 anos:** {'Sim' if relotado_opcao == 'Sim' else 'Não'}")
    with col_r2:
        lotacao_resumo = lotacao_atual.split(" - ", 1)[1] if lotacao_atual and " - " in lotacao_atual else "-"
        escolha_a1_resumo = escolha_a1.split(" - ", 1)[1] if escolha_a1 != OPCAO_NAO_ESCOLHEU and " - " in escolha_a1 else "-"
        escolha_a2_resumo = escolha_a2.split(" - ", 1)[1] if escolha_a2 != OPCAO_NAO_ESCOLHEU and " - " in escolha_a2 else "-"
        st.markdown(f"**Origem:** {lotacao_resumo[:50]}..." if len(lotacao_resumo) > 50 else f"**Origem:** {lotacao_resumo}")
        st.markdown(f"**1ª Opção (Anexo I):** {escolha_a1_resumo[:50]}..." if len(escolha_a1_resumo) > 50 else f"**1ª Opção (Anexo I):** {escolha_a1_resumo}")
        st.markdown(f"**2ª Opção (Anexo II):** {escolha_a2_resumo[:50]}..." if len(escolha_a2_resumo) > 50 else f"**2ª Opção (Anexo II):** {escolha_a2_resumo}")

    submitted = st.form_submit_button("Salvar Inscrição", use_container_width=True)

    if submitted:
        if codigo_lotacao_temp and codigo_escolha_a2_temp and codigo_lotacao_temp == codigo_escolha_a2_temp:
            st.error("Não é possível salvar: origem e destino são iguais!")
        elif not nome or not matricula or not data_admissao or not lotacao_atual:
            st.error("Preencha todos os campos obrigatórios!")
        elif not posicao_lista or posicao_lista < 1 or posicao_lista > 1291:
            st.error("**Posição inválida!** Informe uma posição entre 1 e 1291.")
        elif posicao_lista not in LISTA_CLASSIFICATORIA:
            st.error(f"**Posição {posicao_lista} não encontrada na Lista Classificatória!** Verifique a posição correta.")
        elif relotado_opcao == "Sim" and not data_rel:
            st.error("Informe a data da última relotação a pedido.")
        else:
            codigo_lotacao = extrair_codigo_da_opcao(lotacao_atual, default_vazio="")
            codigo_escolha_a1 = extrair_codigo_da_opcao(escolha_a1, default_vazio=OPCAO_NAO_ESCOLHEU)
            codigo_escolha_a2 = extrair_codigo_da_opcao(escolha_a2, default_vazio=OPCAO_NAO_ESCOLHEU)

            dados = {
                "nome": nome,
                "matricula": matricula,
                "data_admissao": data_admissao.strftime("%d/%m/%Y"),
                "lotacao_atual": codigo_lotacao,
                "escolha_anexo1": codigo_escolha_a1,
                "escolha_anexo2": codigo_escolha_a2,
                "data_inscricao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "posicao_lista_classificatoria": posicao_lista,
                "relotado_menos_2_anos": "S" if relotado_opcao == "Sim" else "N",
                "data_ultima_relotacao": data_rel.strftime("%d/%m/%Y") if data_rel else "",
            }

            if salvar_inscricao(sheet, dados):
                handle_success("Inscrição salva com sucesso!", show_balloons=True)
                invalidar_cache()
                st.rerun()

# ---- Excluir inscrição (dentro de form para evitar rerun ao digitar) ----
st.subheader("Excluir Inscrição")

with st.form("form_excluir"):
    matricula_excluir = st.text_input("Matrícula para excluir:", key="mat_excluir")
    btn_excluir = st.form_submit_button("Excluir Inscrição")

    if btn_excluir:
        if matricula_excluir:
            inscricao = buscar_inscricao(sheet, matricula_excluir)
            if inscricao:
                sucesso, nome_exc = excluir_inscricao(sheet, matricula_excluir)
                if sucesso:
                    st.success(f"Inscrição de {inscricao['nome']} excluída!")
                    invalidar_cache()
                    st.rerun()
            else:
                st.error("Matrícula não encontrada!")
        else:
            st.error("Informe a matrícula!")

st.divider()
st.info("Dúvidas sobre regras, inscrição ou resultado? Consulte a página **Como Usar**.")

footer()
