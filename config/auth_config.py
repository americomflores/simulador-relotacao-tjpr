"""
Configuração de autenticação do sistema.
Carrega credenciais de secrets.toml ou usa valores padrão (fallback).
"""
import streamlit as st
from exceptions import ConfigurationError

# Valores padrão (fallback) - manter para compatibilidade
DEFAULT_AUTH_CODES = {
    "17982226188": "TJPR-2SRORW",
    "17996292028": "TJPR-Q91TKT",
    "21990432004": "TJPR-XD3195",
    "41984053073": "TJPR-840D2O",
    "41984145956": "TJPR-U1P372",
    "41984714180": "TJPR-T3PJVY",
    "41984884473": "TJPR-XA1OTO",
    "41984965883": "TJPR-XHAXAY",
    "41985230491": "TJPR-PKD2MN",
    "41987233990": "TJPR-97U7HX",
    "41987771822": "TJPR-SMOBOV",
    "41987981984": "TJPR-N11XHO",
    "41988079178": "TJPR-MC80AW",
    "41988197149": "TJPR-0ABJZT",
    "41988205840": "TJPR-6YHNU7",
    "41988253875": "TJPR-BU6ICQ",
    "41988505079": "TJPR-E5VLYN",
    "41988682140": "TJPR-TOPR6C",
    "41988716808": "TJPR-3KLDYH",
    "41988742311": "TJPR-6F1OSK",
    "41988766147": "TJPR-6IFX35",
    "41991064141": "TJPR-3GJ7YU",
    "41991354423": "TJPR-CR8XAW",
    "41992354642": "TJPR-9EVUPY",
    "41995591575": "TJPR-PYR12J",
    "41996111692": "TJPR-1MAI9P",
    "41996139482": "TJPR-838SKH",
    "41996144848": "TJPR-6C45R8",
    "41996248850": "TJPR-1JXLC2",
    "41996399051": "TJPR-H72QCG",
    "41996506223": "TJPR-A9HPUX",
    "41996528826": "TJPR-HJ2ZZV",
    "41996590719": "TJPR-I9VJ4R",
    "41996591926": "TJPR-CXINT3",
    "41996632845": "TJPR-1K91RE",
    "41996641615": "TJPR-LV0O00",
    "41996765443": "TJPR-7W2LPL",
    "41997511879": "TJPR-SVXQ87",
    "41997813606": "TJPR-F4F1X5",  # ADMIN - código mantido
    "41998038212": "TJPR-NQ1900",
    "41998457595": "TJPR-T5LZPZ",
    "41998500089": "TJPR-37NHTA",
    "41998526855": "TJPR-O44IH1",
    "41999081377": "TJPR-M2NCPL",
    "41999160027": "TJPR-T3E2CL",
    "41999280158": "TJPR-E3Y7EB",
    "41999535487": "TJPR-JV74TJ",
    "41999822924": "TJPR-8RS63G",
    "41999831440": "TJPR-TP1OD5",
    "42984212931": "TJPR-Y4VLNX",
    "42998023435": "TJPR-UQSAU8",
    "42998356154": "TJPR-K2TKIV",
    "42999065470": "TJPR-JG1KAR",
    "42999113251": "TJPR-SN50BR",
    "42999151717": "TJPR-DKTXME",
    "42999193219": "TJPR-P05D57",
    "42999678689": "TJPR-IMR8XA",
    "42999746557": "TJPR-WTUEJ7",
    "42999825296": "TJPR-VW7EV5",
    "42999994903": "TJPR-HPCBQ0",
    "43935728485": "TJPR-RYDMU2",
    "43984913099": "TJPR-V4A1PU",
    "43984920995": "TJPR-WZ1EYN",
    "43991286949": "TJPR-JBGAXD",
    "43991310174": "TJPR-1YNVVT",
    "43991506066": "TJPR-AUDYK0",
    "43991639901": "TJPR-0XIVMT",
    "43991973901": "TJPR-8IPMDL",
    "43996186413": "TJPR-WJNZAV",
    "43999196949": "TJPR-PDIP7W",
    "43999236148": "TJPR-LT870Y",
    "43999509978": "TJPR-9J03G4",
    "43999639622": "TJPR-XSCDHM",
    "43999676080": "TJPR-8HQ2QQ",
    "44984059858": "TJPR-6D3YVC",
    "44984095131": "TJPR-9EHZMB",
    "44984250493": "TJPR-YLA7KI",
    "44988554062": "TJPR-S31RS0",
    "44991574505": "TJPR-E3HV4I",
    "44997167692": "TJPR-UKIVLJ",
    "44998557700": "TJPR-QPY3DD",
    "44999339584": "TJPR-ZLFABP",
    "44999457959": "TJPR-QTB4U7",
    "44999459999": "TJPR-RNKW0W",
    "44999527950": "TJPR-6T9KNN",
    "44999571321": "TJPR-A40KT3",
    "44999717000": "TJPR-BRAANY",
    "44999943800": "TJPR-SACVPS",
    "45984047070": "TJPR-POGQHO",
    "45988194141": "TJPR-SPVIKY",
    "45998208420": "TJPR-L3B6GK",
    "45998424843": "TJPR-XB0VXE",
    "45999005757": "TJPR-MJDD03",
    "45999228068": "TJPR-EIMZEA",
    "45999246297": "TJPR-CTGAI4",
    "45999314847": "TJPR-CMGQ1T",
    "45999729986": "TJPR-RGRIVN",
    "45999799439": "TJPR-LP22VK",
    "45999801630": "TJPR-CE3AFR",
    "46988274385": "TJPR-L0CHHW",
    "46991023946": "TJPR-IQFWA3",
    "46991202091": "TJPR-RYIJVG",
    "46991252521": "TJPR-DVEK4I",
    "46999170352": "TJPR-7ETVCV",
    "46999199900": "TJPR-K99JGX",
    "47988463737": "TJPR-NOUN2H",
    "47996150787": "TJPR-P8HREB",
    "49998411291": "TJPR-4A5JSO",
    "51998654686": "TJPR-0U0ONN",
    "85999247334": "TJPR-3REA0T",
}

