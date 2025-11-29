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
from io import BytesIO
import unicodedata

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

# Data limite para estágio probatório (3 anos antes de 26/11/2025)
DATA_LIMITE_ESTAGIO = date(2022, 11, 26)

# =============================================================================
# ADMINISTRADORES DO SISTEMA
# =============================================================================

# Telefones com acesso ao painel administrativo
ADMIN_TELEFONES = [
    "41997813606",  # Admin principal
]

# Senha de acesso ao painel admin (além do telefone)
ADMIN_SENHA = "TJPR-F4F1X5"

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
    "41988505079": "TJPR-L2C5O6",
}

# =============================================================================
# FUNÇÕES DE AUTENTICAÇÃO
# =============================================================================

def formatar_telefone_display(telefone):
    """Formata telefone para exibição: (XX) XXXXX-XXXX"""
    numeros = re.sub(r'\D', '', str(telefone))
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

def limpar_telefone(telefone):
    """Remove tudo que não for número do telefone"""
    return re.sub(r'\D', '', str(telefone))

def verificar_login(telefone, codigo):
    """Verifica se telefone e código são válidos"""
    telefone_limpo = limpar_telefone(telefone)
    codigo_upper = codigo.upper().strip()
    
    if telefone_limpo in AUTH_CODES:
        return AUTH_CODES[telefone_limpo] == codigo_upper
    return False

def get_usuario_logado():
    """Retorna o telefone formatado do usuário logado"""
    if "telefone_usuario" in st.session_state and st.session_state.telefone_usuario:
        return formatar_telefone_display(st.session_state.telefone_usuario)
    return "Desconhecido"

def tela_login():
    """Exibe a tela de login"""
    st.title("⚖️ Simulador de Relotação - TJPR")
    st.caption("Edital nº 4/2025 - Técnico Judiciário")
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Acesso Restrito")
        st.info("Este simulador é exclusivo para membros autorizados. Informe seu telefone e código de acesso.")
        
        telefone_input = st.text_input(
            "📱 Telefone com DDD:",
            placeholder="41999999999",
            help="Digite apenas os números (DDD + telefone)",
            key="telefone_login",
            max_chars=11
        )
        
        # Mostrar preview formatado em tempo real
        if telefone_input:
            telefone_numeros = limpar_telefone(telefone_input)
            telefone_formatado = formatar_telefone_display(telefone_numeros)
            if telefone_formatado:
                st.caption(f"📞 {telefone_formatado}")
        
        codigo = st.text_input(
            "🔑 Código de Acesso:",
            placeholder="TJPR-XXXXXX",
            help="Código enviado por WhatsApp, ex: TJPR-A1B2C3"
        )
        
        if st.button("🚀 Entrar", use_container_width=True):
            telefone_numeros = limpar_telefone(telefone_input)
            if not telefone_numeros or not codigo:
                st.error("Preencha o telefone e o código!")
            elif len(telefone_numeros) < 10:
                st.error("Telefone inválido! Digite DDD + número (mínimo 10 dígitos).")
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


def salvar_inscricao(sheet, dados, telefone_usuario):
    """Salva ou atualiza uma inscrição, registrando quem fez a operação"""
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
        
        # Formatar telefone do usuário para o log
        telefone_formatado = formatar_telefone_display(telefone_usuario) if telefone_usuario else "Desconhecido"
        data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        if linha_existente and registro_antigo:
            # Atualização - manter registrado_por original, atualizar alterado_por
            registrado_por = registro_antigo.get("registrado_por", telefone_formatado) or telefone_formatado
            valores = [
                dados["nome"],
                dados["matricula"],
                dados["data_admissao"],
                dados["lotacao_atual"],
                dados["escolha_anexo1"],
                dados["escolha_anexo2"],
                dados["data_inscricao"],
                registrado_por,           # H: manter original
                telefone_formatado,       # I: quem alterou
                data_hora_atual           # J: quando alterou
            ]
            sheet.update(f"A{linha_existente}:J{linha_existente}", [valores])
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
                telefone_formatado,       # H: quem registrou
                telefone_formatado,       # I: quem alterou (mesmo, pois é novo)
                data_hora_atual           # J: quando
            ]
            sheet.append_row(valores)
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False


def excluir_inscricao(sheet, matricula, telefone_usuario):
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
                        # Conforme item 3.14 do Edital: designação apenas se a saída OCASIONAR DÉFICIT
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
                        # Conforme item 3.14 do Edital: designação apenas se a saída OCASIONAR DÉFICIT
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


def gerar_excel_resultado(df_resultado):
    """
    Gera um arquivo Excel com o resultado da simulação.
    Retorna bytes do arquivo para download.
    """
    output = BytesIO()
    
    # Preparar DataFrame para exportação
    df_export = df_resultado[[
        "posicao_antiguidade", "nome", "matricula", "data_admissao",
        "status", "resultado", "vaga_obtida", "designacao_origem", "observacao"
    ]].copy()
    
    # Formatar data
    df_export["data_admissao"] = df_export["data_admissao"].apply(
        lambda x: x.strftime("%d/%m/%Y") if x else ""
    )
    
    # Renomear colunas
    df_export.columns = [
        "Posição", "Nome", "Matrícula", "Data Admissão",
        "Status", "Resultado", "Vaga Obtida", "Designação Origem", "Observação"
    ]
    
    # Criar Excel com pandas
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Resultado Simulação', index=False)
    
    output.seek(0)
    return output.getvalue()


def gerar_excel_inscricoes(df_inscricoes):
    """
    Gera um arquivo Excel com todas as inscrições.
    """
    output = BytesIO()
    
    df_export = df_inscricoes.copy()
    
    # Formatar data
    if "data_admissao" in df_export.columns:
        df_export["data_admissao"] = df_export["data_admissao"].apply(
            lambda x: x.strftime("%d/%m/%Y") if x else ""
        )
    
    # Adicionar descrições das unidades
    df_export["lotacao_desc"] = df_export["lotacao_atual"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x in ANEXO_II else x
    )
    df_export["escolha_a1_desc"] = df_export["escolha_anexo1"].apply(
        lambda x: f"{ANEXO_I[x]['comarca']} - {ANEXO_I[x]['unidade']}" if x and x in ANEXO_I else "-"
    )
    df_export["escolha_a2_desc"] = df_export["escolha_anexo2"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
    )
    
    # Criar Excel com pandas
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Inscrições', index=False)
    
    output.seek(0)
    return output.getvalue()


def gerar_excel_logs(df_inscricoes):
    """
    Gera um arquivo Excel com logs de alterações.
    """
    output = BytesIO()
    
    colunas_log = ["nome", "matricula", "registrado_por", "alterado_por", "data_alteracao", "data_inscricao"]
    df_export = df_inscricoes[[c for c in colunas_log if c in df_inscricoes.columns]].copy()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Logs de Alterações', index=False)
    
    output.seek(0)
    return output.getvalue()


def is_admin():
    """Verifica se o usuário logado é administrador."""
    if "telefone_usuario" in st.session_state and st.session_state.telefone_usuario:
        return st.session_state.telefone_usuario in ADMIN_TELEFONES
    return False


