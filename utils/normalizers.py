"""
Funções de normalização de dados.
"""
import re
import unicodedata
from data import ANEXO_II


def normalizar_nome_pessoa(nome):
    """
    Normaliza nome de pessoa para exibição com capitalização correta.

    Regras:
    - Primeira letra de cada palavra em maiúscula (Title Case)
    - Preposições e artigos em minúscula: de, do, dos, da, das, e, a, o, as, os
    - Exceção: primeira palavra do nome sempre em maiúscula

    Exemplos:
        "AMANDA DOS SANTOS" → "Amanda dos Santos"
        "JOÃO DE OLIVEIRA" → "João de Oliveira"
        "MARIA DA SILVA E SOUZA" → "Maria da Silva e Souza"

    Args:
        nome: Nome a ser normalizado

    Returns:
        Nome normalizado para exibição
    """
    if not nome:
        return ""

    # Converter para string se não for
    nome = str(nome).strip()

    # Preposições e artigos que devem ficar em minúscula
    preposicoes = {
        'de', 'do', 'dos', 'da', 'das',
        'e', 'a', 'o', 'as', 'os',
        'em', 'no', 'na', 'nos', 'nas',
        'ao', 'aos', 'à', 'às',
        'com', 'por', 'para'
    }

    # Separar em palavras
    palavras = nome.split()

    # Normalizar cada palavra
    palavras_normalizadas = []
    for i, palavra in enumerate(palavras):
        # Primeira palavra sempre em Title Case
        if i == 0:
            palavras_normalizadas.append(palavra.capitalize())
        # Preposições em minúscula (exceto se for a primeira palavra)
        elif palavra.lower() in preposicoes:
            palavras_normalizadas.append(palavra.lower())
        # Outras palavras em Title Case
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
    
    Args:
        nome1: Primeiro nome
        nome2: Segundo nome
        
    Returns:
        True se os nomes são considerados iguais
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
        "Sao Joao Do Ivai": "São João do Ivaí",
        "Apucarana": "Apucarana",
        "Arapongas": "Arapongas",
        "Astorga": "Astorga",
        "Atalaia": "Atalaia",
        "Bom Sucesso": "Bom Sucesso",
        "Borrazopolis": "Borrazópolis",
        "Califonia": "Califórnia",
        "Cambira": "Cambira",
        "Cruzmaltina": "Cruzmaltina",
        "Faxinal": "Faxinal",
        "Jaguapita": "Jaguapitã",
        "Jaguapita": "Jaguapitã",
        "Jandaia Do Sul": "Jandaia do Sul",
        "Marialva": "Marialva",
        "Marumbi": "Marumbi",
        "Maua Da Serra": "Mauá da Serra",
        "Maua Da Serra": "Mauá da Serra",
        "Nova Esperanca": "Nova Esperança",
        "Nova Esperanca": "Nova Esperança",
        "Novo Itacolomi": "Novo Itacolomi",
        "Pitangueiras": "Pitangueiras",
        "Porecatu": "Porecatu",
        "Presidente Castelo Branco": "Presidente Castelo Branco",
        "Sabaudia": "Sabáudia",
        "Sabaudia": "Sabáudia",
        "Sao Pedro Do Ivai": "São Pedro do Ivaí",
        "Sao Pedro Do Ivai": "São Pedro do Ivaí",
        "Tamboara": "Tamboara",
        "Tuneiras Do Oeste": "Tuneiras do Oeste",
        "Tuneiras Do Oeste": "Tuneiras do Oeste",
    }
    return correcoes.get(nome, nome)


def tentar_match_anexo2(vaga_csv):
    """
    Tenta encontrar correspondência entre o nome da vaga no CSV e o Anexo II.
    Retorna (codigo, score) ou (None, 0) se não encontrar.
    
    Args:
        vaga_csv: Nome da vaga do CSV
        
    Returns:
        Tupla (codigo, score) ou (None, 0)
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

