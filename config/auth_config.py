"""
Configuração de autenticação do sistema.
Carrega credenciais de secrets.toml ou usa valores padrão (fallback).
"""
import streamlit as st
from exceptions import ConfigurationError

# Valores padrão (fallback) - manter para compatibilidade
DEFAULT_AUTH_CODES = {
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

