"""
Funções de normalização de dados.
"""
import re
import unicodedata


def normalizar_nome_pessoa(nome):
    """
    Normaliza nome de pessoa para exibição com capitalização correta.

    Regras:
    - Primeira letra de cada palavra em maiúscula (Title Case)
    - Preposições e artigos em minúscula: de, do, dos, da, das, e, a, o, as, os
    - Exceção: primeira palavra do nome sempre em maiúscula

    Args:
        nome: Nome a ser normalizado

    Returns:
        Nome normalizado para exibição
    """
    if not nome:
        return ""

    nome = str(nome).strip()

    preposicoes = {
        'de', 'do', 'dos', 'da', 'das',
        'e', 'a', 'o', 'as', 'os',
        'em', 'no', 'na', 'nos', 'nas',
        'ao', 'aos', 'à', 'às',
        'com', 'por', 'para'
    }

    palavras = nome.split()

    palavras_normalizadas = []
    for i, palavra in enumerate(palavras):
        if i == 0:
            palavras_normalizadas.append(palavra.capitalize())
        elif palavra.lower() in preposicoes:
            palavras_normalizadas.append(palavra.lower())
        else:
            palavras_normalizadas.append(palavra.capitalize())

    return ' '.join(palavras_normalizadas)


def normalizar_nome(nome):
    """
    Normaliza um nome para comparação:
    - Remove acentos
    - Converte para minúsculas
    - Remove espaços extras
    - Remove caracteres especiais

    Args:
        nome: Nome a ser normalizado

    Returns:
        Nome normalizado
    """
    if not nome:
        return ""
    nome = str(nome)
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_normalizado = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    nome_normalizado = re.sub(r'[^a-zA-Z0-9\s]', '', nome_normalizado)
    nome_normalizado = ' '.join(nome_normalizado.lower().split())
    return nome_normalizado


def normalizar_comarca(nome):
    """
    Normaliza nome de comarca para comparação.

    Args:
        nome: Nome da comarca

    Returns:
        Nome normalizado
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
        "Borrazopolis": "Borrazópolis",
        "Califonia": "Califórnia",
        "Jaguapita": "Jaguapitã",
        "Maua Da Serra": "Mauá da Serra",
        "Nova Esperanca": "Nova Esperança",
        "Sabaudia": "Sabáudia",
        "Sao Pedro Do Ivai": "São Pedro do Ivaí",
        "Tuneiras Do Oeste": "Tuneiras do Oeste",
    }
    return correcoes.get(nome, nome)
