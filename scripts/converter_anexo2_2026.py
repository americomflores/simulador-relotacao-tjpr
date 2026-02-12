"""
Script para converter Anexo II do Edital 01/2026 (Excel -> Python)
"""
import pandas as pd


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


def converter_anexo2():
    """Converte Anexo II do Excel para formato Python dict"""

    df = pd.read_excel('edital 2026/Anexo II.xlsx', header=None)

    anexo_ii = {}
    contador = 1

    # Primeiro, processar colunas 1 e 4 (primeiras linhas)
    for idx, row in df.iterrows():
        comarca = row[1] if pd.notna(row[1]) else None
        unidade = row[4] if pd.notna(row[4]) else None

        # Pular headers e linhas vazias
        if not comarca or not unidade:
            continue
        if str(comarca).strip().upper() == 'COMARCA':
            continue

        comarca = corrigir_encoding(comarca)
        unidade = corrigir_encoding(unidade).upper()

        codigo = f"A2-{contador:03d}"
        anexo_ii[codigo] = {
            "comarca": comarca,
            "unidade": unidade
        }
        contador += 1

    # Depois, processar colunas 0 e 4 (restante das páginas)
    for idx, row in df.iterrows():
        comarca = row[0] if pd.notna(row[0]) else None
        unidade = row[4] if pd.notna(row[4]) else None

        # Pular headers, títulos e linhas vazias
        if not comarca or not unidade:
            continue

        comarca_upper = str(comarca).strip().upper()
        if comarca_upper == 'COMARCA' or 'EDITAL' in comarca_upper or 'ANEXO' in comarca_upper:
            continue

        comarca = corrigir_encoding(comarca)
        unidade = corrigir_encoding(unidade).upper()

        codigo = f"A2-{contador:03d}"
        anexo_ii[codigo] = {
            "comarca": comarca,
            "unidade": unidade
        }
        contador += 1

    return anexo_ii


def gerar_codigo_python(anexo_ii):
    """Gera o código Python para o dicionário ANEXO_II"""

    linhas = []
    linhas.append('')
    linhas.append('# =============================================================================')
    linhas.append('# ANEXO II - Todas as unidades judiciarias')
    linhas.append('# Formato: "CODIGO": {"comarca": "...", "unidade": "..."}')
    linhas.append('# =============================================================================')
    linhas.append('')
    linhas.append('ANEXO_II = {')

    for codigo, dados in anexo_ii.items():
        comarca = dados['comarca'].replace('"', '\\"')
        unidade = dados['unidade'].replace('"', '\\"')
        linhas.append(f'    "{codigo}": {{"comarca": "{comarca}", "unidade": "{unidade}"}},')

    linhas.append('}')

    return '\n'.join(linhas)


if __name__ == '__main__':
    print("Convertendo Anexo II do Edital 01/2026...")

    anexo_ii = converter_anexo2()

    # Estatísticas
    total_unidades = len(anexo_ii)
    comarcas = set(d['comarca'] for d in anexo_ii.values())

    print(f"\nEstatísticas do Anexo II:")
    print(f"  - Total de unidades: {total_unidades}")
    print(f"  - Comarcas únicas: {len(comarcas)}")

    # Gerar código Python
    codigo_python = gerar_codigo_python(anexo_ii)

    # Salvar em arquivo temporário para revisão
    with open('edital 2026/anexo2_convertido.py', 'w', encoding='utf-8') as f:
        f.write(codigo_python)

    print(f"\nArquivo gerado: edital 2026/anexo2_convertido.py")

    # Mostrar primeiras e últimas entradas para verificação
    print("\nPrimeiras 5 entradas:")
    for codigo, dados in list(anexo_ii.items())[:5]:
        print(f"  {codigo}: {dados}")

    print("\nÚltimas 5 entradas:")
    for codigo, dados in list(anexo_ii.items())[-5:]:
        print(f"  {codigo}: {dados}")