def normalizar_nome(nome):
    """
    Normaliza um nome para comparação:
    - Remove acentos
    - Converte para minúsculas
    - Remove espaços extras
    """
    if not nome:
        return ""
    # Remove acentos
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_normalizado = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    # Converte para minúsculas e remove espaços extras
    nome_normalizado = ' '.join(nome_normalizado.lower().split())
    return nome_normalizado


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
    Compara os dados do CSV oficial com as inscrições do simulador.
    Retorna dicionário com resultados da comparação.
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
    
    # 4. Criar set de nomes normalizados do simulador
    if not df_inscricoes.empty:
        df_inscricoes['nome_normalizado'] = df_inscricoes['nome'].apply(normalizar_nome)
        nomes_simulador = set(df_inscricoes['nome_normalizado'].unique())
        nomes_simulador_dict = dict(zip(df_inscricoes['nome_normalizado'], df_inscricoes['nome']))
        matriculas_dict = dict(zip(df_inscricoes['nome_normalizado'], df_inscricoes['matricula']))
    else:
        nomes_simulador = set()
        nomes_simulador_dict = {}
        matriculas_dict = {}
    
    nomes_csv_finalizados = set(servidores_finalizados['servidor_normalizado'].unique())
    
    # 5. Comparar
    # Coincidentes
    coincidentes = nomes_csv_finalizados & nomes_simulador
    for nome_norm in coincidentes:
        servidor_csv = servidores_finalizados[servidores_finalizados['servidor_normalizado'] == nome_norm].iloc[0]
        resultados['coincidentes'].append({
            'nome_csv': servidor_csv['servidor'],
            'nome_simulador': nomes_simulador_dict.get(nome_norm, ''),
            'matricula': matriculas_dict.get(nome_norm, ''),
            'vagas_csv': servidor_csv['vaga']
        })
    
    # Faltam no simulador
    faltam = nomes_csv_finalizados - nomes_simulador
    for nome_norm in faltam:
        servidor_csv = servidores_finalizados[servidores_finalizados['servidor_normalizado'] == nome_norm].iloc[0]
        
        # Tentar fazer match com Anexo II
        vagas_match = []
        for vaga in servidor_csv['vaga']:
            codigo, score = tentar_match_anexo2(vaga)
            vagas_match.append({
                'vaga_csv': vaga,
                'codigo_anexo2': codigo,
                'score': score,
                'unidade_anexo2': f"{ANEXO_II[codigo]['comarca']} - {ANEXO_II[codigo]['unidade']}" if codigo else None
            })
        
        resultados['faltam_simulador'].append({
            'nome': servidor_csv['servidor'],
            'nome_normalizado': nome_norm,
            'vagas': vagas_match,
            'data': servidor_csv['data']
        })
    
    # Remover do simulador (estão no simulador mas não finalizaram no CSV)
    remover = nomes_simulador - nomes_csv_finalizados
    for nome_norm in remover:
        # Verificar se está no CSV mas não finalizou
        if nome_norm in servidores_todos:
            motivo = "Inscrição NÃO FINALIZADA no edital oficial"
        else:
            motivo = "NÃO ENCONTRADO no edital oficial"
        
        resultados['remover_simulador'].append({
            'nome': nomes_simulador_dict.get(nome_norm, ''),
            'matricula': matriculas_dict.get(nome_norm, ''),
            'motivo': motivo
        })
    
    return resultados


