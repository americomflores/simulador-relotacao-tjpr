"""
Simulador de Relotação - TJPR
Edital nº 4/2025 - Técnico Judiciário
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from data import ANEXO_I, ANEXO_II
import gspread
from google.oauth2.service_account import Credentials
import json

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

st.set_page_config(
    page_title="Simulador Relotação TJPR",
    page_icon="⚖️",
    layout="wide"
)

# Data limite para estágio probatório (3 anos antes de 26/11/2025)
DATA_LIMITE_ESTAGIO = date(2022, 11, 26)

# =============================================================================
# CONEXÃO GOOGLE SHEETS
# =============================================================================

@st.cache_resource
def conectar_sheets():
    """Conecta ao Google Sheets usando credenciais do secrets"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Credenciais do Streamlit Secrets
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Abre a planilha (criar manualmente no Google Sheets e compartilhar com o service account)
        spreadsheet = client.open(st.secrets["spreadsheet_name"])
        return spreadsheet.sheet1
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        return None


def carregar_inscricoes(sheet):
    """Carrega todas as inscrições do Google Sheets"""
    if sheet is None:
        return pd.DataFrame(columns=["nome", "matricula", "data_admissao", "lotacao_atual", "escolha_anexo1", "escolha_anexo2", "data_inscricao"])
    
    try:
        dados = sheet.get_all_records()
        if not dados:
            return pd.DataFrame(columns=["nome", "matricula", "data_admissao", "lotacao_atual", "escolha_anexo1", "escolha_anexo2", "data_inscricao"])
        
        df = pd.DataFrame(dados)
        # Converter data de admissão
        df["data_admissao"] = pd.to_datetime(df["data_admissao"], format="%d/%m/%Y", errors="coerce").dt.date
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(columns=["nome", "matricula", "data_admissao", "lotacao_atual", "escolha_anexo1", "escolha_anexo2", "data_inscricao"])


def salvar_inscricao(sheet, dados):
    """Salva ou atualiza uma inscrição"""
    if sheet is None:
        st.error("Conexão com Google Sheets não disponível")
        return False
    
    try:
        # Busca se já existe inscrição com essa matrícula
        registros = sheet.get_all_records()
        linha_existente = None
        
        for i, reg in enumerate(registros, start=2):  # Linha 1 é cabeçalho
            if str(reg.get("matricula", "")) == str(dados["matricula"]):
                linha_existente = i
                break
        
        valores = [
            dados["nome"],
            dados["matricula"],
            dados["data_admissao"],
            dados["lotacao_atual"],
            dados["escolha_anexo1"],
            dados["escolha_anexo2"],
            dados["data_inscricao"]
        ]
        
        if linha_existente:
            # Atualiza registro existente
            sheet.update(f"A{linha_existente}:G{linha_existente}", [valores])
        else:
            # Adiciona novo registro
            sheet.append_row(valores)
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False


def excluir_inscricao(sheet, matricula):
    """Exclui uma inscrição pela matrícula"""
    if sheet is None:
        return False
    
    try:
        registros = sheet.get_all_records()
        for i, reg in enumerate(registros, start=2):
            if str(reg.get("matricula", "")) == str(matricula):
                sheet.delete_rows(i)
                return True
        return False
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")
        return False


def buscar_inscricao(sheet, matricula):
    """Busca inscrição por matrícula"""
    if sheet is None:
        return None
    
    try:
        registros = sheet.get_all_records()
        for reg in registros:
            if str(reg.get("matricula", "")) == str(matricula):
                return reg
        return None
    except:
        return None


# =============================================================================
# LÓGICA DE SIMULAÇÃO
# =============================================================================

def verificar_estagio_probatorio(data_admissao):
    """Verifica se servidor está em estágio probatório"""
    if data_admissao is None:
        return True
    return data_admissao > DATA_LIMITE_ESTAGIO


