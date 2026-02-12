"""
Script para converter Anexo I do Edital 01/2026 (Excel -> Python)
"""
import pandas as pd
import re


def corrigir_encoding(texto):
    """Corrige problemas de encoding do PDF convertido para Excel"""
    if pd.isna(texto):
        return ""

    texto = str(texto)

    # Remove quebras de linha e espaços extras
    texto = " ".join(texto.split())

    # Mapeamento de caracteres corrompidos para corretos
    # Padrão: Windows-1252 -> UTF-8 mal interpretado
    correcoes = {
        # Acentos comuns em português
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
        '�': '',  # Remove replacement character
    }

    for errado, correto in correcoes.items():
        texto = texto.replace(errado, correto)

    return texto.strip()


def converter_anexo1():
    """Converte Anexo I do Excel para formato Python dict"""

    df = pd.read_excel('edital 2026/Anexo I.xlsx', header=None)

    anexo_i = {}
    contador = 1

    # Primeiro, processar colunas 1, 3, 5 (lado direito do PDF)
    for idx, row in df.iterrows():
        comarca = row[1] if pd.notna(row[1]) else None
        unidade = row[3] if pd.notna(row[3]) else None
        quantidade = row[5] if pd.notna(row[5]) else None

        # Pular headers e linhas vazias
        if not comarca or not unidade or not quantidade:
            continue
        if str(comarca).strip() == 'Comarca':
            continue

        comarca = corrigir_encoding(comarca)
        unidade = corrigir_encoding(unidade).upper()

        try:
            quantidade = int(float(quantidade))
        except (ValueError, TypeError):
            continue

        codigo = f"A1-{contador:03d}"
        anexo_i[codigo] = {
            "comarca": comarca,
            "unidade": unidade,
            "quantidade": quantidade
        }
        contador += 1

    # Depois, processar colunas 0, 2, 4 (lado esquerdo do PDF, páginas seguintes)
    for idx, row in df.iterrows():
        comarca = row[0] if pd.notna(row[0]) else None
        unidade = row[2] if pd.notna(row[2]) else None
        quantidade = row[4] if pd.notna(row[4]) else None

        # Pular headers, títulos e linhas vazias
        if not comarca or not unidade or not quantidade:
            continue
        if str(comarca).strip() == 'Comarca':
            continue
        if 'EDITAL' in str(comarca).upper() or 'ANEXO' in str(comarca).upper():
            continue

        comarca = corrigir_encoding(comarca)
        unidade = corrigir_encoding(unidade).upper()

        try:
            quantidade = int(float(quantidade))
        except (ValueError, TypeError):
            continue

        codigo = f"A1-{contador:03d}"
        anexo_i[codigo] = {
            "comarca": comarca,
            "unidade": unidade,
            "quantidade": quantidade
        }
        contador += 1

    return anexo_i


def gerar_codigo_python(anexo_i):
    """Gera o código Python para o dicionário ANEXO_I"""

    linhas = []
    linhas.append('"""')
    linhas.append('Dados dos Anexos do Edital n 01/2026 - TJPR')
    linhas.append('"""')
    linhas.append('')
    linhas.append('# =============================================================================')
    linhas.append('# ANEXO I - Vagas com deficit')
    linhas.append('# Formato: "CODIGO": {"comarca": "...", "unidade": "...", "quantidade": N}')
    linhas.append('# =============================================================================')
    linhas.append('')
    linhas.append('ANEXO_I = {')

    for codigo, dados in anexo_i.items():
        comarca = dados['comarca'].replace('"', '\\"')
        unidade = dados['unidade'].replace('"', '\\"')
        quantidade = dados['quantidade']
        linhas.append(f'    "{codigo}": {{"comarca": "{comarca}", "unidade": "{unidade}", "quantidade": {quantidade}}},')

    linhas.append('}')

    return '\n'.join(linhas)


if __name__ == '__main__':
    print("Convertendo Anexo I do Edital 01/2026...")

    anexo_i = converter_anexo1()

    # Estatísticas
    total_vagas = sum(d['quantidade'] for d in anexo_i.values())
    total_unidades = len(anexo_i)
    comarcas = set(d['comarca'] for d in anexo_i.values())

    print(f"\nEstatísticas do Anexo I:")
    print(f"  - Total de unidades: {total_unidades}")
    print(f"  - Total de vagas: {total_vagas}")
    print(f"  - Comarcas únicas: {len(comarcas)}")

    # Gerar código Python
    codigo_python = gerar_codigo_python(anexo_i)

    # Salvar em arquivo temporário para revisão
    with open('edital 2026/anexo1_convertido.py', 'w', encoding='utf-8') as f:
        f.write(codigo_python)

    print(f"\nArquivo gerado: edital 2026/anexo1_convertido.py")

    # Mostrar primeiras e últimas entradas para verificação
    print("\nPrimeiras 5 entradas:")
    for codigo, dados in list(anexo_i.items())[:5]:
        print(f"  {codigo}: {dados}")

    print("\nÚltimas 5 entradas:")
    for codigo, dados in list(anexo_i.items())[-5:]:
        print(f"  {codigo}: {dados}")
