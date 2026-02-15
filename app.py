"""
Simulador de Relotação - TJPR
Edital nº 01/2026 - Técnico Judiciário
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from data import ANEXO_I, ANEXO_II
from lotacao_data import LOTACAO_POR_CODIGO, LOTACAO_COMPLETA
from lista_classificatoria import LISTA_CLASSIFICATORIA
from config.matricula_posicao_map import MATRICULA_POSICAO_MAP
from config.constants import (
    FUZZY_MATCH_HIGH,
    FUZZY_MATCH_MEDIUM,
    LISTA_SIZE,
    LISTA_MIN_POSICAO,
    LISTA_MAX_POSICAO,
    NOME_MIN_LENGTH,
    STATUS_APROVADO,
    STATUS_DESCLASSIFICADO,
    STATUS_NAO_OBTEVE,
    OPCAO_NAO_ESCOLHEU
)
from services.simulacao_service import (
    obter_status_lotacao,
    obter_dados_lotacao,
    calcular_lotacao_dinamica
    # verificar_estagio_probatorio removido - Edital 01/2026 permite servidores em estágio probatório
)
from utils.ui_helpers import (
    construir_opcoes_selectbox,
    extrair_codigo_da_opcao,
    formatar_codigo_para_exibicao,
    encontrar_indice_opcao,
    extrair_comarca_da_string
)
from config.rajs_config import RAJS
from services.rajs_service import (
    obter_raj_da_comarca,
    obter_numero_raj,
    obter_comarcas_da_raj,
    obter_sede_da_raj,
    listar_todas_rajs,
    contar_servidores_por_raj
)
from services.search_service import (
    buscar_servidor_por_nome,
    buscar_servidor_por_matricula,
    buscar_servidor_por_posicao,
    determinar_qualidade_match
)
from services.export_service import (
    gerar_excel_resultado,
    gerar_excel_inscricoes,
    gerar_excel_logs,
    gerar_excel_comparacao,
    gerar_excel_vagas_disponiveis
)
from utils.error_handlers import (
    handle_error,
    handle_success,
    handle_warning,
    handle_info,
    safe_execute
)
from utils.ui_components import (
    card,
    info_card,
    badge,
    alert_box,
    progress_bar,
    status_badge_for_resultado,
    metric_card,
    styled_dataframe,
    section_header,
    loading_spinner,
    empty_state,
    divider_with_text
)
import gspread
from google.oauth2.service_account import Credentials
import json
import re
from io import BytesIO
import unicodedata
from fuzzywuzzy import fuzz

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

st.set_page_config(
    page_title="Simulador Relotação TJPR",
    page_icon="⚖️",
    layout="wide"
)

# CSS para melhorar responsividade em dispositivos móveis
st.markdown("""
<style>
/* Ajustes para telas menores */
@media (max-width: 768px) {
    /* Reduzir padding das colunas */
    .stColumn {
        padding: 0 5px !important;
    }
    
    /* Reduzir tamanho das métricas */
    [data-testid="metric-container"] {
        padding: 10px 5px !important;
    }
    
    /* Ajustar tamanho da fonte dos títulos */
    h1 {
        font-size: 1.5rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
    }
    h3 {
        font-size: 1rem !important;
    }
    
    /* Ajustar tabelas para scroll horizontal */
    .stDataFrame {
        overflow-x: auto !important;
    }
    
    /* Reduzir espaçamento das tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 5px 8px;
        font-size: 12px;
    }
}

/* Melhorar visualização das tabs em geral */
.stTabs [data-baseweb="tab-list"] {
    flex-wrap: wrap;
}

/* Cards de RAJ */
.raj-box {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin: 5px 0;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Edital 01/2026: Não há mais restrição de estágio probatório
# Servidores em estágio probatório PODEM participar da relotação
# (DATA_LIMITE_ESTAGIO removido)


# =============================================================================
# REGIÕES ADMINISTRATIVAS JUDICIÁRIAS (RAJs)
# =============================================================================

def normalizar_comarca(nome):
    """
    Normaliza nome de comarca para comparação consistente.

    Remove espaços extras, converte para title case e aplica correções ortográficas
    específicas para comarcas do Paraná (acentuação, preposições, etc).

    Args:
        nome: Nome da comarca a ser normalizado

    Returns:
        Nome normalizado com acentuação e capitalização corretas

    Example:
        >>> normalizar_comarca("foz do iguacu")
        'Foz do Iguaçu'
        >>> normalizar_comarca("SAO JOSE  DOS  PINHAIS")
        'São José dos Pinhais'
    """
    if not nome:
        return ""
    nome = " ".join(nome.split()).title()
    correcoes = {
        "Bocaiuva Do Sul": "Bocaiúva do Sul",
        "Candido De Abreu": "Cândido de Abreu",
        "Pirai Do Sul": "Piraí do Sul",
        "Sao Joao Do Triunfo": "São João do Triunfo",
        "Sao Mateus Do Sul": "São Mateus do Sul",
        "Telemaco Borba": "Telêmaco Borba",
        "Uniao Da Vitoria": "União da Vitória",
        "Laranjeiras Do Sul": "Laranjeiras do Sul",
        "Santo Antonio Do Sudoeste": "Santo Antônio do Sudoeste",
        "Sao Joao": "São João",
        "Foz Do Iguacu": "Foz do Iguaçu",
        "Foz Do Iguaçu": "Foz do Iguaçu",
        "Sao Miguel Do Iguacu": "São Miguel do Iguaçu",
        "Sao Miguel Do Iguaçu": "São Miguel do Iguaçu",
        "Capitao Leonidas Marques": "Capitão Leônidas Marques",
        "Marechal Candido Rondon": "Marechal Cândido Rondon",
        "Quedas Do Iguacu": "Quedas do Iguaçu",
        "Quedas Do Iguaçu": "Quedas do Iguaçu",
        "Altonia": "Altônia",
        "Goioere": "Goioerê",
        "Guaira": "Guaíra",
        "Ipora": "Iporã",
        "Paraiso Do Norte": "Paraíso do Norte",
        "Perola": "Pérola",
        "Santa Isabel Do Ivai": "Santa Isabel do Ivaí",
        "Santa Isabel Do Ivaí": "Santa Isabel do Ivaí",
        "Centenario Do Sul": "Centenário do Sul",
        "Jandaia Do Sul": "Jandaia do Sul",
        "Mandaguacu": "Mandaguaçu",
        "Sao Joao Do Ivai": "São João do Ivaí",
        "Sao Joao Do Ivaí": "São João do Ivaí",
        "Marilandia Do Sul": "Marilândia do Sul",
        "Sao Jeronimo Da Serra": "São Jerônimo da Serra",
        "Urai": "Uraí",
        "Ibipora": "Ibiporã",
        "Rolandia": "Rolândia",
        "Joaquim Tavora": "Joaquim Távora",
        "Ribeirao Claro": "Ribeirão Claro",
        "Ribeirao Do Pinhal": "Ribeirão do Pinhal",
        "Santo Antonio Da Platina": "Santo Antônio da Platina",
        "Ampere": "Ampére",
        "Clevelandia": "Clevelândia",
        "Ivaipora": "Ivaiporã",
        "Guaraniacu": "Guaraniaçu",
        "Mambore": "Mamborê",
        "Ubirata": "Ubiratã",
        "Sao Jose Dos Pinhais": "São José dos Pinhais",
        "Campina Grande Do Sul": "Campina Grande do Sul",
        "Fazenda Rio Grande": "Fazenda Rio Grande",
        "Rio Branco Do Sul": "Rio Branco do Sul",
        "Almirante Tamandare": "Almirante Tamandaré",
        "Paranagua": "Paranaguá",
    }
    
    for errado, correto in correcoes.items():
        if nome.lower() == errado.lower():
            return correto
    
    return nome




# =============================================================================
# BUSCA NA LISTA CLASSIFICATÓRIA
# =============================================================================



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
        
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open(st.secrets["spreadsheet_name"])
        sheet = spreadsheet.sheet1
        
        # Verificar e adicionar cabeçalhos de log se necessário
        verificar_cabecalhos_log(sheet)
        
        return sheet
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        return None


def verificar_cabecalhos_log(sheet):
    """Verifica se os cabeçalhos de log existem e adiciona se necessário"""
    try:
        # Pegar primeira linha (cabeçalhos)
        cabecalhos = sheet.row_values(1)
        
        # Cabeçalhos esperados
        cabecalhos_necessarios = ["nome", "matricula", "data_admissao", "lotacao_atual", 
                                   "escolha_anexo1", "escolha_anexo2", "data_inscricao",
                                   "registrado_por", "alterado_por", "data_alteracao"]
        
        # Se planilha vazia, criar todos os cabeçalhos
        if not cabecalhos:
            sheet.update('A1:J1', [cabecalhos_necessarios])
            return
        
        # Verificar se cabeçalhos de log existem (colunas H, I, J)
        cabecalhos_log = ["registrado_por", "alterado_por", "data_alteracao"]
        
        for i, cab in enumerate(cabecalhos_log):
            col_idx = 7 + i  # H=7, I=8, J=9 (0-indexed)
            if len(cabecalhos) <= col_idx or cabecalhos[col_idx] != cab:
                # Adicionar cabeçalho na posição correta
                col_letra = chr(ord('H') + i)  # H, I, J
                sheet.update(f'{col_letra}1', [[cab]])
    except Exception as e:
        # Não falhar silenciosamente, mas também não travar o app
        pass


def carregar_inscricoes(sheet):
    """Carrega todas as inscrições do Google Sheets"""
    colunas_base = ["nome", "matricula", "data_admissao", "lotacao_atual", "escolha_anexo1", "escolha_anexo2", "data_inscricao"]
    colunas_log = ["registrado_por", "alterado_por", "data_alteracao"]
    todas_colunas = colunas_base + colunas_log
    
    if sheet is None:
        return pd.DataFrame(columns=todas_colunas)
    
    try:
        dados = sheet.get_all_records()
        if not dados:
            return pd.DataFrame(columns=todas_colunas)
        
        df = pd.DataFrame(dados)
        df["data_admissao"] = pd.to_datetime(df["data_admissao"], format="%d/%m/%Y", errors="coerce").dt.date
        
        # Garantir que colunas de log existam (para compatibilidade com dados antigos)
        for col in colunas_log:
            if col not in df.columns:
                df[col] = ""
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(columns=todas_colunas)


def salvar_inscricao(sheet, dados):
    """Salva ou atualiza uma inscrição"""
    if sheet is None:
        st.error("Conexão com Google Sheets não disponível")
        return False

    try:
        registros = sheet.get_all_records()
        linha_existente = None
        registro_antigo = None

        for i, reg in enumerate(registros, start=2):
            if str(reg.get("matricula", "")) == str(dados["matricula"]):
                linha_existente = i
                registro_antigo = reg
                break

        # Registro público (sem autenticação)
        usuario_registro = "Público"
        data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

        if linha_existente and registro_antigo:
            # Atualização - manter registrado_por original, atualizar alterado_por
            registrado_por = registro_antigo.get("registrado_por", usuario_registro) or usuario_registro
            valores = [
                dados["nome"],
                dados["matricula"],
                dados["data_admissao"],
                dados["lotacao_atual"],
                dados["escolha_anexo1"],
                dados["escolha_anexo2"],
                dados["data_inscricao"],
                registrado_por,           # H: manter original
                usuario_registro,         # I: quem alterou
                data_hora_atual,          # J: quando alterou
                dados.get("posicao_lista_classificatoria", "")  # K: posição na lista classificatória
            ]
            sheet.update(f"A{linha_existente}:K{linha_existente}", [valores])
        else:
            # Nova inscrição
            valores = [
                dados["nome"],
                dados["matricula"],
                dados["data_admissao"],
                dados["lotacao_atual"],
                dados["escolha_anexo1"],
                dados["escolha_anexo2"],
                dados["data_inscricao"],
                usuario_registro,         # H: quem registrou
                usuario_registro,         # I: quem alterou (mesmo, pois é novo)
                data_hora_atual,          # J: quando
                dados.get("posicao_lista_classificatoria", "")  # K: posição na lista classificatória
            ]
            sheet.append_row(valores)

        return True
    except Exception as e:
        handle_error(e, "salvar_inscricao", show_to_user=True)
        return False


def excluir_inscricao(sheet, matricula):
    """Exclui uma inscrição pela matrícula, retornando info para log"""
    if sheet is None:
        return False, None

    try:
        registros = sheet.get_all_records()
        for i, reg in enumerate(registros, start=2):
            if str(reg.get("matricula", "")) == str(matricula):
                nome_excluido = reg.get("nome", "")
                sheet.delete_rows(i)
                return True, nome_excluido
        return False, None
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")
        return False, None


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
    except Exception as e:
        st.error(f"Erro ao buscar inscrição: {e}")
        return None


# =============================================================================
# LÓGICA DE SIMULAÇÃO COM LOTAÇÃO DINÂMICA
# =============================================================================

def calcular_resultado(df_inscricoes):
    """
    Calcula o resultado da simulação de relotação em duas fases.

    Implementa as regras do Edital 01/2026:
    - Fase 1: Processa Anexo I (vagas com déficit)
    - Fase 2: Processa Anexo II (todas as unidades)
    - Item 3.11: Prioriza escolha original do Anexo I se ambas disponíveis
    - Item 3.14: Calcula designação na origem se saída ocasionar déficit

    Utiliza lotação dinâmica: quando servidor sai de uma unidade, ela pode ficar
    disponível no Anexo II. A ordem de processamento é pela posição_lista_classificatoria
    (posição 1 = maior prioridade).

    Args:
        df_inscricoes: DataFrame com inscrições dos servidores.
            Colunas esperadas: nome, matricula, data_admissao, lotacao_atual,
            escolha_anexo1, escolha_anexo2, posicao_lista_classificatoria

    Returns:
        tuple: (df_resultado, vagas_anexo1, vagas_anexo2, ajustes_lotacao)
            - df_resultado: DataFrame com status de cada servidor (APROVADO/DESCLASSIFICADO/NÃO OBTEVE VAGA)
            - vagas_anexo1: dict com vagas restantes do Anexo I
            - vagas_anexo2: dict com vagas disponíveis do Anexo II
            - ajustes_lotacao: dict com ajustes acumulados por unidade

    Raises:
        ValueError: Se df_inscricoes não tiver colunas obrigatórias
    """
    if df_inscricoes.empty:
        return pd.DataFrame(), {}, {}, {}
    
    df = df_inscricoes.copy()

    # Garantir que posicao_lista_classificatoria está como Int64
    df["posicao_lista_classificatoria"] = pd.to_numeric(
        df["posicao_lista_classificatoria"],
        errors="coerce"
    ).astype("Int64")

    # Ordenar por posição na lista classificatória (posição 1 = maior prioridade)
    df = df.sort_values("posicao_lista_classificatoria", ascending=True, na_position='last').reset_index(drop=True)

    # Manter posicao_antiguidade para compatibilidade (agora reflete posição da lista)
    df["posicao_antiguidade"] = df["posicao_lista_classificatoria"]
    df["status"] = ""
    df["resultado"] = ""
    df["vaga_obtida"] = ""
    df["observacao"] = ""
    df["designacao_origem"] = ""
    df["status_origem_inicial"] = ""
    df["status_origem_final"] = ""
    
    # Criar mapeamento de Anexo I para Anexo II (mesma unidade, códigos diferentes)
    mapeamento_a1_para_a2 = {}
    for codigo_a1, info_a1 in ANEXO_I.items():
        comarca_a1 = info_a1['comarca'].strip().lower()
        unidade_a1 = info_a1['unidade'].strip().lower()
        
        for codigo_a2, info_a2 in ANEXO_II.items():
            comarca_a2 = info_a2['comarca'].strip().lower()
            unidade_a2 = info_a2['unidade'].strip().lower()
            
            if comarca_a1 == comarca_a2 and unidade_a1 == unidade_a2:
                mapeamento_a1_para_a2[codigo_a1] = codigo_a2
                break
    
    # Edital 01/2026: Servidores em estágio probatório PODEM participar
    # (Validação de estágio probatório removida)

    # Controle de vagas Anexo I
    vagas_anexo1 = {}
    for codigo, info in ANEXO_I.items():
        vagas_anexo1[codigo] = info["quantidade"]

    # Controle dinâmico de lotação das unidades
    # Começar com os valores originais e ajustar conforme movimentações
    ajustes_lotacao = {}  # codigo_unidade -> ajuste acumulado

    vagas_anexo2 = {}
    servidores_para_anexo2 = []
    
    # FASE 1: Processar Anexo I
    for idx, row in df.iterrows():
        if df.at[idx, "status"] == "DESCLASSIFICADO":
            continue
        
        escolha_a1 = row["escolha_anexo1"]
        lotacao_origem = row["lotacao_atual"]
        
        # Registrar status inicial da origem
        if lotacao_origem:
            dados_origem = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao.get(lotacao_origem, 0))
            if dados_origem:
                df.at[idx, "status_origem_inicial"] = dados_origem["status"]
        
        if escolha_a1 and escolha_a1 in vagas_anexo1:
            if vagas_anexo1[escolha_a1] > 0:
                vagas_anexo1[escolha_a1] -= 1
                df.at[idx, "status"] = "APROVADO"
                df.at[idx, "resultado"] = "Anexo I (vaga deficitária disponibilizada - item 2.1)"
                df.at[idx, "vaga_obtida"] = f"{ANEXO_I[escolha_a1]['comarca']} - {ANEXO_I[escolha_a1]['unidade']}"
                
                # Atualizar ajustes de lotação
                if lotacao_origem:
                    # Servidor sai da origem (-1)
                    ajustes_lotacao[lotacao_origem] = ajustes_lotacao.get(lotacao_origem, 0) - 1
                    
                    # Calcular status final da origem após saída
                    dados_origem_final = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao[lotacao_origem])
                    if dados_origem_final:
                        df.at[idx, "status_origem_final"] = dados_origem_final["status"]

                        # Determinar se precisa designação na origem
                        # Conforme item 3.16 do Edital: designação apenas se a saída OCASIONAR DÉFICIT
                        if dados_origem_final["status"] == "DEFICITÁRIA":
                            df.at[idx, "designacao_origem"] = "SIM"
                        else:
                            df.at[idx, "designacao_origem"] = "NÃO"

                        # NOVA REGRA: Liberar vaga no Anexo II APENAS se a origem ficar DEFICITÁRIA
                        # Isso permite que terceiros ocupem a vaga apenas quando há real necessidade de substituição
                        if dados_origem_final["status"] == "DEFICITÁRIA":
                            if lotacao_origem in vagas_anexo2:
                                vagas_anexo2[lotacao_origem] += 1
                            else:
                                vagas_anexo2[lotacao_origem] = 1
            else:
                servidores_para_anexo2.append(idx)
        elif escolha_a1:
            df.at[idx, "observacao"] = "Código Anexo I inválido"
            servidores_para_anexo2.append(idx)
        else:
            servidores_para_anexo2.append(idx)

    # FASE 2: Processar Anexo II
    # Conforme item 3.11: se possível deferimento em ambas as unidades (A1 e A2),
    # será concedido deferimento para a unidade originalmente indicada no Anexo I
    for idx in servidores_para_anexo2:
        row = df.loc[idx]
        escolha_a1 = row["escolha_anexo1"]  # Escolha original do Anexo I
        escolha_a2 = row["escolha_anexo2"]  # Escolha do Anexo II
        lotacao_origem = row["lotacao_atual"]
        
        # Registrar status inicial da origem (se ainda não registrado)
        if lotacao_origem and not df.at[idx, "status_origem_inicial"]:
            dados_origem = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao.get(lotacao_origem, 0))
            if dados_origem:
                df.at[idx, "status_origem_inicial"] = dados_origem["status"]
        
        # Mapear escolha A1 para código A2 (mesma unidade)
        codigo_a1_no_a2 = mapeamento_a1_para_a2.get(escolha_a1) if escolha_a1 else None
        
        # Verificar disponibilidade das vagas
        vaga_a1_disponivel = codigo_a1_no_a2 and codigo_a1_no_a2 in vagas_anexo2 and vagas_anexo2[codigo_a1_no_a2] > 0
        vaga_a2_disponivel = escolha_a2 and escolha_a2 in vagas_anexo2 and vagas_anexo2[escolha_a2] > 0
        
        # Determinar qual vaga conceder (prioridade para A1 conforme item 3.11)
        vaga_escolhida = None
        origem_vaga = None  # "A1" ou "A2"
        
        if vaga_a1_disponivel and vaga_a2_disponivel:
            # Ambas disponíveis: prioridade para A1 (item 3.11)
            vaga_escolhida = codigo_a1_no_a2
            origem_vaga = "ANEXO I (via A2)"
        elif vaga_a1_disponivel:
            # Apenas A1 disponível
            vaga_escolhida = codigo_a1_no_a2
            origem_vaga = "ANEXO I (via A2)"
        elif vaga_a2_disponivel:
            # Apenas A2 disponível
            vaga_escolhida = escolha_a2
            origem_vaga = "ANEXO II"
        
        if vaga_escolhida:
            vagas_anexo2[vaga_escolhida] -= 1

            # Atribuir resultado baseado no tipo de vaga
            if origem_vaga == "ANEXO I (via A2)":
                resultado_final = "Anexo I (vaga primária incluída na análise do Anexo II - item 3.13)"
            else:  # origem_vaga == "ANEXO II"
                resultado_final = "Anexo II (vaga de servidor a relotar - item 3.11)"

            df.at[idx, "status"] = "APROVADO"
            df.at[idx, "resultado"] = resultado_final
            df.at[idx, "vaga_obtida"] = f"{ANEXO_II[vaga_escolhida]['comarca']} - {ANEXO_II[vaga_escolhida]['unidade']}"
            
            # Atualizar ajustes de lotação
            if lotacao_origem and lotacao_origem != vaga_escolhida:
                # Servidor sai da origem (-1)
                ajustes_lotacao[lotacao_origem] = ajustes_lotacao.get(lotacao_origem, 0) - 1
                
                # Calcular status final da origem após saída
                dados_origem_final = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao[lotacao_origem])
                if dados_origem_final:
                    df.at[idx, "status_origem_final"] = dados_origem_final["status"]
                    
                    # Determinar se precisa designação na origem
                    # Conforme item 3.16 do Edital: designação apenas se a saída OCASIONAR DÉFICIT
                    if dados_origem_final["status"] == "DEFICITÁRIA":
                        df.at[idx, "designacao_origem"] = "SIM"
                    else:
                        df.at[idx, "designacao_origem"] = "NÃO"

                # Liberar vaga no Anexo II
                if lotacao_origem in vagas_anexo2:
                    vagas_anexo2[lotacao_origem] += 1
                else:
                    vagas_anexo2[lotacao_origem] = 1
            else:
                df.at[idx, "designacao_origem"] = "-"
        else:
            # Nenhuma vaga disponível
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"

            # Determinar motivo detalhado no resultado
            if escolha_a1 and escolha_a2:
                resultado_a1 = "Anexo I esgotado" if (escolha_a1 in ANEXO_I) else "Código Anexo I inválido"
                resultado_a2 = "Anexo II não liberado" if (escolha_a2 in ANEXO_II) else "Código Anexo II inválido"
                df.at[idx, "resultado"] = f"Sem vaga — {resultado_a1}; {resultado_a2}"
                df.at[idx, "observacao"] = "Vagas do Anexo I e II não disponíveis"
            elif escolha_a1:
                if escolha_a1 in ANEXO_I:
                    df.at[idx, "resultado"] = "Sem vaga — Anexo I esgotado e não liberado no Anexo II"
                else:
                    df.at[idx, "resultado"] = "Sem vaga — Código Anexo I inválido"
                df.at[idx, "observacao"] = df.at[idx, "resultado"]
            elif escolha_a2:
                if escolha_a2 in ANEXO_II:
                    df.at[idx, "resultado"] = "Sem vaga — Anexo II não liberado (nenhum servidor saiu da unidade)"
                else:
                    df.at[idx, "resultado"] = "Sem vaga — Código Anexo II inválido"
                df.at[idx, "observacao"] = df.at[idx, "resultado"]
            else:
                df.at[idx, "resultado"] = "Sem vaga — não escolheu unidade no Anexo I nem no Anexo II"
                df.at[idx, "observacao"] = df.at[idx, "resultado"]
            
            df.at[idx, "designacao_origem"] = "-"
    
    return df, vagas_anexo1, vagas_anexo2, ajustes_lotacao