def calcular_resultado(df_inscricoes):
    """
    Calcula o resultado da simulação seguindo a lógica:
    1. Ordenar por antiguidade (data_admissao mais antiga primeiro)
    2. Marcar desclassificados por estágio probatório
    3. Processar Anexo I primeiro
    4. Processar Anexo II com vagas liberadas
    """
    if df_inscricoes.empty:
        return pd.DataFrame(), {}, {}
    
    # Criar cópia e ordenar por antiguidade
    df = df_inscricoes.copy()
    df = df.sort_values("data_admissao", ascending=True).reset_index(drop=True)
    
    # Inicializar colunas de resultado
    df["posicao_antiguidade"] = range(1, len(df) + 1)
    df["status"] = ""
    df["resultado"] = ""
    df["vaga_obtida"] = ""
    df["observacao"] = ""
    
    # Marcar desclassificados
    for idx, row in df.iterrows():
        if verificar_estagio_probatorio(row["data_admissao"]):
            df.at[idx, "status"] = "DESCLASSIFICADO"
            df.at[idx, "resultado"] = "Estágio Probatório"
            df.at[idx, "observacao"] = f"Admitido após {DATA_LIMITE_ESTAGIO.strftime('%d/%m/%Y')}"
    
    # Criar dicionário de vagas do Anexo I (código -> vagas restantes)
    vagas_anexo1 = {}
    for codigo, info in ANEXO_I.items():
        vagas_anexo1[codigo] = info["quantidade"]
    
    # Criar dicionário de vagas do Anexo II (começa vazio, preenchido conforme pessoas saem)
    vagas_anexo2 = {}  # codigo -> quantidade disponível
    
    # Processar cada servidor em ordem de antiguidade
    servidores_para_anexo2 = []  # Lista de quem vai tentar o Anexo II
    
    # FASE 1: Processar Anexo I
    for idx, row in df.iterrows():
        if df.at[idx, "status"] == "DESCLASSIFICADO":
            continue
        
        escolha_a1 = row["escolha_anexo1"]
        
        if escolha_a1 and escolha_a1 in vagas_anexo1:
            if vagas_anexo1[escolha_a1] > 0:
                # Conseguiu vaga no Anexo I!
                vagas_anexo1[escolha_a1] -= 1
                df.at[idx, "status"] = "APROVADO"
                df.at[idx, "resultado"] = "ANEXO I"
                df.at[idx, "vaga_obtida"] = f"{ANEXO_I[escolha_a1]['comarca']} - {ANEXO_I[escolha_a1]['unidade']}"
                
                # Libera vaga na lotação atual para o Anexo II
                lotacao = row["lotacao_atual"]
                if lotacao:
                    if lotacao in vagas_anexo2:
                        vagas_anexo2[lotacao] += 1
                    else:
                        vagas_anexo2[lotacao] = 1
            else:
                # Não conseguiu no Anexo I, vai tentar Anexo II
                servidores_para_anexo2.append(idx)
        elif escolha_a1:
            # Código inválido
            df.at[idx, "observacao"] = "Código Anexo I inválido"
            servidores_para_anexo2.append(idx)
        else:
            # Não escolheu Anexo I
            servidores_para_anexo2.append(idx)
    
    # FASE 2: Processar Anexo II
    for idx in servidores_para_anexo2:
        row = df.loc[idx]
        escolha_a2 = row["escolha_anexo2"]
        
        if escolha_a2 and escolha_a2 in vagas_anexo2:
            if vagas_anexo2[escolha_a2] > 0:
                # Conseguiu vaga no Anexo II!
                vagas_anexo2[escolha_a2] -= 1
                df.at[idx, "status"] = "APROVADO"
                df.at[idx, "resultado"] = "ANEXO II"
                df.at[idx, "vaga_obtida"] = f"{ANEXO_II[escolha_a2]['comarca']} - {ANEXO_II[escolha_a2]['unidade']}"
                
                # Também libera vaga na lotação atual
                lotacao = row["lotacao_atual"]
                if lotacao and lotacao != escolha_a2:
                    if lotacao in vagas_anexo2:
                        vagas_anexo2[lotacao] += 1
                    else:
                        vagas_anexo2[lotacao] = 1
            else:
                df.at[idx, "status"] = "NÃO OBTEVE VAGA"
                df.at[idx, "resultado"] = "Sem vaga"
                df.at[idx, "observacao"] = "Vaga do Anexo II não disponível"
        elif escolha_a2 and escolha_a2 in ANEXO_II:
            # Código válido mas vaga ainda não foi liberada
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"
            df.at[idx, "resultado"] = "Sem vaga"
            df.at[idx, "observacao"] = "Vaga do Anexo II não foi liberada"
        elif escolha_a2:
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"
            df.at[idx, "resultado"] = "Sem vaga"
            df.at[idx, "observacao"] = "Código Anexo II inválido"
        else:
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"
            df.at[idx, "resultado"] = "Sem vaga"
            df.at[idx, "observacao"] = "Não escolheu Anexo II"
    
    return df, vagas_anexo1, vagas_anexo2


