"""
Simulador de Relotação - TJPR
Edital nº 4/2025 - Técnico Judiciário
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from data import ANEXO_I, ANEXO_II
from lotacao_data import LOTACAO_POR_CODIGO, LOTACAO_COMPLETA
import gspread
from google.oauth2.service_account import Credentials
import json
import re

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
# CÓDIGOS DE AUTENTICAÇÃO
# =============================================================================

AUTH_CODES = {
    "41988682140": "TJPR-W9D8A6",
    "43999676080": "TJPR-X7J3J8",
    "41987771822": "TJPR-R8Y5U5",
    "44999571321": "TJPR-W6M9G7",
    "47988463737": "TJPR-E9A5M4",
    "21990432004": "TJPR-H8X5O0",
    "41988205840": "TJPR-E8I7P2",
    "41996144848": "TJPR-Q8S1Q5",
    "41998500089": "TJPR-B0U8U9",
    "41992354642": "TJPR-E2X6W9",
    "43999639622": "TJPR-T1I9R2",
    "41996111692": "TJPR-P1I4B0",
    "42984212931": "TJPR-E3Q4M2",
    "41996528826": "TJPR-F9P7U0",
    "41987981984": "TJPR-A9H9O1",
    "17996292028": "TJPR-P8G3T4",
    "41996399051": "TJPR-H3S2F7",
    "44984250493": "TJPR-B6V6F6",
    "41996248850": "TJPR-J2Y5A1",
    "46991023946": "TJPR-A3S0W4",
    "45999799439": "TJPR-Q2Z0O9",
    "41984053073": "TJPR-W6E8P1",
    "41988742311": "TJPR-W7F8C1",
    "41996591926": "TJPR-H5Q5D5",
    "44999527950": "TJPR-S6E8S5",
    "42999065470": "TJPR-T9V2X3",
    "43991973901": "TJPR-Y8W3P8",
    "41991064141": "TJPR-R1C2B9",
    "43991639901": "TJPR-G5P4N6",
    "41996139482": "TJPR-A6C7Y8",
    "43935728485": "TJPR-J0Q1B1",
    "41987233990": "TJPR-N8W5J5",
    "41998526855": "TJPR-V0G3H0",
    "47996150787": "TJPR-A1S9Y6",
    "85999247334": "TJPR-E4V8C7",
    "42999678689": "TJPR-K9X0H6",
    "41991354423": "TJPR-S5M8R2",
    "45998424843": "TJPR-B1J3C0",
    "43999509978": "TJPR-U7F1T3",
    "41996590719": "TJPR-V5Z7G7",
    "41988766147": "TJPR-B5A3J4",
    "45999729986": "TJPR-V2S7P2",
    "51998654686": "TJPR-P2X1V2",
    "44999943800": "TJPR-T6D2A9",
    "41988079178": "TJPR-Q9F4F6",
    "41997511879": "TJPR-L9X2V9",
    "41988505079": "TJPR-G2K3H0",
    "41997813606": "TJPR-F4F1X5",
    "46988274385": "TJPR-B1X3N1",
    "42999825296": "TJPR-R7Q0N0",
    "41988716808": "TJPR-Y3F6X8",
    "49998411291": "TJPR-Z2G1Q4",
    "41984714180": "TJPR-G4N4X4",
    "41984965883": "TJPR-R1S9C2",
    "42999151717": "TJPR-D2V0X0",
    "45998208420": "TJPR-E5P4V1",
    "42999746557": "TJPR-N9G0P8",
    "45984047070": "TJPR-O3X7Q1",
    "43984913099": "TJPR-Q9A6C9",
    "43999196949": "TJPR-G0Z1B9",
    "41999280158": "TJPR-T2P3U0",
    "41985230491": "TJPR-X9N2T3",
    "41998457595": "TJPR-G4T4G8",
    "43991286949": "TJPR-Y8N0Q9",
    "44999459999": "TJPR-V6K7A9",
    "42999113251": "TJPR-B2O9B4",
    "46999170352": "TJPR-M6J6G3",
    "43996186413": "TJPR-A5E3Q4",
    "44999457959": "TJPR-N9L5H5",
    "41998038212": "TJPR-H4P1Z3",
    "41988253875": "TJPR-I3O2L0",
    "46999199900": "TJPR-P8Z7E1",
    "46991252521": "TJPR-I5H7V5",
    "41999081377": "TJPR-K2X6W3",
    "45999228068": "TJPR-V8E2V2",
    "45999314847": "TJPR-L4A4K5",
    "41999160027": "TJPR-H9E7E9",
    "41999822924": "TJPR-Q0W8Q6",
    "44988554062": "TJPR-I5S7M4",
    "44999717000": "TJPR-M9B7S4",
    "42999994903": "TJPR-Z7I4O1",
    "45988194141": "TJPR-P2G0K9",
    "41996506223": "TJPR-V5A8F6",
    "42998356154": "TJPR-J1M4D3",
    "44999339584": "TJPR-X1N7H2",
    "17982226188": "TJPR-V7E6L5",
    "41984145956": "TJPR-P9X8Y4",
    "41984884473": "TJPR-U4F7W5",
    "41996632845": "TJPR-W5U8K2",
    "43991310174": "TJPR-D1K9H7",
    "41995591575": "TJPR-M9N7W8",
    "41996765443": "TJPR-R8N2F6",
    "44997167692": "TJPR-W6Q5L8",
    "44998557700": "TJPR-F4X2L2",
    "45999801630": "TJPR-N2C7D6",
    "45999246297": "TJPR-E6V9I0",
    "41996641615": "TJPR-T0O3P8",
    "44991574505": "TJPR-I6R4F4",
    "44984059858": "TJPR-T9Q3G4",
    "41999831440": "TJPR-E3S2C4",
    "46991202091": "TJPR-O5E8Z5",
    "43984920995": "TJPR-W1X7K0",
    "42999193219": "TJPR-O9S8J7",
    "43999236148": "TJPR-U8L5W2",
    "44984095131": "TJPR-N8N9G3",
    "45999005757": "TJPR-A9I0X1",
    "41988197149": "TJPR-G3C2R9",
    "41999535487": "TJPR-D7D9J5",
    "43991506066": "TJPR-K9B8N8",
    "45998424843": "TJPR-K1B4N5",
}

# =============================================================================
# FUNÇÕES DE AUTENTICAÇÃO
# =============================================================================

def formatar_telefone_display(telefone):
    """Formata telefone para exibição: (XX) XXXXX-XXXX"""
    numeros = re.sub(r'\D', '', telefone)
    if len(numeros) == 0:
        return ""
    elif len(numeros) <= 2:
        return f"({numeros}"
    elif len(numeros) <= 7:
        return f"({numeros[:2]}) {numeros[2:]}"
    elif len(numeros) <= 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    else:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:11]}"

def on_telefone_change():
    """Callback para formatar telefone em tempo real"""
    if "telefone_raw" in st.session_state:
        raw = st.session_state.telefone_raw
        numeros = re.sub(r'\D', '', raw)
        numeros = numeros[:11]
        st.session_state.telefone_formatado = formatar_telefone_display(numeros)
        st.session_state.telefone_numeros = numeros

def limpar_telefone(telefone):
    """Remove tudo que não for número do telefone"""
    return re.sub(r'\D', '', telefone)

def verificar_login(telefone, codigo):
    """Verifica se telefone e código são válidos"""
    telefone_limpo = limpar_telefone(telefone)
    codigo_upper = codigo.upper().strip()
    
    if telefone_limpo in AUTH_CODES:
        return AUTH_CODES[telefone_limpo] == codigo_upper
    return False

def tela_login():
    """Exibe a tela de login"""
    st.title("⚖️ Simulador de Relotação - TJPR")
    st.caption("Edital nº 4/2025 - Técnico Judiciário")
    
    st.divider()
    
    if "telefone_formatado" not in st.session_state:
        st.session_state.telefone_formatado = ""
    if "telefone_numeros" not in st.session_state:
        st.session_state.telefone_numeros = ""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Acesso Restrito")
        st.info("Este simulador é exclusivo para membros autorizados. Informe seu telefone e código de acesso.")
        
        telefone_input = st.text_input(
            "📱 Telefone com DDD:",
            value=st.session_state.telefone_formatado,
            placeholder="(41) 99999-9999",
            help="Digite seu número com DDD",
            key="telefone_raw",
            on_change=on_telefone_change
        )
        
        codigo = st.text_input(
            "🔑 Código de Acesso:",
            placeholder="TJPR-XXXXXX",
            help="Código enviado por WhatsApp, ex: TJPR-A1B2C3"
        )
        
        if st.button("🚀 Entrar", use_container_width=True):
            telefone_numeros = st.session_state.telefone_numeros
            if not telefone_numeros or not codigo:
                st.error("Preencha o telefone e o código!")
            elif len(telefone_numeros) < 10:
                st.error("Telefone inválido! Digite DDD + número.")
            elif verificar_login(telefone_numeros, codigo):
                st.session_state.autenticado = True
                st.session_state.telefone_usuario = telefone_numeros
                st.rerun()
            else:
                st.error("❌ Telefone ou código inválido!")
        
        st.divider()
        st.caption("Não recebeu seu código? Entre em contato com o administrador do grupo.")


# =============================================================================
# REGIÕES ADMINISTRATIVAS JUDICIÁRIAS (RAJs)
# =============================================================================

RAJS = {
    "RAJ 1 - Região Metropolitana de Curitiba e Litoral": {
        "sede": "Curitiba",
        "comarcas": [
            "Curitiba", "Almirante Tamandaré", "Antonina", "Araucária", "Bocaiúva do Sul",
            "Campina Grande do Sul", "Campo Largo", "Cerro Azul", "Colombo", "Fazenda Rio Grande",
            "Guaratuba", "Matinhos", "Morretes", "Paranaguá", "Pinhais", "Piraquara",
            "Pontal do Paraná", "Quatro Barras", "Rio Branco do Sul", "São José dos Pinhais"
        ]
    },
    "RAJ 2 - Ponta Grossa": {
        "sede": "Ponta Grossa",
        "comarcas": [
            "Ponta Grossa", "Imbituva", "Ipiranga", "Jaguariaíva", "Mallet", "Palmeira",
            "Piraí do Sul", "Rebouças", "Reserva", "São João do Triunfo", "Sengés",
            "Teixeira Soares", "Tibagi", "Castro", "Irati", "Lapa", "Rio Negro",
            "São Mateus do Sul", "Telêmaco Borba", "União da Vitória"
        ]
    },
    "RAJ 3 - Guarapuava": {
        "sede": "Guarapuava",
        "comarcas": [
            "Guarapuava", "Cândido de Abreu", "Cantagalo", "Iretama", "Manoel Ribas",
            "Palmital", "Pinhão", "Prudentópolis", "Ivaiporã", "Laranjeiras do Sul", "Pitanga"
        ]
    },
    "RAJ 4 - Francisco Beltrão": {
        "sede": "Francisco Beltrão",
        "comarcas": [
            "Francisco Beltrão", "Ampére", "Barracão", "Clevelândia", "Coronel Vivida",
            "Marmeleiro", "Mangueirinha", "Realeza", "Salto do Lontra", "São João",
            "Chopinzinho", "Dois Vizinhos", "Palmas", "Pato Branco", "Santo Antônio do Sudoeste"
        ]
    },
    "RAJ 5 - Foz do Iguaçu": {
        "sede": "Foz do Iguaçu",
        "comarcas": [
            "Foz do Iguaçu", "Matelândia", "Santa Helena", "São Miguel do Iguaçu", "Medianeira"
        ]
    },
    "RAJ 6 - Cascavel": {
        "sede": "Cascavel",
        "comarcas": [
            "Cascavel", "Assis Chateaubriand", "Campina da Lagoa", "Capanema",
            "Capitão Leônidas Marques", "Catanduvas", "Corbélia", "Formosa do Oeste",
            "Guaraniaçu", "Mamborê", "Marechal Cândido Rondon", "Nova Aurora",
            "Palotina", "Quedas do Iguaçu", "Toledo", "Ubiratã"
        ]
    },
    "RAJ 7 - Umuarama": {
        "sede": "Umuarama",
        "comarcas": [
            "Umuarama", "Alto Paraná", "Alto Piquiri", "Altônia", "Cianorte", "Cidade Gaúcha",
            "Cruzeiro do Oeste", "Goioerê", "Guaíra", "Icaraíma", "Iporã", "Loanda",
            "Nova Londrina", "Paraíso do Norte", "Paranavaí", "Pérola", "Santa Isabel do Ivaí",
            "Terra Rica", "Terra Roxa", "Xambrê"
        ]
    },
    "RAJ 8 - Maringá": {
        "sede": "Maringá",
        "comarcas": [
            "Maringá", "Astorga", "Barbosa Ferraz", "Campo Mourão", "Centenário do Sul",
            "Colorado", "Engenheiro Beltrão", "Jaguapitã", "Jandaia do Sul", "Mandaguaçu",
            "Mandaguari", "Marialva", "Nova Esperança", "Paiçandu", "Paranacity",
            "Peabiru", "Santa Fé", "São João do Ivaí", "Sarandi", "Terra Boa"
        ]
    },
    "RAJ 9 - Londrina": {
        "sede": "Londrina",
        "comarcas": [
            "Londrina", "Congonhinhas", "Faxinal", "Grandes Rios", "Marilândia do Sul",
            "Nova Fátima", "Ortigueira", "Primeiro de Maio", "São Jerônimo da Serra",
            "Sertanópolis", "Uraí", "Apucarana", "Arapongas", "Assaí", "Bela Vista do Paraíso",
            "Cambé", "Cornélio Procópio", "Ibiporã", "Porecatu", "Rolândia"
        ]
    },
    "RAJ 10 - Jacarezinho": {
        "sede": "Jacarezinho",
        "comarcas": [
            "Jacarezinho", "Arapoti", "Cambará", "Carlópolis", "Curiúva", "Joaquim Távora",
            "Ribeirão Claro", "Ribeirão do Pinhal", "Santa Mariana", "Siqueira Campos",
            "Tomazina", "Andirá", "Bandeirantes", "Ibaiti", "Santo Antônio da Platina",
            "Wenceslau Braz"
        ]
    }
}

def normalizar_comarca(nome):
    """Normaliza nome de comarca para comparação"""
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


def obter_raj_da_comarca(comarca):
    """Retorna a RAJ de uma comarca"""
    comarca_norm = normalizar_comarca(comarca)
    
    for raj_nome, raj_info in RAJS.items():
        for c in raj_info["comarcas"]:
            if normalizar_comarca(c).lower() == comarca_norm.lower():
                return raj_nome
    
    return "Não identificada"


# =============================================================================
# FUNÇÕES DE LOTAÇÃO PARADIGMA
# =============================================================================

def obter_status_lotacao(codigo_unidade):
    """Retorna o status de lotação de uma unidade (SUPERAVITÁRIA, EQUILIBRADA, DEFICITÁRIA)"""
    if codigo_unidade in LOTACAO_POR_CODIGO:
        return LOTACAO_POR_CODIGO[codigo_unidade]["status"]
    return "NÃO IDENTIFICADA"

def obter_dados_lotacao(codigo_unidade):
    """Retorna todos os dados de lotação de uma unidade"""
    if codigo_unidade in LOTACAO_POR_CODIGO:
        return LOTACAO_POR_CODIGO[codigo_unidade]
    return None

def calcular_lotacao_dinamica(codigo_unidade, ajuste=0):
    """
    Calcula a lotação considerando ajustes dinâmicos.
    ajuste: número de servidores a adicionar (+) ou remover (-)
    """
    dados = obter_dados_lotacao(codigo_unidade)
    if not dados:
        return None
    
    nova_lotacao_real = dados["lotacao_real"] + ajuste
    nova_diferenca = nova_lotacao_real - dados["lotacao_paradigma"]
    
    if nova_diferenca > 0:
        novo_status = "SUPERAVITÁRIA"
    elif nova_diferenca == 0:
        novo_status = "EQUILIBRADA"
    else:
        novo_status = "DEFICITÁRIA"
    
    return {
        "lotacao_real": nova_lotacao_real,
        "lotacao_paradigma": dados["lotacao_paradigma"],
        "diferenca": nova_diferenca,
        "status": novo_status
    }


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
        registros = sheet.get_all_records()
        linha_existente = None
        
        for i, reg in enumerate(registros, start=2):
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
            sheet.update(f"A{linha_existente}:G{linha_existente}", [valores])
        else:
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
# LÓGICA DE SIMULAÇÃO COM LOTAÇÃO DINÂMICA
# =============================================================================

def verificar_estagio_probatorio(data_admissao):
    """Verifica se servidor está em estágio probatório"""
    if data_admissao is None:
        return True
    return data_admissao > DATA_LIMITE_ESTAGIO


def calcular_resultado(df_inscricoes):
    """
    Calcula o resultado da simulação com lotação dinâmica.
    Inclui cálculo de "Designação na Origem" baseado no status da unidade.
    """
    if df_inscricoes.empty:
        return pd.DataFrame(), {}, {}, {}
    
    df = df_inscricoes.copy()
    df = df.sort_values("data_admissao", ascending=True).reset_index(drop=True)
    
    df["posicao_antiguidade"] = range(1, len(df) + 1)
    df["status"] = ""
    df["resultado"] = ""
    df["vaga_obtida"] = ""
    df["observacao"] = ""
    df["designacao_origem"] = ""
    df["status_origem_inicial"] = ""
    df["status_origem_final"] = ""
    
    # Marcar desclassificados por estágio probatório
    for idx, row in df.iterrows():
        if verificar_estagio_probatorio(row["data_admissao"]):
            df.at[idx, "status"] = "DESCLASSIFICADO"
            df.at[idx, "resultado"] = "Estágio Probatório"
            df.at[idx, "observacao"] = f"Admitido após {DATA_LIMITE_ESTAGIO.strftime('%d/%m/%Y')}"
            df.at[idx, "designacao_origem"] = "-"
    
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
                df.at[idx, "resultado"] = "ANEXO I"
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
                        if dados_origem_final["status"] == "SUPERAVITÁRIA":
                            df.at[idx, "designacao_origem"] = "NÃO"
                        else:
                            df.at[idx, "designacao_origem"] = "SIM"
                    
                    # Liberar vaga no Anexo II
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
    for idx in servidores_para_anexo2:
        row = df.loc[idx]
        escolha_a2 = row["escolha_anexo2"]
        lotacao_origem = row["lotacao_atual"]
        
        # Registrar status inicial da origem (se ainda não registrado)
        if lotacao_origem and not df.at[idx, "status_origem_inicial"]:
            dados_origem = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao.get(lotacao_origem, 0))
            if dados_origem:
                df.at[idx, "status_origem_inicial"] = dados_origem["status"]
        
        if escolha_a2 and escolha_a2 in vagas_anexo2:
            if vagas_anexo2[escolha_a2] > 0:
                vagas_anexo2[escolha_a2] -= 1
                df.at[idx, "status"] = "APROVADO"
                df.at[idx, "resultado"] = "ANEXO II"
                df.at[idx, "vaga_obtida"] = f"{ANEXO_II[escolha_a2]['comarca']} - {ANEXO_II[escolha_a2]['unidade']}"
                
                # Atualizar ajustes de lotação
                if lotacao_origem and lotacao_origem != escolha_a2:
                    # Servidor sai da origem (-1)
                    ajustes_lotacao[lotacao_origem] = ajustes_lotacao.get(lotacao_origem, 0) - 1
                    
                    # Calcular status final da origem após saída
                    dados_origem_final = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao[lotacao_origem])
                    if dados_origem_final:
                        df.at[idx, "status_origem_final"] = dados_origem_final["status"]
                        
                        # Determinar se precisa designação na origem
                        if dados_origem_final["status"] == "SUPERAVITÁRIA":
                            df.at[idx, "designacao_origem"] = "NÃO"
                        else:
                            df.at[idx, "designacao_origem"] = "SIM"
                    
                    # Liberar vaga no Anexo II
                    if lotacao_origem in vagas_anexo2:
                        vagas_anexo2[lotacao_origem] += 1
                    else:
                        vagas_anexo2[lotacao_origem] = 1
                else:
                    df.at[idx, "designacao_origem"] = "-"
            else:
                df.at[idx, "status"] = "NÃO OBTEVE VAGA"
                df.at[idx, "resultado"] = "Sem vaga"
                df.at[idx, "observacao"] = "Vaga do Anexo II não disponível"
                df.at[idx, "designacao_origem"] = "-"
        elif escolha_a2 and escolha_a2 in ANEXO_II:
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"
            df.at[idx, "resultado"] = "Sem vaga"
            df.at[idx, "observacao"] = "Vaga do Anexo II não foi liberada"
            df.at[idx, "designacao_origem"] = "-"
        elif escolha_a2:
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"
            df.at[idx, "resultado"] = "Sem vaga"
            df.at[idx, "observacao"] = "Código Anexo II inválido"
            df.at[idx, "designacao_origem"] = "-"
        else:
            df.at[idx, "status"] = "NÃO OBTEVE VAGA"
            df.at[idx, "resultado"] = "Sem vaga"
            df.at[idx, "observacao"] = "Não escolheu Anexo II"
            df.at[idx, "designacao_origem"] = "-"
    
    return df, vagas_anexo1, vagas_anexo2, ajustes_lotacao


# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================

def main():
    st.title("⚖️ Simulador de Relotação - TJPR")
    st.caption("Edital nº 4/2025 - Técnico Judiciário")
    
    # Botão de logout no sidebar
    with st.sidebar:
        st.success(f"✅ Conectado")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.telefone_usuario = None
            st.rerun()
    
    sheet = conectar_sheets()
    df_inscricoes = carregar_inscricoes(sheet)
    
    # Criar abas (agora com 7 abas)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Vagas Anexo I", 
        "📋 Vagas Anexo II", 
        "✍️ Inscrição",
        "👥 Servidores Inscritos", 
        "🏆 Resultado",
        "🗺️ Inscritos por RAJ",
        "📈 Lotação das Unidades"
    ])
    
    # =========================================================================
    # ABA 1: VAGAS ANEXO I
    # =========================================================================
    with tab1:
        st.header("Vagas com Déficit (Anexo I)")
        st.info("Estas são as vagas prioritárias com déficit de servidores. A quantidade indica o número de posições disponíveis.")
        
        dados_a1 = []
        for codigo, info in ANEXO_I.items():
            dados_a1.append({
                "Código": codigo,
                "Comarca": info["comarca"],
                "Unidade Judiciária": info["unidade"],
                "Vagas": info["quantidade"]
            })
        
        df_a1 = pd.DataFrame(dados_a1)
        
        comarcas_a1 = sorted(df_a1["Comarca"].unique())
        filtro_comarca_a1 = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_a1, key="filtro_a1")
        
        if filtro_comarca_a1 != "Todas":
            df_a1 = df_a1[df_a1["Comarca"] == filtro_comarca_a1]
        
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
        
        dados_a2 = []
        for codigo, info in ANEXO_II.items():
            # Adicionar status de lotação
            status_lot = obter_status_lotacao(codigo)
            dados_a2.append({
                "Código": codigo,
                "Comarca": info["comarca"],
                "Unidade Judiciária": info["unidade"],
                "Status Lotação": status_lot
            })
        
        df_a2 = pd.DataFrame(dados_a2)
        
        comarcas_a2 = sorted(df_a2["Comarca"].unique())
        filtro_comarca_a2 = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_a2, key="filtro_a2")
        
        if filtro_comarca_a2 != "Todas":
            df_a2 = df_a2[df_a2["Comarca"] == filtro_comarca_a2]
        
        # Filtro por status de lotação
        filtro_status = st.selectbox("Filtrar por status de lotação:", 
                                      ["Todos", "SUPERAVITÁRIA", "EQUILIBRADA", "DEFICITÁRIA", "NÃO IDENTIFICADA"],
                                      key="filtro_status_a2")
        if filtro_status != "Todos":
            df_a2 = df_a2[df_a2["Status Lotação"] == filtro_status]
        
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
            use_container_width=True, 
            hide_index=True
        )
        st.caption(f"Total: {len(df_a2)} unidades")
    
    # =========================================================================
    # ABA 3: INSCRIÇÃO
    # =========================================================================
    with tab3:
        st.header("Inscrição / Edição")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Nova Inscrição ou Edição")
            
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
                
                if data_admissao and data_admissao > DATA_LIMITE_ESTAGIO:
                    st.warning(f"⚠️ Servidor em ESTÁGIO PROBATÓRIO (admitido após {DATA_LIMITE_ESTAGIO.strftime('%d/%m/%Y')}). Será desclassificado conforme edital.")
                
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
                
                opcoes_a1 = ["(Não escolheu)"] + [f"{k} - {v['comarca']} - {v['unidade']} ({v['quantidade']} vagas)" for k, v in ANEXO_I.items()]
                
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
                
                opcoes_a2 = ["(Não escolheu)"] + [f"{k} - {v['comarca']} - {v['unidade']}" for k, v in ANEXO_II.items()]
                
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
                        codigo_lotacao = lotacao_atual.split(" - ")[0] if lotacao_atual else ""
                        codigo_escolha_a1 = escolha_a1.split(" - ")[0] if escolha_a1 != "(Não escolheu)" else ""
                        codigo_escolha_a2 = escolha_a2.split(" - ")[0] if escolha_a2 != "(Não escolheu)" else ""
                        
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
            df_inscricoes = carregar_inscricoes(sheet)
            
            df_display = df_inscricoes.sort_values("data_admissao", ascending=True).reset_index(drop=True)
            df_display["posicao"] = range(1, len(df_display) + 1)
            
            df_display["data_admissao_fmt"] = df_display["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if x else ""
            )
            
            df_display["estagio_probatorio"] = df_display["data_admissao"].apply(
                lambda x: "⚠️ SIM" if x and x > DATA_LIMITE_ESTAGIO else "Não"
            )
            
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
            
            st.dataframe(
                df_display[[
                    "posicao", "nome", "matricula", "data_admissao_fmt", 
                    "estagio_probatorio", "status_origem", "lotacao_desc", "escolha_a1_desc", "escolha_a2_desc"
                ]].rename(columns={
                    "posicao": "Pos.",
                    "nome": "Nome",
                    "matricula": "Matrícula",
                    "data_admissao_fmt": "Data Admissão",
                    "estagio_probatorio": "Est. Probatório",
                    "status_origem": "Status Origem",
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
            df_resultado, vagas_restantes_a1, vagas_disponiveis_a2, ajustes_lotacao = calcular_resultado(df_inscricoes)
            
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(df_resultado)
            aprovados_a1 = len(df_resultado[df_resultado["resultado"] == "ANEXO I"])
            aprovados_a2 = len(df_resultado[df_resultado["resultado"] == "ANEXO II"])
            desclass = len(df_resultado[df_resultado["status"] == "DESCLASSIFICADO"])
            
            # Contar designações na origem
            com_designacao = len(df_resultado[df_resultado["designacao_origem"] == "SIM"])
            
            col1.metric("Total Inscritos", total)
            col2.metric("Aprovados Anexo I", aprovados_a1)
            col3.metric("Aprovados Anexo II", aprovados_a2)
            col4.metric("Com Designação na Origem", com_designacao, help="Aprovados que precisarão aguardar substituição")
            
            st.divider()
            
            # Explicação sobre Designação na Origem
            with st.expander("ℹ️ O que significa 'Designação na Origem'?"):
                st.markdown("""
                **Baseado nos itens 3.14, 3.15 e 3.16 do Edital:**
                
                | Designação | Significado |
                |------------|-------------|
                | **NÃO** | O servidor sai de unidade **SUPERAVITÁRIA**. Pode ir embora imediatamente para a nova unidade. Relotação definitiva! ✅ |
                | **SIM** | O servidor sai de unidade **EQUILIBRADA ou DEFICITÁRIA**. A saída cria/aumenta déficit. O servidor é oficialmente relotado, MAS fica designado para continuar trabalhando na unidade antiga até: (1) um concursado tomar posse lá, OU (2) outro servidor ser relotado para lá. ⚠️ |
                
                **⚠️ ATENÇÃO (item 3.15):** Se não vier substituição até o prazo de vigência do concurso, a relotação é **tornada sem efeito** e o servidor **retorna à unidade de lotação originária**.
                """)
            
            st.subheader("📊 Resultado por Ordem de Antiguidade")
            
            df_resultado["data_admissao_fmt"] = df_resultado["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if x else ""
            )
            
            df_exibir = df_resultado[[
                "posicao_antiguidade", "nome", "matricula", "data_admissao_fmt",
                "status", "resultado", "vaga_obtida", "designacao_origem", "observacao"
            ]].rename(columns={
                "posicao_antiguidade": "Pos.",
                "nome": "Nome",
                "matricula": "Matrícula",
                "data_admissao_fmt": "Data Admissão",
                "status": "Status",
                "resultado": "Resultado",
                "vaga_obtida": "Vaga Obtida",
                "designacao_origem": "Designação Origem",
                "observacao": "Observação"
            })
            
            def highlight_status(row):
                if row["Status"] == "APROVADO":
                    if row["Designação Origem"] == "SIM":
                        return ["background-color: #fff3cd"] * len(row)  # Amarelo - aprovado com ressalva
                    return ["background-color: #d4edda"] * len(row)  # Verde
                elif row["Status"] == "DESCLASSIFICADO":
                    return ["background-color: #f8d7da"] * len(row)  # Vermelho
                elif row["Status"] == "NÃO OBTEVE VAGA":
                    return ["background-color: #e2e3e5"] * len(row)  # Cinza
                return [""] * len(row)
            
            st.dataframe(
                df_exibir.style.apply(highlight_status, axis=1),
                use_container_width=True,
                hide_index=True
            )
            
            # Legenda de cores
            st.markdown("""
            **Legenda:** 🟢 Aprovado sem restrição | 🟡 Aprovado com designação na origem | 🔴 Desclassificado | ⚪ Não obteve vaga
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
    
    # =========================================================================
    # ABA 6: INSCRITOS POR RAJ
    # =========================================================================
    with tab6:
        st.header("🗺️ Inscritos por Região Administrativa Judiciária (RAJ)")
        st.info("Análise dos candidatos **APROVADOS** por região de **ORIGEM** (lotação atual). Criada pela Resolução nº 409/2024 do TJPR.")
        
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
                    use_container_width=True,
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
                    lambda x: x.strftime("%d/%m/%Y") if x else ""
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
                
                st.dataframe(df_exibir_raj, use_container_width=True, hide_index=True)
                st.caption(f"Total de aprovados exibidos: {len(df_filtrado)}")
    
    # =========================================================================
    # ABA 7: LOTAÇÃO DAS UNIDADES
    # =========================================================================
    with tab7:
        st.header("📈 Lotação das Unidades Judiciárias")
        st.info("Dados da Tabela de Lotação de Pessoal (TLP) - 2º Semestre 2025. Fonte: BI do TJPR.")
        
        # Explicação
        with st.expander("ℹ️ Como interpretar os dados"):
            st.markdown("""
            **Colunas:**
            - **Lotação Real**: Total de servidores atualmente lotados (Efetivos + Sem Vínculo + Cedidos/Requisitados)
            - **Lotação Paradigma**: Mínimo de servidores necessários segundo a Resolução CNJ 219/2016
            - **Diferença**: Lotação Real - Lotação Paradigma
            
            **Status:**
            - 🟢 **SUPERAVITÁRIA**: Mais servidores que o necessário. Servidor pode sair sem restrição.
            - 🟡 **EQUILIBRADA**: Exatamente o necessário. Saída gera déficit.
            - 🔴 **DEFICITÁRIA**: Menos servidores que o necessário. Saída agrava déficit.
            
            **Impacto na Relotação (itens 3.14 a 3.16 do Edital):**
            - Servidores de unidades **SUPERAVITÁRIAS** são relotados imediatamente.
            - Servidores de unidades **EQUILIBRADAS ou DEFICITÁRIAS** ficam designados na origem até substituição.
            """)
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        total_unidades = len(LOTACAO_COMPLETA)
        superavit = len([u for u in LOTACAO_COMPLETA if u["status"] == "SUPERAVITÁRIA"])
        equilibrada = len([u for u in LOTACAO_COMPLETA if u["status"] == "EQUILIBRADA"])
        deficit = len([u for u in LOTACAO_COMPLETA if u["status"] == "DEFICITÁRIA"])
        
        col1.metric("Total de Unidades", total_unidades)
        col2.metric("Superavitárias", superavit, delta=None)
        col3.metric("Equilibradas", equilibrada, delta=None)
        col4.metric("Deficitárias", deficit, delta=None, delta_color="inverse")
        
        st.divider()
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            comarcas_lot = sorted(set([u["comarca"] for u in LOTACAO_COMPLETA]))
            filtro_comarca_lot = st.selectbox("Filtrar por comarca:", ["Todas"] + comarcas_lot, key="filtro_comarca_lot")
        
        with col2:
            filtro_status_lot = st.selectbox("Filtrar por status:", 
                                              ["Todos", "SUPERAVITÁRIA", "EQUILIBRADA", "DEFICITÁRIA"],
                                              key="filtro_status_lot")
        
        busca_lot = st.text_input("🔍 Buscar:", key="busca_lot", placeholder="Digite parte do nome da comarca ou unidade...")
        
        # Preparar dados
        dados_lot = []
        for u in LOTACAO_COMPLETA:
            # Aplicar filtros
            if filtro_comarca_lot != "Todas" and u["comarca"] != filtro_comarca_lot:
                continue
            if filtro_status_lot != "Todos" and u["status"] != filtro_status_lot:
                continue
            if busca_lot:
                if busca_lot.lower() not in u["comarca"].lower() and busca_lot.lower() not in u["unidade"].lower():
                    continue
            
            dados_lot.append({
                "Comarca": u["comarca"],
                "Unidade Judiciária": u["unidade"],
                "Lotação Real": u["lotacao_real"],
                "Lotação Paradigma": u["lotacao_paradigma"],
                "Diferença": u["diferenca"],
                "Status": u["status"]
            })
        
        df_lot = pd.DataFrame(dados_lot)
        
        if not df_lot.empty:
            def color_status_lot(val):
                if val == "SUPERAVITÁRIA":
                    return "background-color: #d4edda"
                elif val == "EQUILIBRADA":
                    return "background-color: #fff3cd"
                elif val == "DEFICITÁRIA":
                    return "background-color: #f8d7da"
                return ""
            
            def color_diferenca(val):
                if val > 0:
                    return "color: green; font-weight: bold"
                elif val < 0:
                    return "color: red; font-weight: bold"
                return ""
            
            st.dataframe(
                df_lot.style.applymap(color_status_lot, subset=["Status"])
                           .applymap(color_diferenca, subset=["Diferença"]),
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Exibindo {len(df_lot)} de {total_unidades} unidades")
        else:
            st.warning("Nenhuma unidade encontrada com os filtros selecionados.")


# =============================================================================
# FOOTER
# =============================================================================

def footer():
    st.divider()
    st.caption("""
    ⚠️ **ATENÇÃO:** Este é um simulador não oficial, criado apenas para auxiliar na tomada de decisão. 
    O resultado oficial depende exclusivamente da análise do TJPR conforme Edital nº 4/2025.
    """)


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        tela_login()
    else:
        main()
        footer()