def calcular_demanda(df_inscricoes):
    """
    Calcula quantos servidores escolheram cada vaga.
    Retorna dicionários com contagem para Anexo I e Anexo II.
    """
    demanda_a1 = {}
    demanda_a2 = {}
    
    if df_inscricoes.empty:
        return demanda_a1, demanda_a2
    
    for _, row in df_inscricoes.iterrows():
        # Contar escolhas do Anexo I
        escolha_a1 = row.get("escolha_anexo1", "")
        if escolha_a1 and escolha_a1 in ANEXO_I:
            demanda_a1[escolha_a1] = demanda_a1.get(escolha_a1, 0) + 1
        
        # Contar escolhas do Anexo II
        escolha_a2 = row.get("escolha_anexo2", "")
        if escolha_a2 and escolha_a2 in ANEXO_II:
            demanda_a2[escolha_a2] = demanda_a2.get(escolha_a2, 0) + 1
    
    return demanda_a1, demanda_a2


def normalizar_nome(nome):
    """
    Normaliza um nome para comparação:
    - Remove acentos
    - Converte para minúsculas
    - Remove espaços extras
    - Remove caracteres especiais
    """
    if not nome:
        return ""
    # Converter para string se não for
    nome = str(nome)
    # Remove acentos
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_normalizado = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    # Remove caracteres que não são letras, números ou espaços
    nome_normalizado = re.sub(r'[^a-zA-Z0-9\s]', '', nome_normalizado)
    # Converte para minúsculas e remove espaços extras
    nome_normalizado = ' '.join(nome_normalizado.lower().split())
    return nome_normalizado