# =============================================================================
# INTERFACE
# =============================================================================

def main():
    st.title("⚖️ Simulador de Relotação - TJPR")
    st.caption("Edital nº 4/2025 - Técnico Judiciário")
    
    # Conectar ao Google Sheets
    sheet = conectar_sheets()
    
    # Carregar inscrições
    df_inscricoes = carregar_inscricoes(sheet)
    
    # Criar abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Vagas Anexo I", 
        "📋 Vagas Anexo II", 
        "✍️ Inscrição",
        "👥 Servidores Inscritos", 
        "🏆 Resultado"
    ])
    
    # =========================================================================
    # ABA 1: VAGAS ANEXO I
    # =========================================================================
    with tab1:
        st.header("Vagas com Déficit (Anexo I)")
        st.info("Estas são as vagas prioritárias com déficit de servidores. A quantidade indica o número de posições disponíveis.")
        
        # Criar DataFrame para exibição
        dados_a1 = []
        for codigo, info in ANEXO_I.items():
            dados_a1.append({
                "Código": codigo,
                "Comarca": info["comarca"],
                "Unidade Judiciária": info["unidade"],
                "Vagas": info["quantidade"]
            })
        
        df_a1 = pd.DataFrame(dados_a1)
        
        # Filtro por comarca
        comarcas_a1 = sorted(df_a1["Comarca"].unique())
        filtro_comarca_a1 = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_a1, key="filtro_a1")
        
        if filtro_comarca_a1 != "Todas":
            df_a1 = df_a1[df_a1["Comarca"] == filtro_comarca_a1]
        
        # Busca por texto
        busca_a1 = st.text_input("🔍 Buscar:", key="busca_a1", placeholder="Digite parte do nome da comarca ou unidade...")
        if busca_a1:
            mask = df_a1.apply(lambda x: busca_a1.lower() in x["Comarca"].lower() or busca_a1.lower() in x["Unidade Judiciária"].lower(), axis=1)
            df_a1 = df_a1[mask]
        
        st.dataframe(df_a1, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df_a1)} unidades | {df_a1['Vagas'].sum()} vagas")
    
    # =========================================================================
    # ABA 2: VAGAS ANEXO II
    # =========================================================================
    with tab2:
        st.header("Todas as Unidades (Anexo II)")
        st.info("Estas são todas as unidades judiciárias. As vagas só ficam disponíveis quando um servidor sai para o Anexo I.")
        
        # Criar DataFrame para exibição
        dados_a2 = []
        for codigo, info in ANEXO_II.items():
            dados_a2.append({
                "Código": codigo,
                "Comarca": info["comarca"],
                "Unidade Judiciária": info["unidade"]
            })
        
        df_a2 = pd.DataFrame(dados_a2)
        
        # Filtro por comarca
        comarcas_a2 = sorted(df_a2["Comarca"].unique())
        filtro_comarca_a2 = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_a2, key="filtro_a2")
        
        if filtro_comarca_a2 != "Todas":
            df_a2 = df_a2[df_a2["Comarca"] == filtro_comarca_a2]
        
        # Busca por texto
        busca_a2 = st.text_input("🔍 Buscar:", key="busca_a2", placeholder="Digite parte do nome da comarca ou unidade...")
        if busca_a2:
            mask = df_a2.apply(lambda x: busca_a2.lower() in x["Comarca"].lower() or busca_a2.lower() in x["Unidade Judiciária"].lower(), axis=1)
            df_a2 = df_a2[mask]
        
        st.dataframe(df_a2, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df_a2)} unidades")
    
    # =========================================================================
    # ABA 3: INSCRIÇÃO
    # =========================================================================
    with tab3:
        st.header("Inscrição / Edição")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Nova Inscrição ou Edição")
            
            # Verificar se está editando
            matricula_busca = st.text_input("Matrícula (para nova inscrição ou editar existente):", key="mat_busca")
            
            inscricao_existente = None
            if matricula_busca:
                inscricao_existente = buscar_inscricao(sheet, matricula_busca)
                if inscricao_existente:
                    st.info("✏️ Inscrição encontrada! Os dados serão carregados para edição.")
            
            with st.form("form_inscricao"):
                nome = st.text_input(
                    "Nome completo:", 
                    value=inscricao_existente.get("nome", "") if inscricao_existente else ""
                )
                
                matricula = st.text_input(
                    "Matrícula:", 
                    value=matricula_busca,
                    disabled=True if matricula_busca else False
                )
                
                # Data de admissão
                data_default = None
                if inscricao_existente and inscricao_existente.get("data_admissao"):
                    try:
                        data_default = datetime.strptime(inscricao_existente["data_admissao"], "%d/%m/%Y").date()
                    except:
                        pass
                
                data_admissao = st.date_input(
                    "Data de início do exercício:",
                    value=data_default,
                    min_value=date(1980, 1, 1),
                    max_value=date.today(),
                    format="DD/MM/YYYY"
                )
                
                # Verificar estágio probatório
                if data_admissao and data_admissao > DATA_LIMITE_ESTAGIO:
                    st.warning(f"⚠️ Servidor em ESTÁGIO PROBATÓRIO (admitido após {DATA_LIMITE_ESTAGIO.strftime('%d/%m/%Y')}). Será desclassificado conforme edital.")
                
                # Lotação atual (Anexo II)
                opcoes_lotacao = [""] + [f"{k} - {v['comarca']} - {v['unidade']}" for k, v in ANEXO_II.items()]
                
                lotacao_default = 0
                if inscricao_existente and inscricao_existente.get("lotacao_atual"):
                    codigo_lot = inscricao_existente["lotacao_atual"]
                    for i, op in enumerate(opcoes_lotacao):
                        if op.startswith(codigo_lot + " -"):
                            lotacao_default = i
                            break
                
                lotacao_atual = st.selectbox(
                    "Lotação atual (onde você trabalha):",
                    opcoes_lotacao,
                    index=lotacao_default
                )
                
                # Escolha Anexo I
                opcoes_a1 = ["(Não escolher)"] + [f"{k} - {v['comarca']} - {v['unidade']} ({v['quantidade']} vagas)" for k, v in ANEXO_I.items()]
                
                escolha_a1_default = 0
                if inscricao_existente and inscricao_existente.get("escolha_anexo1"):
                    codigo_a1 = inscricao_existente["escolha_anexo1"]
                    for i, op in enumerate(opcoes_a1):
                        if op.startswith(codigo_a1 + " -"):
                            escolha_a1_default = i
                            break
                
                escolha_a1 = st.selectbox(
                    "1ª Opção - Vaga com déficit (Anexo I):",
                    opcoes_a1,
                    index=escolha_a1_default
                )
                
                # Escolha Anexo II
                opcoes_a2 = ["(Não escolher)"] + [f"{k} - {v['comarca']} - {v['unidade']}" for k, v in ANEXO_II.items()]
                
                escolha_a2_default = 0
                if inscricao_existente and inscricao_existente.get("escolha_anexo2"):
                    codigo_a2 = inscricao_existente["escolha_anexo2"]
                    for i, op in enumerate(opcoes_a2):
                        if op.startswith(codigo_a2 + " -"):
                            escolha_a2_default = i
                            break
                
                escolha_a2 = st.selectbox(
                    "2ª Opção - Qualquer unidade (Anexo II):",
                    opcoes_a2,
                    index=escolha_a2_default
                )
                
                submitted = st.form_submit_button("💾 Salvar Inscrição", use_container_width=True)
                
                if submitted:
                    if not nome or not matricula or not data_admissao or not lotacao_atual:
                        st.error("Preencha todos os campos obrigatórios!")
                    else:
                        # Extrair códigos
                        codigo_lotacao = lotacao_atual.split(" - ")[0] if lotacao_atual else ""
                        codigo_escolha_a1 = escolha_a1.split(" - ")[0] if escolha_a1 != "(Não escolher)" else ""
                        codigo_escolha_a2 = escolha_a2.split(" - ")[0] if escolha_a2 != "(Não escolher)" else ""
                        
                        dados = {
                            "nome": nome,
                            "matricula": matricula,
                            "data_admissao": data_admissao.strftime("%d/%m/%Y"),
                            "lotacao_atual": codigo_lotacao,
                            "escolha_anexo1": codigo_escolha_a1,
                            "escolha_anexo2": codigo_escolha_a2,
                            "data_inscricao": datetime.now().strftime("%d/%m/%Y %H:%M")
                        }
                        
                        if salvar_inscricao(sheet, dados):
                            st.success("✅ Inscrição salva com sucesso!")
                            st.cache_resource.clear()
                            st.rerun()
        
        with col2:
            st.subheader("Excluir Inscrição")
            
            matricula_excluir = st.text_input("Matrícula para excluir:", key="mat_excluir")
            
            if st.button("🗑️ Excluir Inscrição", type="secondary"):
                if matricula_excluir:
                    inscricao = buscar_inscricao(sheet, matricula_excluir)
                    if inscricao:
                        if excluir_inscricao(sheet, matricula_excluir):
                            st.success(f"Inscrição de {inscricao['nome']} excluída!")
                            st.cache_resource.clear()
                            st.rerun()
                    else:
                        st.error("Matrícula não encontrada!")
                else:
                    st.error("Informe a matrícula!")
            
            st.divider()
            
            st.subheader("ℹ️ Informações")
            st.markdown("""
            **Regras do Edital:**
            - Servidores em **estágio probatório** (admitidos após 26/11/2022) serão desclassificados
            - Servidores relotados há menos de 2 anos também são desclassificados (verificar manualmente)
            - Critério de desempate: **antiguidade** (data de admissão mais antiga)
            
            **Como funciona:**
            1. Primeiro são analisadas as escolhas do **Anexo I** (vagas deficitárias)
            2. Quem consegue vaga no Anexo I, libera sua lotação atual
            3. As vagas liberadas ficam disponíveis para o **Anexo II**
            4. O mais antigo sempre tem prioridade
            """)
    
    # =========================================================================
    # ABA 4: SERVIDORES INSCRITOS
    # =========================================================================
    with tab4:
        st.header("Servidores Inscritos")
        
        if df_inscricoes.empty:
            st.info("Nenhum servidor inscrito ainda.")
        else:
            # Recarregar dados frescos
            df_inscricoes = carregar_inscricoes(sheet)
            
            # Ordenar por antiguidade
            df_display = df_inscricoes.sort_values("data_admissao", ascending=True).reset_index(drop=True)
            df_display["posicao"] = range(1, len(df_display) + 1)
            
            # Formatar para exibição
            df_display["data_admissao_fmt"] = df_display["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if x else ""
            )
            
            # Marcar estágio probatório
            df_display["estagio_probatorio"] = df_display["data_admissao"].apply(
                lambda x: "⚠️ SIM" if x and x > DATA_LIMITE_ESTAGIO else "Não"
            )
            
            # Adicionar descrições das escolhas
            df_display["lotacao_desc"] = df_display["lotacao_atual"].apply(
                lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x in ANEXO_II else x
            )
            df_display["escolha_a1_desc"] = df_display["escolha_anexo1"].apply(
                lambda x: f"{ANEXO_I[x]['comarca']} - {ANEXO_I[x]['unidade']}" if x and x in ANEXO_I else "-"
            )
            df_display["escolha_a2_desc"] = df_display["escolha_anexo2"].apply(
                lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
            )
            
            st.dataframe(
                df_display[[
                    "posicao", "nome", "matricula", "data_admissao_fmt", 
                    "estagio_probatorio", "lotacao_desc", "escolha_a1_desc", "escolha_a2_desc"
                ]].rename(columns={
                    "posicao": "Pos.",
                    "nome": "Nome",
                    "matricula": "Matrícula",
                    "data_admissao_fmt": "Data Admissão",
                    "estagio_probatorio": "Est. Probatório",
                    "lotacao_desc": "Lotação Atual",
                    "escolha_a1_desc": "Escolha Anexo I",
                    "escolha_a2_desc": "Escolha Anexo II"
                }),
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Total: {len(df_display)} servidores inscritos")
    
    # =========================================================================
    # ABA 5: RESULTADO
    # =========================================================================
    with tab5:
        st.header("Resultado da Simulação")
        
        if df_inscricoes.empty:
            st.info("Nenhum servidor inscrito ainda. O resultado aparecerá quando houver inscrições.")
        else:
            # Recalcular resultado
            df_resultado, vagas_restantes_a1, vagas_disponiveis_a2 = calcular_resultado(df_inscricoes)
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(df_resultado)
            aprovados_a1 = len(df_resultado[df_resultado["resultado"] == "ANEXO I"])
            aprovados_a2 = len(df_resultado[df_resultado["resultado"] == "ANEXO II"])
            desclass = len(df_resultado[df_resultado["status"] == "DESCLASSIFICADO"])
            sem_vaga = len(df_resultado[df_resultado["resultado"] == "Sem vaga"])
            
            col1.metric("Total Inscritos", total)
            col2.metric("Aprovados Anexo I", aprovados_a1, delta=None)
            col3.metric("Aprovados Anexo II", aprovados_a2, delta=None)
            col4.metric("Desclassificados", desclass, delta=None, delta_color="inverse")
            
            st.divider()
            
            # Tabela de resultado
            st.subheader("📊 Resultado por Ordem de Antiguidade")
            
            # Formatar para exibição
            df_resultado["data_admissao_fmt"] = df_resultado["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if x else ""
            )
            
            # Preparar DataFrame para exibição (renomear ANTES de aplicar estilo)
            df_exibir = df_resultado[[
                "posicao_antiguidade", "nome", "matricula", "data_admissao_fmt",
                "status", "resultado", "vaga_obtida", "observacao"
            ]].rename(columns={
                "posicao_antiguidade": "Pos.",
                "nome": "Nome",
                "matricula": "Matrícula",
                "data_admissao_fmt": "Data Admissão",
                "status": "Status",
                "resultado": "Resultado",
                "vaga_obtida": "Vaga Obtida",
                "observacao": "Observação"
            })
            
            # Função para colorir status (usando nomes das colunas APÓS rename)
            def highlight_status(row):
                if row["Status"] == "APROVADO":
                    return ["background-color: #d4edda"] * len(row)
                elif row["Status"] == "DESCLASSIFICADO":
                    return ["background-color: #f8d7da"] * len(row)
                elif row["Status"] == "NÃO OBTEVE VAGA":
                    return ["background-color: #fff3cd"] * len(row)
                return [""] * len(row)
            
            st.dataframe(
                df_exibir.style.apply(highlight_status, axis=1),
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            
            # Vagas restantes
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Vagas Restantes - Anexo I")
                vagas_rest = []
                for codigo, qtd in vagas_restantes_a1.items():
                    if qtd > 0:
                        vagas_rest.append({
                            "Código": codigo,
                            "Comarca": ANEXO_I[codigo]["comarca"],
                            "Unidade": ANEXO_I[codigo]["unidade"],
                            "Restantes": qtd
                        })
                
                if vagas_rest:
                    st.dataframe(pd.DataFrame(vagas_rest), use_container_width=True, hide_index=True)
                else:
                    st.success("Todas as vagas do Anexo I foram preenchidas!")
            
            with col2:
                st.subheader("📋 Vagas Disponíveis - Anexo II")
                vagas_disp = []
                for codigo, qtd in vagas_disponiveis_a2.items():
                    if qtd > 0 and codigo in ANEXO_II:
                        vagas_disp.append({
                            "Código": codigo,
                            "Comarca": ANEXO_II[codigo]["comarca"],
                            "Unidade": ANEXO_II[codigo]["unidade"],
                            "Disponíveis": qtd
                        })
                
                if vagas_disp:
                    st.dataframe(pd.DataFrame(vagas_disp), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma vaga liberada no Anexo II ainda.")


# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.caption("""
⚠️ **ATENÇÃO:** Este é um simulador não oficial, criado apenas para auxiliar na tomada de decisão. 
O resultado oficial depende exclusivamente da análise do TJPR conforme Edital nº 4/2025.
""")


if __name__ == "__main__":
    main()