def painel_administrador(sheet, df_inscricoes):
    """Exibe o painel de administração completo."""
    
    st.title("🔐 Painel Administrativo")
    st.caption("Acesso restrito a administradores do sistema")
    
    # Verificar senha de admin
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False
    
    if not st.session_state.admin_autenticado:
        st.warning("⚠️ Digite a senha de administrador para acessar este painel.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha_admin = st.text_input("Senha de Administrador:", type="password", key="senha_admin_input")
            
            if st.button("🔓 Acessar Painel Admin", use_container_width=True):
                if senha_admin == ADMIN_SENHA:
                    st.session_state.admin_autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        return
    
    # Botão de sair do painel admin
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔒 Sair do Admin", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.session_state.modo_admin = False
            st.rerun()
    
    st.divider()
    
    # Abas do painel admin
    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5, admin_tab6, admin_tab7 = st.tabs([
        "📊 Visão Geral",
        "👥 Usuários",
        "📝 Inscrições",
        "📋 Logs",
        "📥 Exportar",
        "📤 Comparar Edital",
        "⚙️ Configurações"
    ])
    
    # =========================================================================
    # ABA ADMIN 1: VISÃO GERAL
    # =========================================================================
    with admin_tab1:
        st.header("📊 Visão Geral do Sistema")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        total_usuarios = len(AUTH_CODES)
        total_inscricoes = len(df_inscricoes)
        
        # Calcular usuários ativos (que fizeram login - aproximação pelos registros)
        usuarios_ativos = set()
        if not df_inscricoes.empty and "registrado_por" in df_inscricoes.columns:
            usuarios_ativos.update(df_inscricoes["registrado_por"].dropna().unique())
            if "alterado_por" in df_inscricoes.columns:
                usuarios_ativos.update(df_inscricoes["alterado_por"].dropna().unique())
        usuarios_ativos = len([u for u in usuarios_ativos if u and u != "Desconhecido"])
        
        col1.metric("👥 Usuários Cadastrados", total_usuarios)
        col2.metric("✅ Usuários Ativos", usuarios_ativos, help="Usuários que registraram/alteraram inscrições")
        col3.metric("📝 Total de Inscrições", total_inscricoes)
        col4.metric("🔐 Administradores", len(ADMIN_TELEFONES))
        
        st.divider()
        
        # Resultados da simulação
        if not df_inscricoes.empty:
            df_resultado, _, _, _ = calcular_resultado(df_inscricoes)
            
            st.subheader("🏆 Resumo dos Resultados")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            aprovados = len(df_resultado[df_resultado["status"] == "APROVADO"])
            anexo1 = len(df_resultado[df_resultado["resultado"] == "ANEXO I"])
            anexo2 = len(df_resultado[df_resultado["resultado"] == "ANEXO II"])
            desclass = len(df_resultado[df_resultado["status"] == "DESCLASSIFICADO"])
            sem_vaga = len(df_resultado[df_resultado["status"] == "NÃO OBTEVE VAGA"])
            
            col1.metric("✅ Aprovados", aprovados, f"{100*aprovados/total_inscricoes:.1f}%" if total_inscricoes > 0 else "0%")
            col2.metric("📋 Anexo I", anexo1)
            col3.metric("📋 Anexo II", anexo2)
            col4.metric("❌ Desclassificados", desclass)
            col5.metric("⚪ Sem Vaga", sem_vaga)
            
            # Designação na origem
            st.divider()
            st.subheader("📍 Designação na Origem")
            
            com_designacao = len(df_resultado[df_resultado["designacao_origem"] == "SIM"])
            sem_designacao = len(df_resultado[df_resultado["designacao_origem"] == "NÃO"])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Pode ir imediatamente", sem_designacao)
            col2.metric("⚠️ Fica designado na origem", com_designacao)
            col3.metric("📊 Taxa de designação", f"{100*com_designacao/aprovados:.1f}%" if aprovados > 0 else "0%")
        
        else:
            st.info("Nenhuma inscrição registrada ainda.")
        
        # Últimas atividades
        st.divider()
        st.subheader("🕐 Últimas Atividades")
        
        if not df_inscricoes.empty and "data_alteracao" in df_inscricoes.columns:
            df_atividades = df_inscricoes[["nome", "matricula", "alterado_por", "data_alteracao"]].copy()
            df_atividades = df_atividades.dropna(subset=["data_alteracao"])
            df_atividades = df_atividades.sort_values("data_alteracao", ascending=False).head(10)
            
            if not df_atividades.empty:
                st.dataframe(
                    df_atividades.rename(columns={
                        "nome": "Servidor",
                        "matricula": "Matrícula",
                        "alterado_por": "Alterado Por",
                        "data_alteracao": "Data/Hora"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhuma atividade recente registrada.")
        else:
            st.info("Nenhuma atividade recente registrada.")
    
    # =========================================================================
    # ABA ADMIN 2: USUÁRIOS
    # =========================================================================
    with admin_tab2:
        st.header("👥 Gestão de Usuários")
        
        # Lista de usuários cadastrados
        st.subheader("📋 Usuários com Acesso ao Sistema")
        
        dados_usuarios = []
        for telefone, codigo in AUTH_CODES.items():
            telefone_fmt = formatar_telefone_display(telefone)
            is_adm = "✅ Sim" if telefone in ADMIN_TELEFONES else "Não"
            
            # Verificar se tem inscrições
            inscricoes_usuario = 0
            if not df_inscricoes.empty and "registrado_por" in df_inscricoes.columns:
                inscricoes_usuario = len(df_inscricoes[df_inscricoes["registrado_por"] == telefone_fmt])
            
            dados_usuarios.append({
                "Telefone": telefone_fmt,
                "Código": codigo,
                "Admin": is_adm,
                "Inscrições Registradas": inscricoes_usuario
            })
        
        df_usuarios = pd.DataFrame(dados_usuarios)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            busca_usuario = st.text_input("🔍 Buscar por telefone:", key="busca_usuario_admin")
        with col2:
            filtro_admin = st.selectbox("Filtrar:", ["Todos", "Apenas Admins", "Apenas Usuários"], key="filtro_admin")
        
        df_filtrado = df_usuarios.copy()
        
        if busca_usuario:
            df_filtrado = df_filtrado[df_filtrado["Telefone"].str.contains(busca_usuario, case=False)]
        
        if filtro_admin == "Apenas Admins":
            df_filtrado = df_filtrado[df_filtrado["Admin"] == "✅ Sim"]
        elif filtro_admin == "Apenas Usuários":
            df_filtrado = df_filtrado[df_filtrado["Admin"] == "Não"]
        
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df_filtrado)} usuários")
        
        st.divider()
        
        # Estatísticas de uso
        st.subheader("📊 Estatísticas de Uso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Usuários que registraram inscrições:**")
            if not df_inscricoes.empty and "registrado_por" in df_inscricoes.columns:
                contagem = df_inscricoes["registrado_por"].value_counts().head(10)
                if not contagem.empty:
                    df_contagem = pd.DataFrame({
                        "Usuário": contagem.index,
                        "Inscrições": contagem.values
                    })
                    st.dataframe(df_contagem, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum dado disponível.")
            else:
                st.info("Nenhum dado disponível.")
        
        with col2:
            st.markdown("**Usuários que mais alteraram:**")
            if not df_inscricoes.empty and "alterado_por" in df_inscricoes.columns:
                contagem = df_inscricoes["alterado_por"].value_counts().head(10)
                if not contagem.empty:
                    df_contagem = pd.DataFrame({
                        "Usuário": contagem.index,
                        "Alterações": contagem.values
                    })
                    st.dataframe(df_contagem, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum dado disponível.")
            else:
                st.info("Nenhum dado disponível.")
    
    # =========================================================================
    # ABA ADMIN 3: INSCRIÇÕES
    # =========================================================================
    with admin_tab3:
        st.header("📝 Gestão de Inscrições")
        
        if df_inscricoes.empty:
            st.info("Nenhuma inscrição registrada ainda.")
        else:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                busca_inscricao = st.text_input("🔍 Buscar por nome ou matrícula:", key="busca_inscricao_admin")
            
            with col2:
                # Filtro por status (precisa calcular resultado)
                df_resultado, _, _, _ = calcular_resultado(df_inscricoes)
                filtro_status = st.selectbox("Status:", ["Todos", "APROVADO", "DESCLASSIFICADO", "NÃO OBTEVE VAGA"], key="filtro_status_admin")
            
            with col3:
                filtro_designacao = st.selectbox("Designação:", ["Todos", "SIM", "NÃO"], key="filtro_designacao_admin")
            
            # Aplicar filtros
            df_view = df_resultado.copy()
            
            if busca_inscricao:
                mask = df_view.apply(
                    lambda x: busca_inscricao.lower() in str(x["nome"]).lower() or 
                              busca_inscricao.lower() in str(x["matricula"]).lower(), 
                    axis=1
                )
                df_view = df_view[mask]
            
            if filtro_status != "Todos":
                df_view = df_view[df_view["status"] == filtro_status]
            
            if filtro_designacao != "Todos":
                df_view = df_view[df_view["designacao_origem"] == filtro_designacao]
            
            # Formatar data
            df_view["data_admissao_fmt"] = df_view["data_admissao"].apply(
                lambda x: x.strftime("%d/%m/%Y") if x else ""
            )
            
            # Adicionar descrição das lotações
            df_view["lotacao_desc"] = df_view["lotacao_atual"].apply(
                lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade'][:30]}..." if x in ANEXO_II else x
            )
            
            # Exibir tabela
            st.dataframe(
                df_view[[
                    "posicao_antiguidade", "nome", "matricula", "data_admissao_fmt",
                    "lotacao_desc", "status", "resultado", "designacao_origem"
                ]].rename(columns={
                    "posicao_antiguidade": "Pos.",
                    "nome": "Nome",
                    "matricula": "Matrícula",
                    "data_admissao_fmt": "Admissão",
                    "lotacao_desc": "Lotação Atual",
                    "status": "Status",
                    "resultado": "Resultado",
                    "designacao_origem": "Designação"
                }),
                use_container_width=True,
                hide_index=True,
                height=500
            )
            
            st.caption(f"Exibindo: {len(df_view)} de {len(df_resultado)} inscrições")
            
            st.divider()
            
            # Detalhes de uma inscrição específica
            st.subheader("🔍 Detalhes de Inscrição")
            
            matricula_detalhe = st.text_input("Digite a matrícula para ver detalhes:", key="matricula_detalhe_admin")
            
            if matricula_detalhe:
                inscricao = df_inscricoes[df_inscricoes["matricula"].astype(str) == str(matricula_detalhe)]
                
                if inscricao.empty:
                    st.error("Matrícula não encontrada.")
                else:
                    inscricao = inscricao.iloc[0]
                    resultado = df_resultado[df_resultado["matricula"].astype(str) == str(matricula_detalhe)].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Dados Pessoais:**")
                        st.markdown(f"- **Nome:** {inscricao['nome']}")
                        st.markdown(f"- **Matrícula:** {inscricao['matricula']}")
                        st.markdown(f"- **Data Admissão:** {inscricao['data_admissao'].strftime('%d/%m/%Y') if inscricao['data_admissao'] else '-'}")
                        st.markdown(f"- **Posição por Antiguidade:** {resultado['posicao_antiguidade']}º")
                        
                        lotacao = inscricao['lotacao_atual']
                        if lotacao in ANEXO_II:
                            st.markdown(f"- **Lotação:** {ANEXO_II[lotacao]['comarca']} - {ANEXO_II[lotacao]['unidade']}")
                        else:
                            st.markdown(f"- **Lotação:** {lotacao}")
                    
                    with col2:
                        st.markdown("**Escolhas e Resultado:**")
                        
                        escolha_a1 = inscricao.get('escolha_anexo1', '')
                        if escolha_a1 and escolha_a1 in ANEXO_I:
                            st.markdown(f"- **Anexo I:** {ANEXO_I[escolha_a1]['comarca']} - {ANEXO_I[escolha_a1]['unidade']}")
                        else:
                            st.markdown("- **Anexo I:** Não escolheu")
                        
                        escolha_a2 = inscricao.get('escolha_anexo2', '')
                        if escolha_a2 and escolha_a2 in ANEXO_II:
                            st.markdown(f"- **Anexo II:** {ANEXO_II[escolha_a2]['comarca']} - {ANEXO_II[escolha_a2]['unidade']}")
                        else:
                            st.markdown("- **Anexo II:** Não escolheu")
                        
                        st.markdown(f"- **Status:** {resultado['status']}")
                        st.markdown(f"- **Resultado:** {resultado['resultado']}")
                        st.markdown(f"- **Vaga Obtida:** {resultado['vaga_obtida']}")
                        st.markdown(f"- **Designação Origem:** {resultado['designacao_origem']}")
                    
                    # Logs
                    st.markdown("**Logs de Registro:**")
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"- **Registrado por:** {inscricao.get('registrado_por', '-')}")
                    col2.markdown(f"- **Última alteração por:** {inscricao.get('alterado_por', '-')}")
                    col3.markdown(f"- **Data alteração:** {inscricao.get('data_alteracao', '-')}")
    
    # =========================================================================
    # ABA ADMIN 4: LOGS
    # =========================================================================
    with admin_tab4:
        st.header("📋 Logs de Atividades")
        
        if df_inscricoes.empty:
            st.info("Nenhum log disponível.")
        else:
            # Verificar se tem colunas de log
            tem_logs = all(col in df_inscricoes.columns for col in ["registrado_por", "alterado_por", "data_alteracao"])
            
            if not tem_logs:
                st.warning("⚠️ As colunas de log não existem nas inscrições antigas. Novos registros terão logs.")
            else:
                # Filtros de log
                col1, col2 = st.columns(2)
                
                with col1:
                    busca_log = st.text_input("🔍 Buscar por usuário ou servidor:", key="busca_log_admin")
                
                with col2:
                    ordenar_por = st.selectbox("Ordenar por:", ["Mais recentes", "Mais antigos", "Por usuário"], key="ordenar_log")
                
                # Preparar dados de log
                df_logs = df_inscricoes[["nome", "matricula", "registrado_por", "alterado_por", "data_alteracao", "data_inscricao"]].copy()
                
                # Aplicar filtro
                if busca_log:
                    mask = df_logs.apply(
                        lambda x: busca_log.lower() in str(x["nome"]).lower() or 
                                  busca_log.lower() in str(x["registrado_por"]).lower() or
                                  busca_log.lower() in str(x["alterado_por"]).lower(), 
                        axis=1
                    )
                    df_logs = df_logs[mask]
                
                # Ordenar
                if ordenar_por == "Mais recentes":
                    df_logs = df_logs.sort_values("data_alteracao", ascending=False, na_position='last')
                elif ordenar_por == "Mais antigos":
                    df_logs = df_logs.sort_values("data_alteracao", ascending=True, na_position='last')
                else:
                    df_logs = df_logs.sort_values("alterado_por", ascending=True, na_position='last')
                
                # Exibir
                st.dataframe(
                    df_logs.rename(columns={
                        "nome": "Servidor",
                        "matricula": "Matrícula",
                        "registrado_por": "Registrado Por",
                        "alterado_por": "Alterado Por",
                        "data_alteracao": "Data Alteração",
                        "data_inscricao": "Data Inscrição"
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )
                
                st.caption(f"Total: {len(df_logs)} registros")
                
                st.divider()
                
                # Análise de atividade por usuário
                st.subheader("📊 Atividade por Usuário")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Registros criados por usuário:**")
                    if "registrado_por" in df_inscricoes.columns:
                        registros = df_inscricoes["registrado_por"].value_counts()
                        st.dataframe(
                            pd.DataFrame({"Usuário": registros.index, "Registros": registros.values}),
                            use_container_width=True,
                            hide_index=True
                        )
                
                with col2:
                    st.markdown("**Alterações por usuário:**")
                    if "alterado_por" in df_inscricoes.columns:
                        alteracoes = df_inscricoes["alterado_por"].value_counts()
                        st.dataframe(
                            pd.DataFrame({"Usuário": alteracoes.index, "Alterações": alteracoes.values}),
                            use_container_width=True,
                            hide_index=True
                        )
    
    # =========================================================================
    # ABA ADMIN 5: EXPORTAR
    # =========================================================================
    with admin_tab5:
        st.header("📥 Exportar Dados")
        
        st.info("⚠️ Atenção: Estes arquivos contêm dados sensíveis. Utilize com responsabilidade.")
        
        if df_inscricoes.empty:
            st.warning("Nenhum dado para exportar.")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📝 Inscrições")
                st.markdown("Todas as inscrições com dados completos.")
                
                try:
                    excel_inscricoes = gerar_excel_inscricoes(df_inscricoes)
                    st.download_button(
                        label="📥 Baixar Inscrições",
                        data=excel_inscricoes,
                        file_name=f"inscricoes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erro: {e}")
            
            with col2:
                st.subheader("🏆 Resultados")
                st.markdown("Resultado da simulação completo.")
                
                try:
                    df_resultado, _, _, _ = calcular_resultado(df_inscricoes)
                    excel_resultado = gerar_excel_resultado(df_resultado)
                    st.download_button(
                        label="📥 Baixar Resultados",
                        data=excel_resultado,
                        file_name=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erro: {e}")
            
            with col3:
                st.subheader("📋 Logs")
                st.markdown("Histórico de registros e alterações.")
                
                try:
                    excel_logs = gerar_excel_logs(df_inscricoes)
                    st.download_button(
                        label="📥 Baixar Logs",
                        data=excel_logs,
                        file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erro: {e}")
            
            st.divider()
            
            # Exportar tudo em um arquivo
            st.subheader("📦 Exportar Tudo")
            st.markdown("Arquivo Excel com todas as abas (Inscrições, Resultados, Logs).")
            
            try:
                output = BytesIO()
                df_resultado, _, _, _ = calcular_resultado(df_inscricoes)
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Aba de inscrições
                    df_export_insc = df_inscricoes.copy()
                    if "data_admissao" in df_export_insc.columns:
                        df_export_insc["data_admissao"] = df_export_insc["data_admissao"].apply(
                            lambda x: x.strftime("%d/%m/%Y") if x else ""
                        )
                    df_export_insc.to_excel(writer, sheet_name='Inscrições', index=False)
                    
                    # Aba de resultados
                    df_export_res = df_resultado[[
                        "posicao_antiguidade", "nome", "matricula", "data_admissao",
                        "status", "resultado", "vaga_obtida", "designacao_origem", "observacao"
                    ]].copy()
                    df_export_res["data_admissao"] = df_export_res["data_admissao"].apply(
                        lambda x: x.strftime("%d/%m/%Y") if x else ""
                    )
                    df_export_res.to_excel(writer, sheet_name='Resultados', index=False)
                    
                    # Aba de logs
                    colunas_log = ["nome", "matricula", "registrado_por", "alterado_por", "data_alteracao"]
                    df_export_log = df_inscricoes[[c for c in colunas_log if c in df_inscricoes.columns]].copy()
                    df_export_log.to_excel(writer, sheet_name='Logs', index=False)
                
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Relatório Completo",
                    data=output.getvalue(),
                    file_name=f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {e}")
    
    # =========================================================================
    # ABA ADMIN 6: COMPARAR EDITAL OFICIAL
    # =========================================================================
    with admin_tab6:
        st.header("📤 Comparar com Edital Oficial")
        st.info("""
        **Instruções:**
        1. Exporte a lista de inscrições do site oficial do TJPR em formato CSV
        2. Faça upload do arquivo aqui
        3. O sistema irá comparar com as inscrições do simulador
        
        ⚠️ **Atenção:** O CSV oficial não diferencia Anexo I de Anexo II, então a revisão das escolhas deve ser manual.
        """)
        
        uploaded_file = st.file_uploader(
            "📁 Carregar CSV do Edital Oficial",
            type=['csv'],
            help="Arquivo CSV exportado do site do TJPR com a lista de inscrições"
        )
        
        if uploaded_file is not None:
            # Processar CSV
            df_csv = processar_csv_edital(uploaded_file)
            
            if df_csv is not None:
                st.success(f"✅ Arquivo carregado: {len(df_csv)} registros encontrados")
                
                # Mostrar preview do CSV
                with st.expander("📋 Visualizar dados do CSV"):
                    st.dataframe(df_csv[['servidor', 'vaga', 'situacao', 'data']].head(20), 
                                use_container_width=True, hide_index=True)
                
                st.divider()
                
                # Comparar
                if st.button("🔄 Comparar com Simulador", use_container_width=True, type="primary"):
                    with st.spinner("Comparando dados..."):
                        resultados = comparar_edital_simulador(df_csv, df_inscricoes)
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    col1.metric(
                        "✅ Coincidentes", 
                        len(resultados['coincidentes']),
                        help="Servidores que estão no edital oficial E no simulador"
                    )
                    col2.metric(
                        "⚠️ Faltam no Simulador", 
                        len(resultados['faltam_simulador']),
                        help="Servidores finalizados no edital que NÃO estão no simulador"
                    )
                    col3.metric(
                        "❌ Revisar/Remover", 
                        len(resultados['remover_simulador']),
                        help="Servidores no simulador que não finalizaram no edital"
                    )
                    col4.metric(
                        "🚫 Não Finalizaram",
                        len(resultados['csv_nao_finalizados']),
                        help="Servidores com inscrições apenas canceladas ou não concluídas"
                    )
                    
                    st.divider()
                    
                    # ========= FALTAM NO SIMULADOR =========
                    if resultados['faltam_simulador']:
                        st.subheader(f"⚠️ Servidores que FALTAM no Simulador ({len(resultados['faltam_simulador'])})")
                        st.warning("Estes servidores finalizaram inscrição no edital oficial mas NÃO estão no simulador.")
                        
                        dados_faltam = []
                        for item in resultados['faltam_simulador']:
                            # Pegar a primeira vaga com melhor match
                            vagas_str = []
                            codigos_str = []
                            for v in item['vagas']:
                                vagas_str.append(v['vaga_csv'][:60] + "..." if len(v['vaga_csv']) > 60 else v['vaga_csv'])
                                if v['codigo_anexo2']:
                                    codigos_str.append(f"{v['codigo_anexo2']} ({v['score']*100:.0f}%)")
                                else:
                                    codigos_str.append("❓ Não identificado")
                            
                            dados_faltam.append({
                                "Nome": item['nome'],
                                "Vagas Pretendidas (CSV)": " | ".join(vagas_str),
                                "Código Anexo II (tentativa)": " | ".join(codigos_str),
                                "Última Data": item['data']
                            })
                        
                        st.dataframe(
                            pd.DataFrame(dados_faltam),
                            use_container_width=True,
                            hide_index=True,
                            height=min(400, len(dados_faltam) * 35 + 40)
                        )
                    else:
                        st.success("✅ Todos os servidores do edital oficial já estão no simulador!")
                    
                    st.divider()
                    
                    # ========= REMOVER DO SIMULADOR =========
                    if resultados['remover_simulador']:
                        st.subheader(f"❌ Servidores para REVISAR/REMOVER do Simulador ({len(resultados['remover_simulador'])})")
                        st.error("Estes servidores estão no simulador mas NÃO finalizaram inscrição no edital oficial.")
                        
                        dados_remover = []
                        for item in resultados['remover_simulador']:
                            dados_remover.append({
                                "Nome (Simulador)": item['nome'],
                                "Matrícula": item['matricula'],
                                "Motivo": item['motivo']
                            })
                        
                        st.dataframe(
                            pd.DataFrame(dados_remover),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.success("✅ Todos os servidores do simulador finalizaram inscrição no edital oficial!")
                    
                    st.divider()
                    
                    # ========= COINCIDENTES =========
                    with st.expander(f"✅ Servidores Coincidentes ({len(resultados['coincidentes'])})"):
                        if resultados['coincidentes']:
                            dados_coinc = []
                            for item in resultados['coincidentes']:
                                dados_coinc.append({
                                    "Nome (CSV)": item['nome_csv'],
                                    "Nome (Simulador)": item['nome_simulador'],
                                    "Matrícula": item['matricula'],
                                    "Qtd Vagas CSV": len(item['vagas_csv'])
                                })
                            
                            st.dataframe(
                                pd.DataFrame(dados_coinc),
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("Nenhum servidor coincidente encontrado.")
                    
                    # ========= NÃO FINALIZADOS =========
                    with st.expander(f"🚫 Servidores que NÃO Finalizaram no Edital ({len(resultados['csv_nao_finalizados'])})"):
                        if resultados['csv_nao_finalizados']:
                            st.caption("Servidores que tentaram se inscrever mas só têm registros 'Cancelado' ou 'Não concluída'")
                            
                            dados_nao_fin = []
                            for item in resultados['csv_nao_finalizados']:
                                dados_nao_fin.append({
                                    "Nome": item['nome'],
                                    "Situações": ", ".join(item['situacoes'])
                                })
                            
                            st.dataframe(
                                pd.DataFrame(dados_nao_fin),
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("Todos os servidores do CSV finalizaram suas inscrições.")
                    
                    st.divider()
                    
                    # Resumo final
                    st.markdown("### 📊 Resumo da Comparação")
                    
                    total_edital = len(resultados['csv_finalizados'])
                    total_simulador = len(df_inscricoes) if not df_inscricoes.empty else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        **Edital Oficial:**
                        - Total de inscrições finalizadas: **{total_edital}**
                        - Servidores únicos: **{len(set([r['servidor_normalizado'] for r in resultados['csv_finalizados']]))}**
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Simulador:**
                        - Total de inscrições: **{total_simulador}**
                        - Coincidentes com edital: **{len(resultados['coincidentes'])}**
                        """)
                    
                    if len(resultados['faltam_simulador']) > 0 or len(resultados['remover_simulador']) > 0:
                        st.warning(f"""
                        ⚠️ **Ação necessária:**
                        - Adicionar {len(resultados['faltam_simulador'])} servidor(es) ao simulador
                        - Revisar/remover {len(resultados['remover_simulador'])} servidor(es) do simulador
                        """)
                    else:
                        st.success("✅ Simulador está sincronizado com o edital oficial!")
        else:
            st.info("👆 Faça upload do arquivo CSV para iniciar a comparação.")
    
    # =========================================================================
    # ABA ADMIN 7: CONFIGURAÇÕES
    # =========================================================================
    with admin_tab7:
        st.header("⚙️ Configurações do Sistema")
        
        st.warning("⚠️ Alterações nas configurações requerem edição do código fonte.")
        
        # Informações do sistema
        st.subheader("ℹ️ Informações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configurações Atuais:**")
            st.markdown(f"- **Total de usuários:** {len(AUTH_CODES)}")
            st.markdown(f"- **Administradores:** {len(ADMIN_TELEFONES)}")
            st.markdown(f"- **Data limite estágio probatório:** {DATA_LIMITE_ESTAGIO.strftime('%d/%m/%Y')}")
            st.markdown(f"- **Total vagas Anexo I:** {sum(v['quantidade'] for v in ANEXO_I.values())}")
            st.markdown(f"- **Total unidades Anexo II:** {len(ANEXO_II)}")
        
        with col2:
            st.markdown("**Dados de Lotação:**")
            st.markdown(f"- **Unidades mapeadas:** {len(LOTACAO_COMPLETA)}")
            superavit = len([u for u in LOTACAO_COMPLETA if u["status"] == "SUPERAVITÁRIA"])
            equilibrada = len([u for u in LOTACAO_COMPLETA if u["status"] == "EQUILIBRADA"])
            deficit = len([u for u in LOTACAO_COMPLETA if u["status"] == "DEFICITÁRIA"])
            st.markdown(f"- **Superavitárias:** {superavit}")
            st.markdown(f"- **Equilibradas:** {equilibrada}")
            st.markdown(f"- **Deficitárias:** {deficit}")
        
        st.divider()
        
        # Lista de admins
        st.subheader("🔐 Administradores")
        
        for tel in ADMIN_TELEFONES:
            st.markdown(f"- {formatar_telefone_display(tel)}")
        
        st.divider()
        
        # Códigos de acesso
        st.subheader("🔑 Códigos de Acesso")
        
        with st.expander("Ver todos os códigos de acesso"):
            dados_codigos = []
            for tel, cod in AUTH_CODES.items():
                dados_codigos.append({
                    "Telefone": formatar_telefone_display(tel),
                    "Código": cod
                })
            
            st.dataframe(pd.DataFrame(dados_codigos), use_container_width=True, hide_index=True, height=400)
        
        st.divider()
        
        # Ações administrativas
        st.subheader("🛠️ Ações Administrativas")
        
        st.markdown("Para realizar ações administrativas avançadas, edite o código-fonte:")
        st.markdown("""
        - **Adicionar usuário:** Incluir no dicionário `AUTH_CODES`
        - **Remover usuário:** Remover do dicionário `AUTH_CODES`
        - **Adicionar admin:** Incluir na lista `ADMIN_TELEFONES`
        - **Alterar senha admin:** Modificar variável `ADMIN_SENHA`
        - **Atualizar dados de lotação:** Editar `lotacao_data.py`
        """)


# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================

def main():
    st.title("⚖️ Simulador de Relotação - TJPR")
    st.caption("Edital nº 4/2025 - Técnico Judiciário")
    
    # Verificar se está no modo admin
    if "modo_admin" not in st.session_state:
        st.session_state.modo_admin = False
    
    # Botão de logout no sidebar
    with st.sidebar:
        telefone_display = get_usuario_logado()
        st.success(f"✅ Conectado")
        st.caption(f"📱 {telefone_display}")
        
        # Botão de admin (só aparece para admins)
        if is_admin():
            st.divider()
            if st.session_state.modo_admin:
                if st.button("📊 Voltar ao Simulador", use_container_width=True):
                    st.session_state.modo_admin = False
                    st.rerun()
            else:
                if st.button("🔐 Painel Admin", use_container_width=True, type="primary"):
                    st.session_state.modo_admin = True
                    st.rerun()
            st.divider()
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.telefone_usuario = None
            st.session_state.modo_admin = False
            st.session_state.admin_autenticado = False
            st.rerun()
    
    # Conectar ao Google Sheets
    sheet = conectar_sheets()
    df_inscricoes = carregar_inscricoes(sheet)
    
    # Se está no modo admin, mostrar painel admin
    if st.session_state.modo_admin and is_admin():
        painel_administrador(sheet, df_inscricoes)
        return
    
    # Criar abas (7 abas organizadas)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "✍️ Inscrição",
        "👥 Inscritos", 
        "🏆 Resultado",
        "🎯 Simulador",
        "📋 Vagas",
        "📈 Lotação",
        "🗺️ RAJs"
    ])
    
    # Calcular demanda (quantos escolheram cada vaga)
    demanda_a1, demanda_a2 = calcular_demanda(df_inscricoes)
    
    # =========================================================================
    # ABA 1: INSCRIÇÃO
    # =========================================================================
    with tab1:
        st.header("✍️ Inscrição / Edição")
        
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
                
                # Extrair códigos para verificações
                codigo_lotacao_temp = lotacao_atual.split(" - ")[0] if lotacao_atual else ""
                codigo_escolha_a2_temp = escolha_a2.split(" - ")[0] if escolha_a2 != "(Não escolheu)" else ""
                
                # ALERTA DE CONFLITO: origem = destino
                if codigo_lotacao_temp and codigo_escolha_a2_temp and codigo_lotacao_temp == codigo_escolha_a2_temp:
                    st.error("⚠️ **CONFLITO:** Você escolheu a mesma unidade como origem e destino no Anexo II. Isso não faz sentido!")
                
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
                        
                        if salvar_inscricao(sheet, dados, st.session_state.telefone_usuario):
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
                        sucesso, nome = excluir_inscricao(sheet, matricula_excluir, st.session_state.telefone_usuario)
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
            **Regras do Edital:**
            - Servidores em **estágio probatório** (admitidos após 26/11/2022) serão desclassificados
            - Servidores relotados há menos de 2 anos também são desclassificados (verificar manualmente)
            - Critério de desempate: **antiguidade** (data de admissão mais antiga)
            
            **Como funciona:**
            1. Primeiro são analisadas as escolhas do **Anexo I** (vagas deficitárias)
            2. Quem consegue vaga no Anexo I, libera sua lotação atual
            3. As vagas liberadas ficam disponíveis para o **Anexo II**
            4. O mais antigo sempre tem prioridade
            
            **Designação na Origem (item 3.14):**
            - Se sua saída **ocasionar déficit** na origem, você será designado para continuar lá até substituição
            - Se sua saída **não ocasionar déficit**, você pode ir imediatamente para a nova unidade
            """)
    
    # =========================================================================
    # ABA 2: SERVIDORES INSCRITOS
    # =========================================================================
    with tab2:
        st.header("👥 Servidores Inscritos")
        
        if df_inscricoes.empty:
            st.info("Nenhum servidor inscrito ainda.")
        else:
            df_inscricoes_local = carregar_inscricoes(sheet)
            
            df_display = df_inscricoes_local.sort_values("data_admissao", ascending=True).reset_index(drop=True)
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
            
            # BUSCA POR NOME OU MATRÍCULA
            col_busca1, col_busca2 = st.columns([3, 1])
            with col_busca1:
                busca_servidor = st.text_input("🔍 Buscar servidor:", key="busca_servidor", 
                                                placeholder="Digite nome ou matrícula...")
            with col_busca2:
                filtro_estagio = st.selectbox("Estágio Probatório:", ["Todos", "Não", "⚠️ SIM"], key="filtro_estagio")
            
            # Aplicar filtros
            df_filtrado = df_display.copy()
            
            if busca_servidor:
                mask = df_filtrado.apply(
                    lambda x: busca_servidor.lower() in str(x["nome"]).lower() or 
                              busca_servidor.lower() in str(x["matricula"]).lower(), 
                    axis=1
                )
                df_filtrado = df_filtrado[mask]
            
            if filtro_estagio != "Todos":
                df_filtrado = df_filtrado[df_filtrado["estagio_probatorio"] == filtro_estagio]
            
            st.dataframe(
                df_filtrado[[
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
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Registros antigos não possuem informações de log. Novas inscrições terão essa informação automaticamente.")
    
    # =========================================================================
    # ABA 3: RESULTADO E DASHBOARD
    # =========================================================================
    with tab3:
        st.header("🏆 Resultado da Simulação")
        
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
                **Baseado no item 3.14 do Edital:**
                
                > "O deferimento de pedido de relotação que **ocasionar déficit** de técnico judiciário na unidade de origem 
                > implicará **designação** do servidor relotado para continuar prestando serviços na unidade de origem, 
                > até a substituição por outro servidor."
                
                | Designação | Significado |
                |------------|-------------|
                | **NÃO** | A saída do servidor **não ocasiona déficit**. A unidade fica SUPERAVITÁRIA ou EQUILIBRADA após a saída. O servidor pode ir embora imediatamente! ✅ |
                | **SIM** | A saída do servidor **ocasiona ou agrava déficit**. A unidade fica DEFICITÁRIA após a saída. O servidor é relotado oficialmente, MAS fica designado para continuar trabalhando na origem até substituição. ⚠️ |
                
                **⚠️ ATENÇÃO (item 3.15):** Se não vier substituição até o prazo de vigência do concurso, a relotação é **tornada sem efeito** e o servidor **retorna à unidade de lotação originária**.
                
                **Resumo:**
                - 🟢 Origem fica **SUPERAVITÁRIA** após saída → Designação = NÃO
                - 🟡 Origem fica **EQUILIBRADA** após saída → Designação = NÃO  
                - 🔴 Origem fica **DEFICITÁRIA** após saída → Designação = SIM
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
            **Legenda:** 
            - 🟢 Aprovado (designação = NÃO) - pode sair imediatamente
            - 🟡 Aprovado (designação = SIM) - fica na origem até substituição
            - 🔴 Desclassificado (estágio probatório)
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
            
            # Top vagas mais disputadas
            st.subheader("🔥 Top 10 Vagas Mais Disputadas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Anexo I (Vagas com Déficit):**")
                
                if demanda_a1:
                    top_a1 = sorted(demanda_a1.items(), key=lambda x: x[1], reverse=True)[:10]
                    dados_top = []
                    for codigo, dem in top_a1:
                        if codigo in ANEXO_I:
                            vagas = ANEXO_I[codigo]["quantidade"]
                            dados_top.append({
                                "Comarca": ANEXO_I[codigo]['comarca'],
                                "Unidade": ANEXO_I[codigo]['unidade'],
                                "Vagas": vagas,
                                "Interessados": dem
                            })
                    
                    if dados_top:
                        st.dataframe(
                            pd.DataFrame(dados_top), 
                            use_container_width=True, 
                            hide_index=True,
                            height=400
                        )
                else:
                    st.info("Nenhuma escolha de Anexo I registrada.")
            
            with col2:
                st.markdown("**Anexo II (Todas as Unidades):**")
                
                if demanda_a2:
                    top_a2 = sorted(demanda_a2.items(), key=lambda x: x[1], reverse=True)[:10]
                    dados_top = []
                    for codigo, dem in top_a2:
                        if codigo in ANEXO_II:
                            dados_top.append({
                                "Comarca": ANEXO_II[codigo]['comarca'],
                                "Unidade": ANEXO_II[codigo]['unidade'],
                                "Interessados": dem
                            })
                    
                    if dados_top:
                        st.dataframe(
                            pd.DataFrame(dados_top), 
                            use_container_width=True, 
                            hide_index=True,
                            height=400
                        )
                else:
                    st.info("Nenhuma escolha de Anexo II registrada.")
    
    # =========================================================================
    # ABA 4: SIMULADOR (Minha Simulação + Comparador)
    # =========================================================================
    with tab4:
        st.header("🎯 Simulador Individual")
        
        # Sub-seções com radio button
        opcao_simulador = st.radio(
            "Escolha uma opção:",
            ["📊 Minha Simulação", "🔄 Comparador de Cenários"],
            horizontal=True,
            key="opcao_simulador"
        )
        
        st.divider()
        
        if opcao_simulador == "📊 Minha Simulação":
            st.subheader("📊 Minha Simulação Individual")
            st.info("Digite sua matrícula para ver sua posição, chances e análise personalizada.")
            
            if df_inscricoes.empty:
                st.warning("Nenhum servidor inscrito ainda.")
            else:
                # Campo de busca por matrícula
                matricula_consulta = st.text_input(
                    "Digite sua matrícula:",
                    placeholder="Ex: 12345",
                    key="matricula_simulacao"
                )
                
                if matricula_consulta:
                    # Buscar servidor
                    servidor = df_inscricoes[df_inscricoes["matricula"].astype(str) == str(matricula_consulta)]
                    
                    if servidor.empty:
                        st.error(f"❌ Matrícula {matricula_consulta} não encontrada nas inscrições.")
                    else:
                        servidor = servidor.iloc[0]
                        
                        # Calcular resultado completo
                        df_resultado, vagas_rest_a1, vagas_disp_a2, _ = calcular_resultado(df_inscricoes)
                        
                        # Encontrar este servidor no resultado
                        resultado_servidor = df_resultado[df_resultado["matricula"].astype(str) == str(matricula_consulta)].iloc[0]
                        
                        st.success(f"✅ Servidor encontrado: **{servidor['nome']}**")
                        
                        st.divider()
                        
                        # Cards com informações principais
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "📊 Posição por Antiguidade",
                                f"{resultado_servidor['posicao_antiguidade']}º",
                                f"de {len(df_resultado)} inscritos"
                            )
                        
                        with col2:
                            status = resultado_servidor['status']
                            if status == "APROVADO":
                                st.metric("🏆 Status", "APROVADO", delta="✓", delta_color="normal")
                            elif status == "DESCLASSIFICADO":
                                st.metric("🏆 Status", "DESCLASSIFICADO", delta="✗", delta_color="inverse")
                            else:
                                st.metric("🏆 Status", "NÃO OBTEVE VAGA", delta="—")
                        
                        with col3:
                            designacao = resultado_servidor['designacao_origem']
                            if designacao == "SIM":
                                st.metric("📍 Designação na Origem", "SIM", delta="Aguardar substituição", delta_color="off")
                            elif designacao == "NÃO":
                                st.metric("📍 Designação na Origem", "NÃO", delta="Pode ir imediatamente", delta_color="normal")
                            else:
                                st.metric("📍 Designação na Origem", "-", delta="")
                        
                        st.divider()
                        
                        # Detalhes da inscrição
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📋 Dados da Inscrição**")
                            
                            # Lotação atual
                            lotacao_codigo = servidor['lotacao_atual']
                            if lotacao_codigo in ANEXO_II:
                                lotacao_nome = f"{ANEXO_II[lotacao_codigo]['comarca']} - {ANEXO_II[lotacao_codigo]['unidade']}"
                            else:
                                lotacao_nome = lotacao_codigo
                            
                            st.markdown(f"**Data de Admissão:** {servidor['data_admissao'].strftime('%d/%m/%Y') if servidor['data_admissao'] else '-'}")
                            st.markdown(f"**Lotação Atual:** {lotacao_nome}")
                            
                            # Status da lotação atual
                            status_origem = obter_status_lotacao(lotacao_codigo)
                            dados_origem = obter_dados_lotacao(lotacao_codigo)
                            if dados_origem:
                                cor = "🟢" if status_origem == "SUPERAVITÁRIA" else ("🟡" if status_origem == "EQUILIBRADA" else "🔴")
                                st.markdown(f"**Status da Origem:** {cor} {status_origem} (LR: {dados_origem['lotacao_real']} | LP: {dados_origem['lotacao_paradigma']})")
                        
                        with col2:
                            st.markdown("**🎯 Escolhas**")
                            
                            # Escolha Anexo I
                            escolha_a1 = servidor.get('escolha_anexo1', '')
                            if escolha_a1 and escolha_a1 in ANEXO_I:
                                info_a1 = ANEXO_I[escolha_a1]
                                demanda = demanda_a1.get(escolha_a1, 0)
                                vagas = info_a1['quantidade']
                                st.markdown(f"**1ª Opção (Anexo I):** {info_a1['comarca']} - {info_a1['unidade']}")
                                st.markdown(f"   ↳ Vagas: {vagas} | Demanda: {demanda} | Restantes: {vagas_rest_a1.get(escolha_a1, vagas)}")
                            else:
                                st.markdown("**1ª Opção (Anexo I):** Não escolheu")
                            
                            # Escolha Anexo II
                            escolha_a2 = servidor.get('escolha_anexo2', '')
                            if escolha_a2 and escolha_a2 in ANEXO_II:
                                info_a2 = ANEXO_II[escolha_a2]
                                demanda = demanda_a2.get(escolha_a2, 0)
                                st.markdown(f"**2ª Opção (Anexo II):** {info_a2['comarca']} - {info_a2['unidade']}")
                                st.markdown(f"   ↳ Demanda: {demanda} | Vagas liberadas: {vagas_disp_a2.get(escolha_a2, 0)}")
                            else:
                                st.markdown("**2ª Opção (Anexo II):** Não escolheu")
                        
                        st.divider()
                        
                        # Análise e resultado
                        st.markdown("**📊 Análise do Resultado**")
                        
                        resultado = resultado_servidor['resultado']
                        vaga_obtida = resultado_servidor['vaga_obtida']
                        observacao = resultado_servidor['observacao']
                        
                        if resultado_servidor['status'] == "APROVADO":
                            st.success(f"🎉 **Parabéns!** Você obteve vaga pelo **{resultado}**!")
                            st.markdown(f"**Vaga Obtida:** {vaga_obtida}")
                            
                            if resultado_servidor['designacao_origem'] == "SIM":
                                st.warning("⚠️ **Atenção:** Você ficará designado na unidade de origem até que haja substituição (item 3.14 do Edital).")
                            else:
                                st.info("✅ Você poderá ir imediatamente para a nova unidade!")
                        
                        elif resultado_servidor['status'] == "DESCLASSIFICADO":
                            st.error(f"❌ **Desclassificado:** {observacao}")
                            st.markdown("Conforme item 3.2 do Edital, servidores em estágio probatório não podem participar.")
                        
                        else:
                            st.warning(f"😔 **Não obteve vaga:** {observacao}")
                            
                            # Sugestões
                            if escolha_a1 and vagas_rest_a1.get(escolha_a1, 0) == 0:
                                st.markdown("💡 **Dica:** A vaga do Anexo I que você escolheu foi preenchida. Considere escolher outra opção.")
                            
                            if escolha_a2 and vagas_disp_a2.get(escolha_a2, 0) == 0:
                                st.markdown("💡 **Dica:** A vaga do Anexo II que você escolheu não foi liberada. Isso acontece quando ninguém da sua unidade de interesse foi para o Anexo I.")
        
        else:  # Comparador de Cenários
            st.subheader("🔄 Comparador de Cenários")
            st.info("Simule diferentes escolhas e veja como isso afetaria seu resultado, SEM alterar sua inscrição real.")
            
            if df_inscricoes.empty:
                st.warning("Nenhum servidor inscrito ainda.")
            else:
                # Selecionar servidor para simular
                matricula_comparar = st.text_input(
                    "Digite a matrícula para simular:",
                    placeholder="Ex: 12345",
                    key="matricula_comparador"
                )
                
                if matricula_comparar:
                    servidor_orig = df_inscricoes[df_inscricoes["matricula"].astype(str) == str(matricula_comparar)]
                    
                    if servidor_orig.empty:
                        st.error(f"❌ Matrícula {matricula_comparar} não encontrada.")
                    else:
                        servidor_orig = servidor_orig.iloc[0]
                        
                        st.success(f"✅ Simulando para: **{servidor_orig['nome']}**")
                        
                        st.divider()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📋 Cenário ATUAL**")
                            
                            # Calcular resultado atual
                            df_resultado_atual, _, _, _ = calcular_resultado(df_inscricoes)
                            resultado_atual = df_resultado_atual[df_resultado_atual["matricula"].astype(str) == str(matricula_comparar)].iloc[0]
                            
                            escolha_a1_atual = servidor_orig.get('escolha_anexo1', '')
                            escolha_a2_atual = servidor_orig.get('escolha_anexo2', '')
                            
                            if escolha_a1_atual and escolha_a1_atual in ANEXO_I:
                                st.markdown(f"**Anexo I:** {ANEXO_I[escolha_a1_atual]['comarca']} - {ANEXO_I[escolha_a1_atual]['unidade'][:30]}...")
                            else:
                                st.markdown("**Anexo I:** Não escolheu")
                            
                            if escolha_a2_atual and escolha_a2_atual in ANEXO_II:
                                st.markdown(f"**Anexo II:** {ANEXO_II[escolha_a2_atual]['comarca']} - {ANEXO_II[escolha_a2_atual]['unidade'][:30]}...")
                            else:
                                st.markdown("**Anexo II:** Não escolheu")
                            
                            st.divider()
                            
                            if resultado_atual['status'] == "APROVADO":
                                st.success(f"✅ {resultado_atual['status']} - {resultado_atual['resultado']}")
                                st.markdown(f"**Vaga:** {resultado_atual['vaga_obtida']}")
                                st.markdown(f"**Designação:** {resultado_atual['designacao_origem']}")
                            elif resultado_atual['status'] == "DESCLASSIFICADO":
                                st.error(f"❌ {resultado_atual['status']}")
                            else:
                                st.warning(f"⚠️ {resultado_atual['status']}")
                                st.markdown(f"**Motivo:** {resultado_atual['observacao']}")
                        
                        with col2:
                            st.markdown("**🔮 Cenário SIMULADO**")
                            
                            # Seletores para novas escolhas
                            opcoes_a1_sim = ["(Não escolher)"] + [f"{k} - {v['comarca']} - {v['unidade'][:40]}" for k, v in ANEXO_I.items()]
                            opcoes_a2_sim = ["(Não escolher)"] + [f"{k} - {v['comarca']} - {v['unidade'][:40]}" for k, v in ANEXO_II.items()]
                            
                            # Encontrar índice atual
                            idx_a1 = 0
                            if escolha_a1_atual:
                                for i, op in enumerate(opcoes_a1_sim):
                                    if op.startswith(escolha_a1_atual + " -"):
                                        idx_a1 = i
                                        break
                            
                            idx_a2 = 0
                            if escolha_a2_atual:
                                for i, op in enumerate(opcoes_a2_sim):
                                    if op.startswith(escolha_a2_atual + " -"):
                                        idx_a2 = i
                                        break
                            
                            nova_escolha_a1 = st.selectbox("Nova escolha Anexo I:", opcoes_a1_sim, index=idx_a1, key="sim_a1")
                            nova_escolha_a2 = st.selectbox("Nova escolha Anexo II:", opcoes_a2_sim, index=idx_a2, key="sim_a2")
                            
                            if st.button("🔄 Simular Cenário", use_container_width=True):
                                # Criar cópia do dataframe com a alteração
                                df_simulacao = df_inscricoes.copy()
                                
                                # Extrair códigos
                                codigo_sim_a1 = nova_escolha_a1.split(" - ")[0] if nova_escolha_a1 != "(Não escolher)" else ""
                                codigo_sim_a2 = nova_escolha_a2.split(" - ")[0] if nova_escolha_a2 != "(Não escolher)" else ""
                                
                                # Atualizar escolhas no dataframe de simulação
                                mask = df_simulacao["matricula"].astype(str) == str(matricula_comparar)
                                df_simulacao.loc[mask, "escolha_anexo1"] = codigo_sim_a1
                                df_simulacao.loc[mask, "escolha_anexo2"] = codigo_sim_a2
                                
                                # Calcular novo resultado
                                df_resultado_sim, _, _, _ = calcular_resultado(df_simulacao)
                                resultado_sim = df_resultado_sim[df_resultado_sim["matricula"].astype(str) == str(matricula_comparar)].iloc[0]
                                
                                st.divider()
                                
                                if resultado_sim['status'] == "APROVADO":
                                    st.success(f"✅ {resultado_sim['status']} - {resultado_sim['resultado']}")
                                    st.markdown(f"**Vaga:** {resultado_sim['vaga_obtida']}")
                                    st.markdown(f"**Designação:** {resultado_sim['designacao_origem']}")
                                elif resultado_sim['status'] == "DESCLASSIFICADO":
                                    st.error(f"❌ {resultado_sim['status']}")
                                else:
                                    st.warning(f"⚠️ {resultado_sim['status']}")
                                    st.markdown(f"**Motivo:** {resultado_sim['observacao']}")
                                
                                # Comparação
                                st.divider()
                                if resultado_atual['status'] != resultado_sim['status'] or resultado_atual['resultado'] != resultado_sim['resultado']:
                                    st.info("💡 **O resultado mudou!** Compare os cenários acima.")
                                else:
                                    st.info("💡 **O resultado seria o mesmo** com essas escolhas.")
    
    # =========================================================================
    # ABA 5: VAGAS (Anexo I e II)
    # =========================================================================
    with tab5:
        st.header("📋 Vagas Disponíveis")
        
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
            st.info("Estas são as vagas prioritárias com déficit de servidores. A coluna **Demanda** mostra quantos servidores escolheram cada vaga.")
            
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
            
            st.dataframe(df_a1, use_container_width=True, hide_index=True)
            
            total_demanda = df_a1["Demanda"].sum()
            st.caption(f"Total: {len(df_a1)} unidades | {df_a1['Vagas'].sum()} vagas | {total_demanda} servidores interessados")
        
        else:  # Anexo II
            st.subheader("Todas as Unidades (Anexo II)")
            st.info("Estas são todas as unidades judiciárias. A coluna **Demanda** mostra quantos servidores escolheram cada unidade como 2ª opção.")
            
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
                use_container_width=True, 
                hide_index=True
            )
            
            total_demanda_a2 = df_a2["Demanda"].sum()
            st.caption(f"Total: {len(df_a2)} unidades | {total_demanda_a2} servidores interessados")
    
    # =========================================================================
    # ABA 6: LOTAÇÃO DAS UNIDADES
    # =========================================================================
    with tab6:
        st.header("📈 Lotação das Unidades Judiciárias")
        st.info("Dados da Tabela de Lotação de Pessoal (TLP) - 2º Semestre 2025. Fonte: BI do TJPR.")
        
        # Explicação
        with st.expander("ℹ️ Como interpretar os dados"):
            st.markdown("""
            **Colunas:**
            - **Lotação Real (LR)**: Total de servidores atualmente lotados na unidade
            - **Lotação Paradigma (LP)**: Mínimo de servidores necessários segundo a Resolução CNJ 219/2016
            - **Diferença**: Lotação Real - Lotação Paradigma
            
            **Status:**
            - 🟢 **SUPERAVITÁRIA**: Mais servidores que o necessário (diferença > 0)
            - 🟡 **EQUILIBRADA**: Exatamente o necessário (diferença = 0)
            - 🔴 **DEFICITÁRIA**: Menos servidores que o necessário (diferença < 0)
            
            **Impacto na Relotação (item 3.14 do Edital):**
            - Se a saída do servidor **ocasionar déficit** na origem (unidade fica DEFICITÁRIA) → servidor fica **designado** para continuar na origem até substituição
            - Se a saída **não ocasionar déficit** (unidade fica EQUILIBRADA ou SUPERAVITÁRIA) → servidor pode sair **imediatamente**
            """)
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        total_unidades = len(LOTACAO_COMPLETA)
        superavit = len([u for u in LOTACAO_COMPLETA if u["status"] == "SUPERAVITÁRIA"])
        equilibrada = len([u for u in LOTACAO_COMPLETA if u["status"] == "EQUILIBRADA"])
        deficit = len([u for u in LOTACAO_COMPLETA if u["status"] == "DEFICITÁRIA"])
        
        col1.metric("Total Unidades", total_unidades)
        col2.metric("🟢 Superavitárias", superavit)
        col3.metric("🟡 Equilibradas", equilibrada)
        col4.metric("🔴 Deficitárias", deficit)
        
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
        
        # Preparar dados
        dados_lotacao = []
        for u in LOTACAO_COMPLETA:
            dados_lotacao.append({
                "Código": u.get("codigo_anexo2", "-"),
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
            except:
                pass
            return ""
        
        st.dataframe(
            df_lotacao.style.applymap(color_status_lot, subset=["Status"]).applymap(color_diferenca, subset=["Diferença"]),
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        st.caption(f"Exibindo: {len(df_lotacao)} de {total_unidades} unidades")
    
    # =========================================================================
    # ABA 7: RAJS
    # =========================================================================
    with tab7:
        st.header("🗺️ Regiões Administrativas Judiciárias (RAJs)")
        st.info("Análise dos candidatos **APROVADOS** por região de **ORIGEM** (lotação atual). Criada pela Resolução nº 441/2024 do TJPR.")
        
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