def nomes_sao_iguais(nome1, nome2):
    """
    Compara dois nomes de forma flexível.
    Retorna True se forem considerados iguais.
    """
    n1 = normalizar_nome(nome1)
    n2 = normalizar_nome(nome2)
    
    # Comparação direta
    if n1 == n2:
        return True
    
    # Um contém o outro (para casos de nomes com/sem nome do meio)
    if n1 in n2 or n2 in n1:
        # Só se a diferença for pequena
        if abs(len(n1) - len(n2)) <= 5:
            return True
    
    # Comparar palavras (pelo menos 80% das palavras em comum)
    palavras1 = set(n1.split())
    palavras2 = set(n2.split())
    
    if not palavras1 or not palavras2:
        return False
    
    intersecao = palavras1 & palavras2
    menor = min(len(palavras1), len(palavras2))
    
    if menor > 0 and len(intersecao) / menor >= 0.8:
        return True
    
    return False


def tentar_match_anexo2(vaga_csv):
    """
    Tenta encontrar correspondência entre o nome da vaga no CSV e o Anexo II.
    Retorna (codigo, score) ou (None, 0) se não encontrar.
    """
    if not vaga_csv:
        return None, 0
    
    vaga_normalizada = normalizar_nome(vaga_csv)
    
    melhor_match = None
    melhor_score = 0
    
    for codigo, info in ANEXO_II.items():
        # Normalizar nome da unidade do Anexo II
        unidade_normalizada = normalizar_nome(info['unidade'])
        comarca_normalizada = normalizar_nome(info['comarca'])
        
        # Verificar se a comarca está no nome da vaga
        comarca_match = comarca_normalizada in vaga_normalizada
        
        # Calcular similaridade simples
        palavras_unidade = set(unidade_normalizada.split())
        palavras_vaga = set(vaga_normalizada.split())
        
        # Remover palavras comuns
        palavras_comuns = {'de', 'da', 'do', 'das', 'dos', 'e', 'a', 'o', 'secretaria'}
        palavras_unidade = palavras_unidade - palavras_comuns
        palavras_vaga = palavras_vaga - palavras_comuns
        
        if not palavras_unidade:
            continue
        
        # Calcular intersecção
        intersecao = palavras_unidade & palavras_vaga
        score = len(intersecao) / len(palavras_unidade)
        
        # Boost se comarca bate
        if comarca_match:
            score += 0.3
        
        if score > melhor_score:
            melhor_score = score
            melhor_match = codigo
    
    # Só retorna se tiver pelo menos 50% de match
    if melhor_score >= 0.5:
        return melhor_match, melhor_score
    
    return None, 0


def processar_csv_edital(uploaded_file):
    """
    Processa o CSV do edital oficial e retorna DataFrame tratado.
    """
    try:
        # Ler CSV com separador ;
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')
        
        # Renomear colunas
        df.columns = ['tipo', 'servidor', 'vaga', 'processo', 'data', 'situacao']
        
        # Limpar espaços
        df['servidor'] = df['servidor'].str.strip()
        df['vaga'] = df['vaga'].str.strip()
        df['situacao'] = df['situacao'].str.strip()
        
        # Adicionar coluna de nome normalizado
        df['servidor_normalizado'] = df['servidor'].apply(normalizar_nome)
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
        return None


