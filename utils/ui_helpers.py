"""
Funções auxiliares para interface Streamlit.
"""


def construir_opcoes_selectbox(dados_dict, default_text="", incluir_vazio=True, mostrar_quantidade=False):
    """
    Constrói lista de opções para selectbox no formato "CODIGO - Comarca - Unidade".

    Args:
        dados_dict: Dicionário com códigos e dados (ANEXO_I ou ANEXO_II)
        default_text: Texto para primeira opção (ex: "(Não escolheu)")
        incluir_vazio: Se True, adiciona opção vazia no início
        mostrar_quantidade: Se True, adiciona "(N vagas)" no final

    Returns:
        Lista de strings formatadas para selectbox

    Example:
        >>> opcoes_a1 = construir_opcoes_selectbox(
        ...     ANEXO_I,
        ...     default_text="(Não escolheu)",
        ...     mostrar_quantidade=True
        ... )
        >>> # Retorna: ["(Não escolheu)", "A1-001 - Curitiba - 1ª Vara Cível (5 vagas)", ...]
    """
    opcoes = []
    if incluir_vazio:
        opcoes.append(default_text if default_text else "")

    for codigo, info in dados_dict.items():
        opcao = f"{codigo} - {info['comarca']} - {info['unidade']}"
        if mostrar_quantidade and 'quantidade' in info:
            opcao += f" ({info['quantidade']} vagas)"
        opcoes.append(opcao)

    return opcoes


def extrair_codigo_da_opcao(opcao, default_vazio="(Não escolheu)"):
    """
    Extrai código de uma opção de selectbox.

    Args:
        opcao: String no formato "CODIGO - Comarca - Unidade"
        default_vazio: Texto que representa opção vazia

    Returns:
        Código extraído ou string vazia se opção vazia

    Example:
        >>> extrair_codigo_da_opcao("A2-123 - Curitiba - 1ª Vara")
        'A2-123'
        >>> extrair_codigo_da_opcao("(Não escolheu)", "(Não escolheu)")
        ''
    """
    if not opcao or opcao == default_vazio or opcao == "":
        return ""

    # Extrai a primeira parte antes do " - "
    partes = opcao.split(" - ")
    if partes:
        return partes[0]
    return ""


def encontrar_indice_opcao(opcoes, codigo_buscado):
    """
    Encontra o índice de uma opção na lista baseado no código.

    Args:
        opcoes: Lista de opções formatadas
        codigo_buscado: Código a buscar (ex: "A2-123")

    Returns:
        Índice da opção ou 0 se não encontrado

    Example:
        >>> opcoes = ["", "A2-123 - Curitiba - 1ª Vara", "A2-124 - Curitiba - 2ª Vara"]
        >>> encontrar_indice_opcao(opcoes, "A2-123")
        1
    """
    if not codigo_buscado:
        return 0

    for i, opcao in enumerate(opcoes):
        if opcao.startswith(codigo_buscado + " - "):
            return i

    return 0


def extrair_comarca_da_string(texto):
    """
    Extrai o nome da comarca de uma string formatada.

    Args:
        texto: String no formato "Comarca - Unidade" ou "Codigo - Comarca - Unidade"

    Returns:
        Nome da comarca ou string vazia

    Example:
        >>> extrair_comarca_da_string("Curitiba - 1ª Vara Cível")
        'Curitiba'
        >>> extrair_comarca_da_string("A2-123 - Curitiba - 1ª Vara Cível")
        'Curitiba'
    """
    if not texto:
        return ""

    partes = texto.split(" - ")
    if len(partes) >= 2:
        # Se tem 3 partes, a comarca é a segunda (formato: Codigo - Comarca - Unidade)
        # Se tem 2 partes, a comarca é a primeira (formato: Comarca - Unidade)
        if len(partes) >= 3:
            return partes[1].strip()
        else:
            return partes[0].strip()

    return ""
