"""
Script para converter Lista Classificatória do Edital 01/2026 (Excel -> Python)
"""
import pandas as pd
from datetime import datetime


def corrigir_encoding(texto):
    """Corrige problemas de encoding do PDF convertido para Excel"""
    if pd.isna(texto):
        return ""

    texto = str(texto)

    # Remove quebras de linha e espaços extras
    texto = " ".join(texto.split())

    # Mapeamento de caracteres corrompidos para corretos
    correcoes = {
        'á': 'á', 'à': 'à', 'â': 'â', 'ã': 'ã',
        'é': 'é', 'ê': 'ê',
        'í': 'í',
        'ó': 'ó', 'ô': 'ô', 'õ': 'õ',
        'ú': 'ú', 'ü': 'ü',
        'ç': 'ç',
        'Á': 'Á', 'À': 'À', 'Â': 'Â', 'Ã': 'Ã',
        'É': 'É', 'Ê': 'Ê',
        'Í': 'Í',
        'Ó': 'Ó', 'Ô': 'Ô', 'Õ': 'Õ',
        'Ú': 'Ú', 'Ü': 'Ü',
        'Ç': 'Ç',
        '–': '-',
        'º': 'º', 'ª': 'ª',
        '�': '',
    }

    for errado, correto in correcoes.items():
        texto = texto.replace(errado, correto)

    return texto.strip()


def normalizar_nome(nome):
    """Normaliza nome para Title Case com preposições em minúscula"""
    if not nome:
        return ""

    nome = corrigir_encoding(nome)

    # Preposições que devem ficar em minúscula
    preposicoes = {'de', 'da', 'do', 'das', 'dos', 'e'}

    palavras = nome.split()
    palavras_normalizadas = []

    for i, palavra in enumerate(palavras):
        palavra_lower = palavra.lower()
        if i > 0 and palavra_lower in preposicoes:
            palavras_normalizadas.append(palavra_lower)
        else:
            palavras_normalizadas.append(palavra.capitalize())

    return ' '.join(palavras_normalizadas)


def formatar_data(data):
    """Converte datetime para string DD/MM/YYYY"""
    if pd.isna(data):
        return ""

    if isinstance(data, datetime):
        return data.strftime('%d/%m/%Y')

    # Tentar converter string para data
    try:
        if isinstance(data, str):
            # Tentar vários formatos
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(data.split()[0], fmt)
                    return dt.strftime('%d/%m/%Y')
                except:
                    pass
    except:
        pass

    return str(data)


def converter_lista():
    """Converte Lista Classificatória do Excel para formato Python dict"""

    df = pd.read_excel('edital 2026/lista classificatoria.xlsx', header=None)

    lista = {}

    # Colunas:
    # 1: Posição na Lista
    # 2: Nome
    # 3: Início no Cargo
    # 4: Tempo no Cargo
    # 5: Tempo no Poder Judiciário
    # 6: Tempo no Serviço Público
    # 7: Data de Nascimento
    # 8: Lotação
    # 9: Localização Principal

    for idx, row in df.iterrows():
        posicao = row[1]

        # Pular linhas sem posição válida
        if not isinstance(posicao, (int, float)) or pd.isna(posicao) or posicao <= 0:
            continue

        posicao = int(posicao)

        nome_original = corrigir_encoding(row[2]) if pd.notna(row[2]) else ""
        nome = normalizar_nome(nome_original)
        inicio_cargo = formatar_data(row[3])
        tempo_cargo = corrigir_encoding(row[4]) if pd.notna(row[4]) else ""
        tempo_poder_judiciario = corrigir_encoding(row[5]) if pd.notna(row[5]) else ""
        tempo_servico_publico = corrigir_encoding(row[6]) if pd.notna(row[6]) else ""
        data_nascimento = formatar_data(row[7])
        lotacao = corrigir_encoding(row[8]) if pd.notna(row[8]) else ""
        localizacao_principal = corrigir_encoding(row[9]) if pd.notna(row[9]) else ""

        lista[posicao] = {
            "nome": nome,
            "nome_original": nome_original,
            "nome_display": nome,
            "inicio_cargo": inicio_cargo,
            "tempo_cargo": tempo_cargo,
            "tempo_poder_judiciario": tempo_poder_judiciario,
            "tempo_servico_publico": tempo_servico_publico,
            "data_nascimento": data_nascimento,
            "lotacao": lotacao,
            "localizacao_principal": localizacao_principal
        }

    return lista


def gerar_codigo_python(lista):
    """Gera o código Python para o dicionário LISTA_CLASSIFICATORIA"""

    linhas = []
    linhas.append('"""')
    linhas.append('Lista Classificatória do Edital nº 01/2026 - Técnico Judiciário')
    linhas.append('Extraído do arquivo Excel oficial do TJPR')
    linhas.append(f'Total: {len(lista)} servidores (posições 1 a {len(lista)})')
    linhas.append('NOMES NORMALIZADOS: Title Case com preposições em minúscula')
    linhas.append('"""')
    linhas.append('')
    linhas.append('LISTA_CLASSIFICATORIA = {')

    for posicao in sorted(lista.keys()):
        dados = lista[posicao]
        linhas.append(f'    {posicao}: {{')

        for campo, valor in dados.items():
            valor_escaped = str(valor).replace('"', '\\"').replace('\n', ' ')
            linhas.append(f'        "{campo}": "{valor_escaped}",')

        linhas.append('    },')

    linhas.append('}')

    return '\n'.join(linhas)


if __name__ == '__main__':
    print("Convertendo Lista Classificatória do Edital 01/2026...")

    lista = converter_lista()

    # Estatísticas
    total = len(lista)
    posicoes = sorted(lista.keys())

    print(f"\nEstatísticas da Lista Classificatória:")
    print(f"  - Total de servidores: {total}")
    print(f"  - Posição mínima: {min(posicoes)}")
    print(f"  - Posição máxima: {max(posicoes)}")

    # Verificar se há lacunas
    esperado = set(range(1, max(posicoes) + 1))
    lacunas = esperado - set(posicoes)
    if lacunas:
        print(f"  - ATENÇÃO: Posições faltando: {sorted(lacunas)[:20]}...")
    else:
        print("  - Todas as posições preenchidas (sem lacunas)")

    # Gerar código Python
    codigo_python = gerar_codigo_python(lista)

    # Salvar em arquivo temporário para revisão
    with open('edital 2026/lista_convertida.py', 'w', encoding='utf-8') as f:
        f.write(codigo_python)

    print(f"\nArquivo gerado: edital 2026/lista_convertida.py")

    # Mostrar primeiras e últimas entradas para verificação
    print("\nPrimeiras 3 entradas:")
    for pos in sorted(lista.keys())[:3]:
        dados = lista[pos]
        print(f"  {pos}: {dados['nome']} | {dados['inicio_cargo']} | {dados['lotacao'][:50]}...")

    print("\nÚltimas 3 entradas:")
    for pos in sorted(lista.keys())[-3:]:
        dados = lista[pos]
        print(f"  {pos}: {dados['nome']} | {dados['inicio_cargo']}")