def comparar_edital_simulador(df_csv, df_inscricoes):
    """
    Compara resultado oficial do TJPR com simulação.

    Realiza fuzzy matching entre servidores do CSV oficial e inscrições do simulador
    para identificar acertos, erros e discrepâncias entre a previsão do simulador
    e o resultado real do edital.

    Args:
        df_csv: DataFrame processado do CSV oficial (via processar_csv_edital)
        df_inscricoes: DataFrame com inscrições do simulador

    Returns:
        dict: {
            'df_comparacao': DataFrame com comparação lado a lado,
            'df_nao_encontrados': DataFrame com servidores do CSV não encontrados no simulador,
            'acertos': int - número de previsões corretas,
            'erros': int - número de previsões incorretas,
            'nao_encontrados': int - servidores do CSV sem match no simulador
        }

    Example:
        >>> df_csv = processar_csv_edital(uploaded_file)
        >>> df_inscricoes = carregar_inscricoes(sheet)
        >>> resultado = comparar_edital_simulador(df_csv, df_inscricoes)
        >>> print(f"Acurácia: {resultado['acertos']}/{resultado['acertos']+resultado['erros']}")
    """
    resultados = {
        'coincidentes': [],      # Estão nos dois
        'faltam_simulador': [],  # Estão no CSV mas não no simulador
        'remover_simulador': [], # Estão no simulador mas não no CSV (finalizados)
        'csv_finalizados': [],   # Lista de servidores com inscrição finalizada no CSV
        'csv_nao_finalizados': [] # Lista de servidores que só têm cancelado/não concluída
    }
    
    # 1. Filtrar apenas inscrições finalizadas do CSV
    df_finalizados = df_csv[df_csv['situacao'] == 'Finalizado'].copy()
    
    # 2. Pegar lista única de servidores com inscrição finalizada
    servidores_finalizados = df_finalizados.groupby('servidor_normalizado').agg({
        'servidor': 'first',
        'vaga': lambda x: list(x.unique()),
        'processo': lambda x: list(x.unique()),
        'data': 'max'
    }).reset_index()
    
    resultados['csv_finalizados'] = servidores_finalizados.to_dict('records')
    
    # 3. Servidores que só têm inscrições não finalizadas
    servidores_todos = set(df_csv['servidor_normalizado'].unique())
    servidores_ok = set(df_finalizados['servidor_normalizado'].unique())
    servidores_problema = servidores_todos - servidores_ok
    
    for nome_norm in servidores_problema:
        registros = df_csv[df_csv['servidor_normalizado'] == nome_norm]
        nome_original = registros['servidor'].iloc[0]
        situacoes = registros['situacao'].unique().tolist()
        resultados['csv_nao_finalizados'].append({
            'nome': nome_original,
            'nome_normalizado': nome_norm,
            'situacoes': situacoes
        })
    
    # 4. Preparar dados do simulador
    if not df_inscricoes.empty:
        df_inscricoes['nome_normalizado'] = df_inscricoes['nome'].apply(normalizar_nome)
        lista_simulador = [
            {
                'nome': row['nome'],
                'nome_normalizado': row['nome_normalizado'],
                'matricula': row['matricula']
            }
            for _, row in df_inscricoes.iterrows()
        ]
    else:
        lista_simulador = []
    
    # 5. Lista de servidores finalizados no CSV
    lista_csv = [
        {
            'nome': row['servidor'],
            'nome_normalizado': row['servidor_normalizado'],
            'vagas': row['vaga'],
            'data': row['data']
        }
        for _, row in servidores_finalizados.iterrows()
    ]
    
    # 6. Comparar usando função flexível
    # Para cada servidor do CSV, verificar se existe no simulador
    csv_encontrados = set()  # índices do CSV que foram encontrados
    simulador_encontrados = set()  # índices do simulador que foram encontrados
    
    for i, srv_csv in enumerate(lista_csv):
        for j, srv_sim in enumerate(lista_simulador):
            if nomes_sao_iguais(srv_csv['nome'], srv_sim['nome']):
                # Match encontrado
                csv_encontrados.add(i)
                simulador_encontrados.add(j)
                resultados['coincidentes'].append({
                    'nome_csv': srv_csv['nome'],
                    'nome_simulador': srv_sim['nome'],
                    'matricula': srv_sim['matricula'],
                    'vagas_csv': srv_csv['vagas']
                })
                break
    
    # 7. Servidores do CSV que não foram encontrados no simulador
    for i, srv_csv in enumerate(lista_csv):
        if i not in csv_encontrados:
            # Tentar fazer match com Anexo II
            vagas_match = []
            for vaga in srv_csv['vagas']:
                codigo, score = tentar_match_anexo2(vaga)
                vagas_match.append({
                    'vaga_csv': vaga,
                    'codigo_anexo2': codigo,
                    'score': score,
                    'unidade_anexo2': f"{ANEXO_II[codigo]['comarca']} - {ANEXO_II[codigo]['unidade']}" if codigo else None
                })
            
            resultados['faltam_simulador'].append({
                'nome': srv_csv['nome'],
                'nome_normalizado': srv_csv['nome_normalizado'],
                'vagas': vagas_match,
                'data': srv_csv['data']
            })
    
    # 8. Servidores do simulador que não foram encontrados no CSV finalizado
    for j, srv_sim in enumerate(lista_simulador):
        if j not in simulador_encontrados:
            # Verificar se está no CSV mas não finalizou
            encontrado_nao_finalizado = False
            for srv_nf in resultados['csv_nao_finalizados']:
                if nomes_sao_iguais(srv_sim['nome'], srv_nf['nome']):
                    encontrado_nao_finalizado = True
                    break
            
            if encontrado_nao_finalizado:
                motivo = "Inscrição NÃO FINALIZADA no edital oficial"
            else:
                motivo = "NÃO ENCONTRADO no edital oficial"
            
            resultados['remover_simulador'].append({
                'nome': srv_sim['nome'],
                'matricula': srv_sim['matricula'],
                'motivo': motivo
            })
    
    return resultados


# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================