DEFAULT_ADMIN_TELEFONES = ["41997813606"]
DEFAULT_ADMIN_SENHA = "swift"


def get_auth_codes():
    """
    Retorna os códigos de autenticação.
    Tenta carregar de secrets.toml, caso contrário usa valores padrão.
    """
    try:
        if "auth_codes" in st.secrets:
            return st.secrets["auth_codes"]
    except (AttributeError, KeyError):
        pass
    return DEFAULT_AUTH_CODES


def get_admin_telefones():
    """
    Retorna a lista de telefones de administradores.
    Tenta carregar de secrets.toml, caso contrário usa valores padrão.
    """
    try:
        if "admin_telefones" in st.secrets:
            telefones = st.secrets["admin_telefones"]
            if isinstance(telefones, list):
                return telefones
            elif isinstance(telefones, str):
                # Se for string, separar por vírgula
                return [t.strip() for t in telefones.split(",")]
    except (AttributeError, KeyError):
        pass
    return DEFAULT_ADMIN_TELEFONES


def get_admin_senha():
    """
    Retorna a senha de administrador.
    Tenta carregar de secrets.toml, caso contrário usa valores padrão.
    
    NOTA: Em produção, a senha deve ser armazenada como hash (bcrypt).
    Por enquanto, mantém texto plano para compatibilidade.
    """
    try:
        if "admin_senha" in st.secrets:
            return st.secrets["admin_senha"]
    except (AttributeError, KeyError):
        pass
    return DEFAULT_ADMIN_SENHA


# Exportar valores para compatibilidade com código existente
AUTH_CODES = get_auth_codes()
ADMIN_TELEFONES = get_admin_telefones()
ADMIN_SENHA = get_admin_senha()