def main():
    st.title("⚖️ Simulador de Relotação - TJPR")
    st.caption("Edital nº 01/2026 - Técnico Judiciário")

    # Aviso importante
    st.warning("""
    ⚠️ **AVISO IMPORTANTE:** Este simulador é **não oficial** e serve apenas para você se planejar melhor.
    O resultado real só sai depois da análise oficial do TJPR seguindo o Edital nº 1/2026.
    Use este simulador para testar suas opções, mas saiba que o resultado oficial pode ser diferente.
    """)

    # Conectar ao Google Sheets
    with loading_spinner("Conectando ao banco de dados..."):
        sheet = conectar_sheets()
        df_inscricoes = carregar_inscricoes(sheet)
    
    # Criar abas (7 abas: resultado, inscrição, lista, catálogo de vagas, vagas após sim, lotação, RAJs)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏆 Resultado",
        "✍️ Minha Inscrição",
        "👥 Inscritos",
        "📋 Vagas do Edital (Anexos I e II)",
        "📊 Vagas após a simulação",
        "📈 Lotação",
        "🗺️ Regiões (RAJs)"
    ])
    
    # Calcular demanda (quantos escolheram cada vaga)
    demanda_a1, demanda_a2 = calcular_demanda(df_inscricoes)
    
    # =========================================================================
    # ABA 2: INSCRIÇÃO
    # =========================================================================
    with tab2:
        st.header("✍️ Inscrição / Edição")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Nova Inscrição ou Edição")
            
            matricula_busca = st.text_input("Matrícula (para nova inscrição ou editar existente):", key="mat_busca")
            
            inscricao_existente = None
            posicao_por_matricula = None
            if matricula_busca:
                inscricao_existente = buscar_inscricao(sheet, matricula_busca)
                if inscricao_existente:
                    st.info("✏️ Inscrição encontrada! Os dados serão carregados para edição.")

                    # Verificar se matrícula está mapeada
                    if matricula_busca in MATRICULA_POSICAO_MAP:
                        posicao_por_matricula = MATRICULA_POSICAO_MAP[matricula_busca]
                        st.success(f"✅ Matrícula mapeada! Posição na lista: **{posicao_por_matricula}**")

            # BUSCA AUTOMÁTICA DE POSIÇÃO - FORA DO FORM (tempo real)
            st.subheader("🔍 Buscar Servidor na Lista Classificatória")

            nome_busca_auto = st.text_input(
                "Digite o nome completo do servidor:",
                value=inscricao_existente.get("nome", "") if inscricao_existente else "",
                help="A busca é feita automaticamente conforme você digita",
                key="nome_busca_auto"
            )

            posicao_sugerida = None
            nome_encontrado = ""

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
                        st.success(f"✅ **Servidor encontrado na Lista Classificatória!**\n\n**Posição: {posicao_sugerida}**\n\nNome na lista: {nome_lista}")
                        nome_encontrado = nome_lista
                    elif score >= 85:
                        st.warning(f"⚠️ **Servidor possivelmente encontrado** (similaridade: {score}%)\n\n**Posição: {posicao_sugerida}**\n\nNome na lista: {nome_lista}\n\n⚠️ Verifique se está correto ou informe a posição manualmente abaixo!")
                        nome_encontrado = nome_lista
                else:
                    st.error(f"❌ **Servidor NÃO encontrado automaticamente!**\n\nInforme a posição manualmente no formulário abaixo.")

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
                        st.info(f"📋 **Inscrição existente encontrada pelo nome!** Matrícula: **{inscricao_existente.get('matricula', '')}** — dados carregados para edição.")

            st.divider()

            # Aviso sobre verificações manuais necessárias (Edital 01/2026)
            st.warning("""
**Verificações Manuais Necessárias (Edital 01/2026):**

Antes de confirmar a inscrição, verifique se o servidor:
- Está lotado em unidade do **1º Grau de Jurisdição** (Item 3.2)
- **NÃO** foi relotado a pedido há menos de **2 anos** da data de publicação do edital - 10/02/2026 (Item 3.3)
- Se relotou no Edital 04/2025 e permaneceu designado na origem, só pode participar se atender ao item 3.3 (Item 3.3.2)
""")

            # Determinar matrícula para o formulário (da busca direta ou encontrada por nome)
            matricula_valor = matricula_busca
            if not matricula_valor and inscricao_existente:
                matricula_valor = str(inscricao_existente.get("matricula", ""))

            with st.form("form_inscricao"):
                nome = st.text_input(
                    "Nome completo:",
                    value=nome_encontrado if nome_encontrado else (inscricao_existente.get("nome", "") if inscricao_existente else ""),
                    help="Nome do servidor (preenchido automaticamente se encontrado acima)"
                )

                # Campo manual de posição com valor sugerido
                posicao_default = posicao_sugerida if posicao_sugerida else (inscricao_existente.get("posicao_lista_classificatoria") if inscricao_existente else None)

                posicao_lista = st.number_input(
                    "Posição na Lista Classificatória:",
                    min_value=1,
                    max_value=1291,
                    value=int(posicao_default) if posicao_default else 1,
                    step=1,
                    help="Posição do servidor na Lista Classificatória do Edital 01/2026 (1 a 1291)"
                )

                # Validar e mostrar dados da posição informada
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

                # Fallback: usar inicio_cargo da Lista Classificatória
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
                
                # Edital 01/2026: Servidores em estágio probatório PODEM participar
                # (Aviso de estágio probatório removido)

                opcoes_lotacao = construir_opcoes_selectbox(ANEXO_II, default_text="", incluir_vazio=True)

                lotacao_default = 0
                if inscricao_existente and inscricao_existente.get("lotacao_atual"):
                    codigo_lot = inscricao_existente["lotacao_atual"]
                    lotacao_default = encontrar_indice_opcao(opcoes_lotacao, codigo_lot)
                
                lotacao_atual = st.selectbox(
                    "Lotação Atual:",
                    opcoes_lotacao,
                    index=lotacao_default,
                    help="Unidade judiciária onde você está lotado atualmente"
                )
                
                opcoes_a1 = construir_opcoes_selectbox(ANEXO_I, default_text=OPCAO_NAO_ESCOLHEU, incluir_vazio=True, mostrar_quantidade=True)

                escolha_a1_default = 0
                if inscricao_existente and inscricao_existente.get("escolha_anexo1"):
                    codigo_a1 = inscricao_existente["escolha_anexo1"]
                    escolha_a1_default = encontrar_indice_opcao(opcoes_a1, codigo_a1)
                
                escolha_a1 = st.selectbox(
                    "1ª Escolha - Anexo I (Vagas Prioritárias com Déficit):",
                    opcoes_a1,
                    index=escolha_a1_default,
                    help="50 unidades judiciárias que estão com déficit de servidores. Opcional: você pode deixar em branco se preferir."
                )
                
                opcoes_a2 = construir_opcoes_selectbox(ANEXO_II, default_text=OPCAO_NAO_ESCOLHEU, incluir_vazio=True)

                escolha_a2_default = 0
                if inscricao_existente and inscricao_existente.get("escolha_anexo2"):
                    codigo_a2 = inscricao_existente["escolha_anexo2"]
                    escolha_a2_default = encontrar_indice_opcao(opcoes_a2, codigo_a2)
                
                escolha_a2 = st.selectbox(
                    "2ª Escolha - Anexo II (Todas as Unidades Judiciárias):",
                    opcoes_a2,
                    index=escolha_a2_default,
                    help="Mais de 300 unidades judiciárias. Você pode escolher apenas esta opção se preferir, sem escolher Anexo I."
                )
                
                # Extrair códigos para verificações
                codigo_lotacao_temp = extrair_codigo_da_opcao(lotacao_atual, default_vazio="")
                codigo_escolha_a2_temp = extrair_codigo_da_opcao(escolha_a2, default_vazio=OPCAO_NAO_ESCOLHEU)
                
                # ALERTA DE CONFLITO: origem = destino
                if codigo_lotacao_temp and codigo_escolha_a2_temp and codigo_lotacao_temp == codigo_escolha_a2_temp:
                    alert_box(
                        "CONFLITO: Você escolheu a mesma unidade como origem e destino no Anexo II. Isso não faz sentido!",
                        alert_type="error"
                    )
                
                # RESUMO/PREVIEW antes de salvar
                st.divider()
                st.markdown("**📋 Resumo da Inscrição:**")
                
                col_resumo1, col_resumo2 = st.columns(2)
                with col_resumo1:
                    st.markdown(f"**Nome:** {nome if nome else '-'}")
                    st.markdown(f"**Matrícula:** {matricula if matricula else '-'}")
                    st.markdown(f"**Data Admissão:** {data_admissao.strftime('%d/%m/%Y') if data_admissao else '-'}")
                
                with col_resumo2:
                    lotacao_resumo = lotacao_atual.split(" - ", 1)[1] if lotacao_atual and " - " in lotacao_atual else "-"
                    escolha_a1_resumo = escolha_a1.split(" - ", 1)[1] if escolha_a1 != "(Não escolheu)" and " - " in escolha_a1 else "-"
                    escolha_a2_resumo = escolha_a2.split(" - ", 1)[1] if escolha_a2 != "(Não escolheu)" and " - " in escolha_a2 else "-"
                    
                    st.markdown(f"**Origem:** {lotacao_resumo[:50]}..." if len(lotacao_resumo) > 50 else f"**Origem:** {lotacao_resumo}")
                    st.markdown(f"**1ª Opção (Anexo I):** {escolha_a1_resumo[:50]}..." if len(escolha_a1_resumo) > 50 else f"**1ª Opção (Anexo I):** {escolha_a1_resumo}")
                    st.markdown(f"**2ª Opção (Anexo II):** {escolha_a2_resumo[:50]}..." if len(escolha_a2_resumo) > 50 else f"**2ª Opção (Anexo II):** {escolha_a2_resumo}")
                
                submitted = st.form_submit_button("💾 Salvar Inscrição", use_container_width=True)

                if submitted:
                    # Verificar conflito novamente
                    if codigo_lotacao_temp and codigo_escolha_a2_temp and codigo_lotacao_temp == codigo_escolha_a2_temp:
                        st.error("❌ Não é possível salvar: origem e destino são iguais!")
                    elif not nome or not matricula or not data_admissao or not lotacao_atual:
                        st.error("Preencha todos os campos obrigatórios!")
                    elif not posicao_lista or posicao_lista < 1 or posicao_lista > 1291:
                        st.error("❌ **Posição inválida!**\n\nInforme uma posição entre 1 e 1291.")
                    elif posicao_lista not in LISTA_CLASSIFICATORIA:
                        st.error(f"❌ **Posição {posicao_lista} não encontrada na Lista Classificatória!**\n\nVerifique a posição correta.")
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
                            "posicao_lista_classificatoria": posicao_lista
                        }

                        if salvar_inscricao(sheet, dados):
                            handle_success("✅ Inscrição salva com sucesso!", show_balloons=True)
                            st.cache_resource.clear()
                            st.rerun()
        
        with col2:
            st.subheader("Excluir Inscrição")
            
            matricula_excluir = st.text_input("Matrícula para excluir:", key="mat_excluir")
            
            if st.button("🗑️ Excluir Inscrição", type="secondary"):
                if matricula_excluir:
                    inscricao = buscar_inscricao(sheet, matricula_excluir)
                    if inscricao:
                        sucesso, nome = excluir_inscricao(sheet, matricula_excluir)
                        if sucesso:
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
            **Regras do Edital 01/2026:**
            - Servidores relotados há menos de 2 anos são desclassificados (verificar manualmente)
            - Critério de prioridade: **posição na Lista Classificatória**

            **Como funciona:**
            1. Primeiro são analisadas as escolhas do **Anexo I** (vagas deficitárias)
            2. Quem consegue vaga no Anexo I, libera sua lotação atual
            3. As vagas liberadas ficam disponíveis para o **Anexo II**
            4. A posição na lista classificatória define a prioridade

            **Designação na Origem (item 3.14):**
            - Se sua saída **ocasionar déficit** na origem, você será designado para continuar lá até substituição
            - Se sua saída **não ocasionar déficit**, você pode ir imediatamente para a nova unidade
            """)
    
    # =========================================================================
    # ABA 3: SERVIDORES INSCRITOS
    # =========================================================================
    with tab3:
        st.header("👥 Lista de Inscritos")
        st.caption("Todos os servidores que se inscreveram na relotação")
        
        if df_inscricoes.empty:
            st.info("Nenhum servidor inscrito ainda.")
        else:
            df_inscricoes_local = carregar_inscricoes(sheet)

            # Garantir que posicao_lista_classificatoria está como Int64
            df_inscricoes_local["posicao_lista_classificatoria"] = pd.to_numeric(
                df_inscricoes_local["posicao_lista_classificatoria"],
                errors="coerce"
            ).astype("Int64")

            # Ordenar por posição na lista classificatória (NA no final)
            df_display = df_inscricoes_local.sort_values(
                "posicao_lista_classificatoria",
                ascending=True,
                na_position='last'
            ).reset_index(drop=True)
            df_display["posicao"] = df_display["posicao_lista_classificatoria"]
            
            df_display["data_admissao_fmt"] = df_display["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
            )
            
            # Edital 01/2026: Coluna de estágio probatório removida (todos podem participar)

            # Adicionar status de lotação da origem
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
            
            # BUSCA POR NOME OU MATRÍCULA
            busca_servidor = st.text_input("🔍 Buscar servidor:", key="busca_servidor",
                                            placeholder="Digite nome ou matrícula...")

            # Aplicar filtros
            df_filtrado = df_display.copy()

            if busca_servidor:
                mask = df_filtrado.apply(
                    lambda x: busca_servidor.lower() in str(x["nome"]).lower() or
                              busca_servidor.lower() in str(x["matricula"]).lower(),
                    axis=1
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
                width="stretch",
                hide_index=True
            )
            
            st.caption(f"Exibindo: {len(df_filtrado)} de {len(df_display)} servidores inscritos")
            
            # Expander com histórico de alterações
            with st.expander("📋 Histórico de Registros/Alterações"):
                st.markdown("**Quem cadastrou ou alterou cada inscrição:**")
                
                # Verificar se as colunas de log existem
                tem_log = "registrado_por" in df_display.columns and "alterado_por" in df_display.columns
                
                if tem_log:
                    df_log = df_display[[
                        "nome", "matricula", "registrado_por", "alterado_por", "data_alteracao"
                    ]].copy()
                    
                    df_log["registrado_por"] = df_log["registrado_por"].fillna("-")
                    df_log["alterado_por"] = df_log["alterado_por"].fillna("-")
                    df_log["data_alteracao"] = df_log["data_alteracao"].fillna("-")
                    
                    st.dataframe(
                        df_log.rename(columns={
                            "nome": "Nome",
                            "matricula": "Matrícula",
                            "registrado_por": "Registrado Por",
                            "alterado_por": "Última Alteração Por",
                            "data_alteracao": "Data/Hora Alteração"
                        }),
                        width="stretch",
                        hide_index=True
                    )
                else:
                    st.info("Registros antigos não possuem informações de log. Novas inscrições terão essa informação automaticamente.")
    
    # =========================================================================
    # ABA 1: RESULTADO E DASHBOARD
    # =========================================================================
    with tab1:
        section_header("Resultado da Simulação", icon="🏆", subtitle="Edital nº 01/2026 - Técnico Judiciário")

        if df_inscricoes.empty:
            empty_state(
                "Nenhum servidor inscrito ainda",
                icon="📭",
                suggestion="O resultado aparecerá quando houver inscrições. Faça sua inscrição na aba ✍️ Inscrição"
            )
        else:
            with loading_spinner("Calculando resultado da simulação..."):
                df_resultado, vagas_restantes_a1, vagas_disponiveis_a2, ajustes_lotacao = calcular_resultado(df_inscricoes)

            col1, col2, col3, col4 = st.columns(4)

            total = len(df_resultado)
            # Contar aprovados por Anexo I e Anexo II
            aprovados_a1 = len(df_resultado[df_resultado["resultado"].str.startswith("Anexo I", na=False)])
            aprovados_a2 = len(df_resultado[df_resultado["resultado"].str.startswith("Anexo II", na=False)])
            desclass = len(df_resultado[df_resultado["status"] == "DESCLASSIFICADO"])

            # Contar designações na origem
            com_designacao = len(df_resultado[df_resultado["designacao_origem"] == "SIM"])

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
            
            # Explicação sobre Designação na Origem
            with st.expander("ℹ️ O que significa 'Designação na Origem'?"):
                st.markdown("""
                **O que é "Designação na Origem"?**

                É quando você consegue a vaga, mas precisa continuar trabalhando na sua unidade atual até chegar um substituto.

                | Designação | O que acontece? |
                |------------|-------------|
                | **NÃO** | ✅ Sua saída **não deixa a unidade abaixo do mínimo** de servidores. Você pode ir para a nova unidade imediatamente! |
                | **SIM** | ⚠️ Sua saída **deixaria a unidade abaixo do mínimo**. Você foi aprovado e será transferido oficialmente, MAS continua trabalhando na unidade atual até chegarem novos servidores. |

                **⚠️ Atenção Importante:** Se não chegarem substitutos até o final da validade do concurso, sua transferência pode ser cancelada e você volta oficialmente para a unidade de origem.

                **Como saber se terei que ficar designado?**
                - 🟢 Se a unidade ficar **acima do mínimo** depois que você sair → Designação = NÃO
                - 🟡 Se a unidade ficar **no mínimo exato** depois que você sair → Designação = NÃO
                - 🔴 Se a unidade ficar **abaixo do mínimo** depois que você sair → Designação = SIM
                """)

            # Nota sobre verificações manuais (Edital 01/2026)
            st.info("""
**Nota sobre o Edital 01/2026:**

Este simulador **NÃO verifica automaticamente**:
- Se o servidor está lotado em 1º grau (Item 3.2)
- Se houve relotação nos últimos 2 anos (Item 3.3)
- Regras especiais para unidades em estatização (Item 3.4)
- Servidores de unidades superavitárias ou já designados de ofício (Item 3.18)

Essas verificações são feitas manualmente pela Secretaria de Gestão de Pessoas.
""")

            st.subheader("📊 Resultado por Ordem de Antiguidade")

            df_resultado["data_admissao_fmt"] = df_resultado["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
            )

            # Adicionar unidade de origem formatada
            df_resultado["unidade_origem"] = df_resultado["lotacao_atual"].apply(
                lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
            )

            # Busca por nome ou matrícula
            col_busca, col_filtro = st.columns([3, 1])
            with col_busca:
                busca_resultado = st.text_input(
                    "🔍 Buscar no resultado:",
                    placeholder="Digite nome ou matrícula...",
                    key="busca_resultado"
                )
            with col_filtro:
                filtro_status = st.selectbox(
                    "Filtrar por status:",
                    ["Todos", "APROVADO", "DESCLASSIFICADO", "NÃO OBTEVE VAGA"],
                    key="filtro_status_resultado"
                )

            # Aplicar filtros
            df_filtrado = df_resultado.copy()

            if busca_resultado:
                mask = df_filtrado.apply(
                    lambda x: busca_resultado.lower() in str(x["nome"]).lower() or
                              busca_resultado.lower() in str(x["matricula"]).lower(),
                    axis=1
                )
                df_filtrado = df_filtrado[mask]

            if filtro_status != "Todos":
                df_filtrado = df_filtrado[df_filtrado["status"] == filtro_status]

            # Tabela resumida (sem Data Admissão e Observação para reduzir largura)
            df_exibir = df_filtrado[[
                "posicao_antiguidade", "nome", "matricula", "unidade_origem", "status",
                "resultado", "vaga_obtida", "designacao_origem"
            ]].copy()

            # Renomear colunas
            df_exibir = df_exibir.rename(columns={
                "posicao_antiguidade": "Pos.",
                "nome": "Nome",
                "matricula": "Matrícula",
                "unidade_origem": "Origem",
                "status": "Status",
                "resultado": "Resultado",
                "vaga_obtida": "Vaga Obtida",
                "designacao_origem": "Designação"
            })

            # Função otimizada para styling de linha inteira
            def highlight_row(row):
                if row["Status"] == "APROVADO":
                    if row["Designação"] == "SIM":
                        color = "#fff3cd"  # Amarelo
                    else:
                        color = "#d4edda"  # Verde
                elif row["Status"] == "DESCLASSIFICADO":
                    color = "#f8d7da"  # Vermelho
                elif row["Status"] == "NÃO OBTEVE VAGA":
                    color = "#e2e3e5"  # Cinza
                else:
                    color = ""

                return [f"background-color: {color}" if color else ""] * len(row)

            st.dataframe(
                df_exibir.style.apply(highlight_row, axis=1),
                width="stretch",
                hide_index=True,
                height=500,
                use_container_width=True
            )

            st.caption(f"Exibindo: {len(df_filtrado)} de {len(df_resultado)} servidores")

            # Legenda de cores
            st.markdown("""
            **Legenda:**
            - 🟢 Aprovado (designação = NÃO) - pode sair imediatamente
            - 🟡 Aprovado (designação = SIM) - fica na origem até substituição
            - ⚪ Não obteve vaga
            """)

            
            st.divider()
            
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
                    st.dataframe(pd.DataFrame(vagas_rest), width="stretch", hide_index=True)
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
                    st.dataframe(pd.DataFrame(vagas_disp), width="stretch", hide_index=True)
                else:
                    st.info("Nenhuma vaga liberada no Anexo II ainda.")
            
            # =========== DASHBOARD INTEGRADO ===========
            st.divider()
            st.subheader("📊 Dashboard - Estatísticas")

            # Métricas adicionais
            col1, col2, col3, col4, col5 = st.columns(5)

            aprovados = len(df_resultado[df_resultado["status"] == "APROVADO"])
            sem_vaga = len(df_resultado[df_resultado["status"] == "NÃO OBTEVE VAGA"])
            sem_designacao = len(df_resultado[df_resultado["designacao_origem"] == "NÃO"])

            col1.metric("✅ Aprovados", aprovados, f"{100*aprovados/total:.1f}%" if total > 0 else "0%")
            col2.metric("📋 Anexo I", aprovados_a1)
            col3.metric("📋 Anexo II", aprovados_a2)
            col4.metric("❌ Desclassificados", desclass)
            col5.metric("⚪ Sem Vaga", sem_vaga)

            st.divider()

            # =========== GRÁFICOS VISUAIS ===========
            st.subheader("📈 Visualização Gráfica")

            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.markdown("**📊 Distribuição de Resultados**")
                # Gráfico de pizza
                fig_dados = {
                    'Status': ['Aprovados', 'Desclassificados', 'Sem Vaga'],
                    'Quantidade': [aprovados, desclass, sem_vaga],
                    'Cor': ['#28a745', '#dc3545', '#6c757d']
                }
                df_grafico = pd.DataFrame(fig_dados)

                import plotly.express as px
                fig_pizza = px.pie(
                    df_grafico,
                    values='Quantidade',
                    names='Status',
                    color='Status',
                    color_discrete_map={
                        'Aprovados': '#28a745',
                        'Desclassificados': '#dc3545',
                        'Sem Vaga': '#6c757d'
                    },
                    hole=0.4
                )
                fig_pizza.update_traces(textposition='inside', textinfo='percent+label+value')
                fig_pizza.update_layout(
                    showlegend=True,
                    height=350,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col_graf2:
                st.markdown("**📋 Aprovados por Anexo**")
                # Gráfico de barras
                fig_dados_anexo = {
                    'Anexo': ['Anexo I', 'Anexo II'],
                    'Quantidade': [aprovados_a1, aprovados_a2],
                    'Cor': ['#1E88E5', '#43A047']
                }
                df_anexo = pd.DataFrame(fig_dados_anexo)

                fig_barras = px.bar(
                    df_anexo,
                    x='Anexo',
                    y='Quantidade',
                    color='Anexo',
                    color_discrete_map={
                        'Anexo I': '#1E88E5',
                        'Anexo II': '#43A047'
                    },
                    text='Quantidade'
                )
                fig_barras.update_traces(textposition='outside')
                fig_barras.update_layout(
                    showlegend=False,
                    height=350,
                    yaxis_title="Servidores Aprovados",
                    xaxis_title="",
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_barras, use_container_width=True)

            # Gráfico de designação
            col_graf3, col_graf4 = st.columns(2)

            with col_graf3:
                st.markdown("**🏢 Designação na Origem**")
                com_designacao = len(df_resultado[df_resultado["designacao_origem"] == "SIM"])
                sem_designacao = len(df_resultado[df_resultado["designacao_origem"] == "NÃO"])

                fig_dados_desig = {
                    'Situação': ['Podem sair\nimediatamente', 'Aguardam\nsubstituição'],
                    'Quantidade': [sem_designacao, com_designacao]
                }
                df_desig = pd.DataFrame(fig_dados_desig)

                fig_desig = px.bar(
                    df_desig,
                    x='Situação',
                    y='Quantidade',
                    color='Situação',
                    color_discrete_map={
                        'Podem sair\nimediatamente': '#28a745',
                        'Aguardam\nsubstituição': '#ffc107'
                    },
                    text='Quantidade'
                )
                fig_desig.update_traces(textposition='outside')
                fig_desig.update_layout(
                    showlegend=False,
                    height=350,
                    yaxis_title="Servidores Aprovados",
                    xaxis_title="",
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_desig, use_container_width=True)

            with col_graf4:
                st.markdown("**🗺️ Top 5 Comarcas Mais Procuradas**")
                # Contar comarcas mais escolhidas
                comarcas_count = {}
                for _, row in df_resultado.iterrows():
                    if row['status'] == 'APROVADO' and row['vaga_obtida'] and row['vaga_obtida'] != '-':
                        comarca = extrair_comarca_da_string(row['vaga_obtida'])
                        if comarca:
                            comarcas_count[comarca] = comarcas_count.get(comarca, 0) + 1

                if comarcas_count:
                    top_comarcas = sorted(comarcas_count.items(), key=lambda x: x[1], reverse=True)[:5]
                    df_comarcas = pd.DataFrame(top_comarcas, columns=['Comarca', 'Servidores'])

                    fig_comarcas = px.bar(
                        df_comarcas,
                        y='Comarca',
                        x='Servidores',
                        orientation='h',
                        text='Servidores',
                        color='Servidores',
                        color_continuous_scale='Blues'
                    )
                    fig_comarcas.update_traces(textposition='outside')
                    fig_comarcas.update_layout(
                        showlegend=False,
                        height=350,
                        xaxis_title="Servidores Aprovados",
                        yaxis_title="",
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig_comarcas, use_container_width=True)
                else:
                    st.info("Nenhum servidor aprovado ainda.")

    # =========================================================================
    # ABA 4: VAGAS (Anexo I e II)
    # =========================================================================
    with tab4:
        st.header("📋 Vagas do Edital")
        st.caption("Catálogo de vagas com quantidade e demanda (quantos inscritos escolheram cada unidade)")
        
        # Sub-seções com radio button
        opcao_vagas = st.radio(
            "Escolha o anexo:",
            ["📋 Anexo I (Vagas com Déficit)", "📋 Anexo II (Todas as Unidades)"],
            horizontal=True,
            key="opcao_vagas"
        )
        
        st.divider()
        
        if opcao_vagas == "📋 Anexo I (Vagas com Déficit)":
            st.subheader("Vagas com Déficit (Anexo I)")
            st.info("💡 **Anexo I** = 50 unidades que precisam urgentemente de servidores. A coluna **Demanda** mostra quantos servidores querem ir para cada unidade.")
            
            dados_a1 = []
            for codigo, info in ANEXO_I.items():
                demanda = demanda_a1.get(codigo, 0)
                vagas = info["quantidade"]
                # Calcular indicador de concorrência
                if demanda == 0:
                    concorrencia = "🟢 Sem demanda"
                elif demanda < vagas:
                    concorrencia = "🟡 Baixa"
                elif demanda == vagas:
                    concorrencia = "🟠 Equilibrada"
                else:
                    concorrencia = "🔴 Alta"
                
                dados_a1.append({
                    "Código": codigo,
                    "Comarca": info["comarca"],
                    "Unidade Judiciária": info["unidade"],
                    "Vagas": vagas,
                    "Demanda": demanda,
                    "Concorrência": concorrencia
                })
            
            df_a1 = pd.DataFrame(dados_a1)
            
            col1, col2 = st.columns(2)
            with col1:
                comarcas_a1 = sorted(df_a1["Comarca"].unique())
                filtro_comarca_a1 = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_a1, key="filtro_a1")
            with col2:
                filtro_concorrencia = st.selectbox("Filtrar por concorrência:", 
                                                    ["Todas", "🟢 Sem demanda", "🟡 Baixa", "🟠 Equilibrada", "🔴 Alta"], 
                                                    key="filtro_conc_a1")
            
            if filtro_comarca_a1 != "Todas":
                df_a1 = df_a1[df_a1["Comarca"] == filtro_comarca_a1]
            
            if filtro_concorrencia != "Todas":
                df_a1 = df_a1[df_a1["Concorrência"] == filtro_concorrencia]
            
            busca_a1 = st.text_input("🔍 Buscar:", key="busca_a1", placeholder="Digite parte do nome da comarca ou unidade...")
            if busca_a1:
                mask = df_a1.apply(lambda x: busca_a1.lower() in x["Comarca"].lower() or busca_a1.lower() in x["Unidade Judiciária"].lower(), axis=1)
                df_a1 = df_a1[mask]
            
            st.dataframe(df_a1, width="stretch", hide_index=True)
            
            total_demanda = df_a1["Demanda"].sum()
            st.caption(f"Total: {len(df_a1)} unidades | {df_a1['Vagas'].sum()} vagas | {total_demanda} servidores interessados")
        
        else:  # Anexo II
            st.subheader("Todas as Unidades (Anexo II)")
            st.info("💡 **Anexo II** = Todas as 300+ unidades judiciárias do TJPR. A coluna **Demanda** mostra quantos servidores querem ir para cada unidade (escolha 2ª opção).")
            
            dados_a2 = []
            for codigo, info in ANEXO_II.items():
                # Adicionar status de lotação
                status_lot = obter_status_lotacao(codigo)
                demanda = demanda_a2.get(codigo, 0)
                dados_a2.append({
                    "Código": codigo,
                    "Comarca": info["comarca"],
                    "Unidade Judiciária": info["unidade"],
                    "Status Lotação": status_lot,
                    "Demanda": demanda
                })
            
            df_a2 = pd.DataFrame(dados_a2)
            
            col1, col2 = st.columns(2)
            with col1:
                comarcas_a2 = sorted(df_a2["Comarca"].unique())
                filtro_comarca_a2 = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_a2, key="filtro_a2")
            with col2:
                # Filtro por status de lotação
                filtro_status = st.selectbox("Filtrar por status de lotação:", 
                                              ["Todos", "SUPERAVITÁRIA", "EQUILIBRADA", "DEFICITÁRIA", "NÃO IDENTIFICADA"],
                                              key="filtro_status_a2")
            
            if filtro_comarca_a2 != "Todas":
                df_a2 = df_a2[df_a2["Comarca"] == filtro_comarca_a2]
            
            if filtro_status != "Todos":
                df_a2 = df_a2[df_a2["Status Lotação"] == filtro_status]
            
            # Checkbox para mostrar apenas com demanda
            mostrar_com_demanda = st.checkbox("Mostrar apenas unidades com demanda", key="filtro_demanda_a2")
            if mostrar_com_demanda:
                df_a2 = df_a2[df_a2["Demanda"] > 0]
            
            busca_a2 = st.text_input("🔍 Buscar:", key="busca_a2", placeholder="Digite parte do nome da comarca ou unidade...")
            if busca_a2:
                mask = df_a2.apply(lambda x: busca_a2.lower() in x["Comarca"].lower() or busca_a2.lower() in x["Unidade Judiciária"].lower(), axis=1)
                df_a2 = df_a2[mask]
            
            # Colorir por status
            def color_status(val):
                if val == "SUPERAVITÁRIA":
                    return "background-color: #d4edda"
                elif val == "EQUILIBRADA":
                    return "background-color: #fff3cd"
                elif val == "DEFICITÁRIA":
                    return "background-color: #f8d7da"
                return ""
            
            st.dataframe(
                df_a2.style.applymap(color_status, subset=["Status Lotação"]),
                width="stretch", 
                hide_index=True
            )
            
            total_demanda_a2 = df_a2["Demanda"].sum()
            st.caption(f"Total: {len(df_a2)} unidades | {total_demanda_a2} servidores interessados")

    # =========================================================================
    # ABA 5: VAGAS APÓS A SIMULAÇÃO (por RAJ)
    # =========================================================================
    with tab5:
        st.header("📊 Vagas após a simulação")
        st.caption("O que restou do Anexo I (não preenchidas) e o que abriu no Anexo II (vagas liberadas por quem saiu), agrupado por região")

        if df_inscricoes.empty:
            st.info("📝 Faça inscrições primeiro para poder ver esta análise.")
        else:
            # Calcular resultado para obter vagas restantes
            df_resultado, vagas_restantes_a1, vagas_disponiveis_a2, ajustes_lotacao = calcular_resultado(df_inscricoes)

            st.markdown("### 📊 Visão Geral")

            # Calcular totais
            total_nao_preenchidas_a1 = sum(vagas_restantes_a1.values())
            total_disponiveis_a2 = sum(vagas_disponiveis_a2.values())

            col1, col2 = st.columns(2)
            col1.metric("🔴 Vagas não preenchidas (Anexo I)", total_nao_preenchidas_a1)
            col2.metric("🟢 Vagas abertas (Anexo II)", total_disponiveis_a2)

            st.divider()

            # Preparar dados por RAJ - Anexo I
            st.markdown("### 🔴 Anexo I - Vagas não preenchidas")
            st.caption("Vagas com déficit que continuam abertas porque ninguém as escolheu como 1ª opção")

            dados_raj_a1 = {}
            for codigo, qtd_restante in vagas_restantes_a1.items():
                if qtd_restante > 0:
                    info = ANEXO_I[codigo]
                    comarca = info['comarca']
                    unidade = info['unidade']
                    raj = obter_raj_da_comarca(comarca, normalizar_func=normalizar_comarca)

                    if raj not in dados_raj_a1:
                        dados_raj_a1[raj] = []

                    dados_raj_a1[raj].append({
                        'Comarca': comarca,
                        'Unidade': unidade,
                        'Vagas não preenchidas': qtd_restante,
                        'Código': codigo
                    })

            if dados_raj_a1:
                # Ordenar RAJs
                rajs_ordenadas_a1 = sorted(dados_raj_a1.keys())

                for raj in rajs_ordenadas_a1:
                    total_raj = sum(v['Vagas não preenchidas'] for v in dados_raj_a1[raj])
                    with st.expander(f"**{raj}** ({total_raj} vagas não preenchidas)"):
                        df_raj = pd.DataFrame(dados_raj_a1[raj])
                        df_raj = df_raj.sort_values('Comarca')
                        st.dataframe(
                            df_raj[['Comarca', 'Unidade', 'Vagas não preenchidas']],
                            hide_index=True,
                            use_container_width=True
                        )
            else:
                st.success("✅ Todas as vagas do Anexo I foram preenchidas!")

            st.divider()

            # Preparar dados por RAJ - Anexo II
            st.markdown("### 🟢 Anexo II - Vagas abertas pela simulação")
            st.caption("Unidades que passaram a ter vaga porque servidores foram aprovados e saíram (origem liberou vaga)")

            dados_raj_a2 = {}
            for codigo, qtd_disponivel in vagas_disponiveis_a2.items():
                if qtd_disponivel > 0:
                    info = ANEXO_II[codigo]
                    comarca = info['comarca']
                    unidade = info['unidade']
                    raj = obter_raj_da_comarca(comarca, normalizar_func=normalizar_comarca)

                    if raj not in dados_raj_a2:
                        dados_raj_a2[raj] = []

                    dados_raj_a2[raj].append({
                        'Comarca': comarca,
                        'Unidade': unidade,
                        'Vagas Disponíveis': qtd_disponivel,
                        'Código': codigo
                    })

            if dados_raj_a2:
                # Ordenar RAJs
                rajs_ordenadas_a2 = sorted(dados_raj_a2.keys())

                for raj in rajs_ordenadas_a2:
                    total_raj = sum(v['Vagas Disponíveis'] for v in dados_raj_a2[raj])
                    with st.expander(f"**{raj}** ({total_raj} vagas disponíveis)"):
                        df_raj = pd.DataFrame(dados_raj_a2[raj])
                        df_raj = df_raj.sort_values('Comarca')
                        st.dataframe(
                            df_raj[['Comarca', 'Unidade', 'Vagas Disponíveis']],
                            hide_index=True,
                            use_container_width=True
                        )
            else:
                st.info("ℹ️ Nenhuma vaga do Anexo II abriu ainda. Vagas só abrem quando servidores saem e deixam a unidade de origem precisando de gente.")

    # =========================================================================
    # ABA 6: LOTAÇÃO DAS UNIDADES
    # =========================================================================
    with tab6:
        st.header("📈 Lotação das Unidades Judiciárias")
        st.info("📊 Dados oficiais do TJPR mostrando quantos servidores tem cada unidade (Lotação Real) e quantos deveriam ter pelo mínimo legal (Lotação Paradigma CNJ 219/2016).")

        # Explicação
        with st.expander("ℹ️ Como interpretar os dados"):
            st.markdown("""
            **Colunas:**
            - **Lotação Real**: Quantidade de servidores que trabalham na unidade hoje
            - **Lotação Paradigma**: Quantidade mínima de servidores necessária (definida pelo CNJ)
            - **Diferença**: Quantos servidores a mais ou a menos a unidade tem

            **Status (Situação da Unidade):**
            - 🟢 **SUPERAVITÁRIA** (Acima do mínimo): Tem mais servidores que o necessário
            - 🟡 **EQUILIBRADA** (No mínimo): Tem exatamente o necessário
            - 🔴 **DEFICITÁRIA** (Abaixo do mínimo): Faltam servidores

            **Impacto na sua Relotação:**
            - Se sua saída **deixar a unidade abaixo do mínimo** (DEFICITÁRIA) → você será designado para ficar até chegar um substituto ⚠️
            - Se sua saída **NÃO deixar a unidade abaixo do mínimo** → você pode sair imediatamente ✅
            """)
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        total_unidades = len(LOTACAO_COMPLETA)
        superavit = len([u for u in LOTACAO_COMPLETA if u["status"] == "SUPERAVITÁRIA"])
        equilibrada = len([u for u in LOTACAO_COMPLETA if u["status"] == "EQUILIBRADA"])
        deficit = len([u for u in LOTACAO_COMPLETA if u["status"] == "DEFICITÁRIA"])
        
        col1.metric("Total Unidades", total_unidades)
        col2.metric("🟢 Acima do Mínimo", superavit, help="Unidades com mais servidores que o necessário")
        col3.metric("🟡 No Mínimo", equilibrada, help="Unidades com exatamente o necessário")
        col4.metric("🔴 Abaixo do Mínimo", deficit, help="Unidades com menos servidores que o necessário")
        
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
            busca_lot = st.text_input("🔍 Buscar:", key="busca_lot", placeholder="Nome da unidade...")
        
        # Criar mapeamento reverso: comarca+unidade -> código
        mapa_codigo = {}
        for codigo, dados in LOTACAO_POR_CODIGO.items():
            chave = (dados["comarca"].lower().strip(), dados["unidade"].lower().strip())
            mapa_codigo[chave] = codigo

        # Preparar dados
        dados_lotacao = []
        for u in LOTACAO_COMPLETA:
            # Buscar o código correspondente
            chave = (u["comarca"].lower().strip(), u["unidade"].lower().strip())
            codigo = mapa_codigo.get(chave, "-")

            dados_lotacao.append({
                "Código": codigo,
                "Comarca": u["comarca"],
                "Unidade": u["unidade"],
                "Lotação Real": u["lotacao_real"],
                "Lotação Paradigma": u["lotacao_paradigma"],
                "Diferença": u["diferenca"],
                "Status": u["status"]
            })
        
        df_lotacao = pd.DataFrame(dados_lotacao)
        
        # Aplicar filtros
        if filtro_comarca_lot != "Todas":
            df_lotacao = df_lotacao[df_lotacao["Comarca"] == filtro_comarca_lot]
        
        if filtro_status_lot != "Todos":
            df_lotacao = df_lotacao[df_lotacao["Status"] == filtro_status_lot]
        
        if busca_lot:
            mask = df_lotacao.apply(lambda x: busca_lot.lower() in x["Comarca"].lower() or busca_lot.lower() in x["Unidade"].lower(), axis=1)
            df_lotacao = df_lotacao[mask]
        
        # Colorir por status
        def color_status_lot(val):
            if val == "SUPERAVITÁRIA":
                return "background-color: #d4edda"
            elif val == "EQUILIBRADA":
                return "background-color: #fff3cd"
            elif val == "DEFICITÁRIA":
                return "background-color: #f8d7da"
            return ""
        
        def color_diferenca(val):
            try:
                if int(val) > 0:
                    return "color: green; font-weight: bold"
                elif int(val) < 0:
                    return "color: red; font-weight: bold"
            except (ValueError, TypeError):
                # Valor não numérico, sem coloração
                pass
            return ""
        
        st.dataframe(
            df_lotacao.style.applymap(color_status_lot, subset=["Status"]).applymap(color_diferenca, subset=["Diferença"]),
            width="stretch",
            hide_index=True,
            height=500
        )
        
        st.caption(f"Exibindo: {len(df_lotacao)} de {total_unidades} unidades")
    
    # =========================================================================
    # ABA 7: RAJS
    # =========================================================================
    with tab7:
        st.header("🗺️ Regiões Administrativas Judiciárias (RAJs)")
        st.info("📍 Veja quantos servidores **aprovados** existem em cada região geográfica do Paraná (baseado na unidade onde trabalham atualmente).")
        
        if df_inscricoes.empty:
            st.warning("Nenhum servidor inscrito ainda.")
        else:
            df_resultado, _, _, _ = calcular_resultado(df_inscricoes)
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
                
                # MAPA VISUAL DO PARANÁ
                st.subheader("🗺️ Mapa das RAJs do Paraná")
                
                # Criar dicionário de contagem
                contagem_dict = dict(zip(contagem_raj["RAJ"], contagem_raj["Quantidade de Aprovados"]))
                
                def get_raj_qtd(raj_num):
                    for raj, qtd in contagem_dict.items():
                        if f"RAJ {raj_num}" in raj:
                            return qtd
                    return 0
                
                # Linha 1: Norte do Paraná
                st.markdown("**Norte do Paraná:**")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    qtd = get_raj_qtd(10)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 10** {cor}  \nJacarezinho  \n{qtd} aprovados")
                
                with col2:
                    qtd = get_raj_qtd(9)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 9** {cor}  \nLondrina  \n{qtd} aprovados")
                
                with col3:
                    qtd = get_raj_qtd(8)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 8** {cor}  \nMaringá  \n{qtd} aprovados")
                
                with col4:
                    qtd = get_raj_qtd(7)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 7** {cor}  \nUmuarama  \n{qtd} aprovados")
                
                with col5:
                    st.markdown("")
                
                # Linha 2: Centro-Oeste
                st.markdown("**Centro-Oeste:**")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    qtd = get_raj_qtd(2)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 2** {cor}  \nPonta Grossa  \n{qtd} aprovados")
                
                with col2:
                    qtd = get_raj_qtd(3)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 3** {cor}  \nGuarapuava  \n{qtd} aprovados")
                
                with col3:
                    qtd = get_raj_qtd(6)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 6** {cor}  \nCascavel  \n{qtd} aprovados")
                
                with col4:
                    qtd = get_raj_qtd(5)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 5** {cor}  \nFoz do Iguaçu  \n{qtd} aprovados")
                
                with col5:
                    st.markdown("")
                
                # Linha 3: Sul
                st.markdown("**Sul e Litoral:**")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    qtd = get_raj_qtd(1)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 1** {cor}  \nCuritiba/Litoral  \n{qtd} aprovados")
                
                with col2:
                    qtd = get_raj_qtd(4)
                    cor = "🟢" if qtd > 0 else "⚪"
                    st.markdown(f"**RAJ 4** {cor}  \nFrancisco Beltrão  \n{qtd} aprovados")
                
                with col3:
                    st.markdown("")
                with col4:
                    st.markdown("")
                with col5:
                    st.markdown("")
                
                st.divider()
                
                st.subheader("📊 Resumo por RAJ")
                
                cols = st.columns(5)
                for i, (_, row) in enumerate(contagem_raj.iterrows()):
                    col_idx = i % 5
                    raj_nome_curto = row["RAJ"].replace("RAJ ", "").replace("Região Administrativa ", "")
                    if len(raj_nome_curto) > 25:
                        raj_nome_curto = raj_nome_curto[:22] + "..."
                    cols[col_idx].metric(raj_nome_curto, row["Quantidade de Aprovados"])
                
                st.divider()
                
                st.subheader("📋 Detalhamento por RAJ")
                
                dados_raj_detalhado = []
                for raj_nome in sorted(RAJS.keys()):
                    raj_info = RAJS[raj_nome]
                    qtd = len(df_aprovados[df_aprovados["raj_origem"] == raj_nome])
                    comarcas_str = ", ".join(sorted(raj_info["comarcas"]))
                    dados_raj_detalhado.append({
                        "RAJ": raj_nome,
                        "Sede": raj_info["sede"],
                        "Aprovados": qtd,
                        "Comarcas": comarcas_str
                    })
                
                df_raj_detalhado = pd.DataFrame(dados_raj_detalhado)
                
                st.dataframe(
                    df_raj_detalhado,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "RAJ": st.column_config.TextColumn("Região Administrativa", width="medium"),
                        "Sede": st.column_config.TextColumn("Sede", width="small"),
                        "Aprovados": st.column_config.NumberColumn("Aprovados", width="small"),
                        "Comarcas": st.column_config.TextColumn("Comarcas Abrangidas", width="large")
                    }
                )
                
                st.divider()
                
                st.subheader("👥 Lista de Aprovados por RAJ")
                
                rajs_com_aprovados = sorted(df_aprovados["raj_origem"].unique())
                raj_selecionada = st.selectbox(
                    "Selecione uma RAJ para ver os aprovados:",
                    ["Todas"] + rajs_com_aprovados
                )
                
                if raj_selecionada == "Todas":
                    df_filtrado = df_aprovados.copy()
                else:
                    df_filtrado = df_aprovados[df_aprovados["raj_origem"] == raj_selecionada].copy()
                
                df_filtrado["data_admissao_fmt"] = df_filtrado["data_admissao"].apply(
                    lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
                )
                
                df_exibir_raj = df_filtrado[[
                    "posicao_antiguidade", "nome", "matricula", "data_admissao_fmt",
                    "comarca_origem", "raj_origem", "resultado", "vaga_obtida", "designacao_origem"
                ]].rename(columns={
                    "posicao_antiguidade": "Pos. Antiguidade",
                    "nome": "Nome",
                    "matricula": "Matrícula",
                    "data_admissao_fmt": "Data Admissão",
                    "comarca_origem": "Comarca Origem",
                    "raj_origem": "RAJ Origem",
                    "resultado": "Resultado",
                    "vaga_obtida": "Vaga Obtida",
                    "designacao_origem": "Designação Origem"
                })
                
                st.dataframe(df_exibir_raj, width="stretch", hide_index=True)
                st.caption(f"Total de aprovados exibidos: {len(df_filtrado)}")


def footer():
    st.divider()
    st.caption("""
    ⚠️ **ATENÇÃO:** Este é um simulador não oficial, criado apenas para auxiliar na tomada de decisão. 
    O resultado oficial depende exclusivamente da análise do TJPR conforme Edital nº 1/2026.
    """)


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    main()
    footer()
