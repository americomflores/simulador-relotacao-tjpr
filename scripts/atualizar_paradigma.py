"""
Script para atualizar lotacao_paradigma em lotacao_data.py
usando os dados dos Anexos III e IV do Edital 01/2026

Anexo III = Unidades Judiciárias (Varas, Juizados, etc.)
Anexo IV = Direções dos Fóruns (Secretarias da Direção)
"""

import sys
import os
import re
import unicodedata
from datetime import datetime
import xml.etree.ElementTree as ET

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lotacao_data import LOTACAO_POR_CODIGO

# Namespaces do XML do Excel
NS = {
    'ss': 'urn:schemas-microsoft-com:office:spreadsheet',
    'html': 'http://www.w3.org/TR/REC-html40'
}

def normalizar_texto(texto):
    """Normaliza texto para comparação"""
    if not texto:
        return ""
    # Remove acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Maiúscula e remove espaços extras
    texto = texto.upper().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def criar_chave(comarca, unidade):
    """Cria chave única normalizada"""
    return f"{normalizar_texto(comarca)}|{normalizar_texto(unidade)}"

def extrair_texto_celula(cell):
    """Extrai texto de uma célula XML, ignorando formatação HTML"""
    data = cell.find('.//ss:Data', NS)
    if data is None:
        return ""

    # Pegar todo o texto, incluindo dentro de tags Font
    texto = ""
    if data.text:
        texto += data.text
    for elem in data.iter():
        if elem.text and elem != data:
            texto += elem.text
        if elem.tail:
            texto += elem.tail

    # Limpar caracteres especiais
    texto = texto.replace('\n', ' ').replace('&#10;', ' ')
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def extrair_numero_celula(cell):
    """Extrai número de uma célula XML"""
    data = cell.find('.//ss:Data', NS)
    if data is None:
        return None

    tipo = data.get('{urn:schemas-microsoft-com:office:spreadsheet}Type')
    if tipo == 'Number':
        try:
            return int(float(data.text or extrair_texto_celula(cell)))
        except:
            pass

    # Tentar extrair número do texto
    texto = extrair_texto_celula(cell)
    try:
        return int(float(texto))
    except:
        return None

def parsear_anexo3(xml_path):
    """
    Parseia Anexo III - Unidades Judiciárias
    Retorna dict: {chave_normalizada: paradigma}
    """
    print(f"Parseando Anexo III: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    resultado = {}
    comarca_atual = ""
    merge_count = 0

    # Encontrar todas as linhas
    for row in root.findall('.//ss:Row', NS):
        cells = row.findall('ss:Cell', NS)

        # Pular linhas de cabeçalho
        texto_primeira = extrair_texto_celula(cells[0]) if cells else ""
        if 'COMARCA' in texto_primeira.upper():
            continue
        if '+SECRETARIA' in texto_primeira.upper():
            continue

        # Extrair dados das células
        col1_cell = None
        col2_cell = None
        col3_cell = None

        for cell in cells:
            index = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
            if index:
                idx = int(index)
            else:
                # Calcular índice baseado na posição
                idx = cells.index(cell) + 1

            if idx == 1:
                col1_cell = cell
            elif idx == 2:
                col2_cell = cell
            elif idx == 3:
                col3_cell = cell

        # Verificar se célula 1 tem MergeDown (comarca mesclada)
        if col1_cell is not None:
            merge_down = col1_cell.get('{urn:schemas-microsoft-com:office:spreadsheet}MergeDown')
            texto_col1 = extrair_texto_celula(col1_cell)

            if texto_col1 and texto_col1.upper() not in ['COMARCA', '']:
                comarca_atual = texto_col1
                if merge_down:
                    merge_count = int(merge_down)
            elif merge_count > 0:
                merge_count -= 1

        # Extrair unidade e paradigma
        unidade = extrair_texto_celula(col2_cell) if col2_cell else ""
        paradigma = extrair_numero_celula(col3_cell) if col3_cell else None

        # Validar e adicionar ao resultado
        if comarca_atual and unidade and paradigma is not None:
            # Ignorar linhas de cabeçalho repetidas
            if 'UNIDADE' in unidade.upper() or 'TOTAL DE' in unidade.upper():
                continue

            chave = criar_chave(comarca_atual, unidade)
            resultado[chave] = paradigma
            # print(f"  {comarca_atual} | {unidade} | {paradigma}")

    print(f"  -> {len(resultado)} unidades encontradas")
    return resultado

def parsear_anexo4(xml_path):
    """
    Parseia Anexo IV - Direções dos Fóruns
    Retorna dict: {chave_normalizada: paradigma}

    Mapeia "Total Direção da Comarca" para "SECRETARIA DA DIREÇÃO DO FÓRUM"

    Estrutura do XML:
    - Coluna 1: Comarca (com MergeDown para agrupar linhas)
    - Coluna 2: Unidade (com MergeAcross=1, ocupa colunas 2-3)
    - Coluna 4: Quantidade (paradigma)
    """
    print(f"Parseando Anexo IV: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    resultado = {}
    comarca_atual = ""
    merge_count = 0

    # Encontrar todas as linhas
    for row in root.findall('.//ss:Row', NS):
        cells = row.findall('ss:Cell', NS)
        if not cells:
            continue

        # Mapear células por índice real (considerando ss:Index)
        cell_map = {}
        current_idx = 1
        for cell in cells:
            index_attr = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
            if index_attr:
                current_idx = int(index_attr)
            cell_map[current_idx] = cell
            # Avançar índice considerando MergeAcross
            merge_across = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}MergeAcross')
            if merge_across:
                current_idx += int(merge_across) + 1
            else:
                current_idx += 1

        col1_cell = cell_map.get(1)
        col2_cell = cell_map.get(2)
        col4_cell = cell_map.get(4)

        # Pular linhas de cabeçalho
        texto_col1 = extrair_texto_celula(col1_cell) if col1_cell is not None else ""
        if 'COMARCA' in texto_col1.upper() or 'UNIDADE' in texto_col1.upper():
            continue

        # Verificar comarca (com MergeDown)
        if col1_cell is not None:
            merge_down = col1_cell.get('{urn:schemas-microsoft-com:office:spreadsheet}MergeDown')
            if texto_col1 and texto_col1.strip():
                comarca_atual = texto_col1.strip()
                if merge_down:
                    merge_count = int(merge_down)
        elif merge_count > 0:
            merge_count -= 1

        # Extrair unidade e paradigma
        unidade = extrair_texto_celula(col2_cell) if col2_cell is not None else ""
        paradigma = extrair_numero_celula(col4_cell) if col4_cell is not None else None

        # Procurar "Total Direção da Comarca" - esse é o paradigma da Secretaria
        if comarca_atual and 'TOTAL' in unidade.upper() and 'DIRE' in unidade.upper():
            if paradigma is not None:
                # Mapear para "SECRETARIA DA DIREÇÃO DO FÓRUM"
                chave = criar_chave(comarca_atual, "SECRETARIA DA DIREÇÃO DO FÓRUM")
                resultado[chave] = paradigma
                # print(f"  {comarca_atual} | Secretaria da Direção do Fórum | {paradigma}")

    print(f"  -> {len(resultado)} direções de fórum encontradas")
    return resultado

def calcular_status(diferenca):
    """Calcula status baseado na diferença"""
    if diferenca > 0:
        return "SUPERAVITÁRIA"
    elif diferenca == 0:
        return "EQUILIBRADA"
    else:
        return "DEFICITÁRIA"

def main():
    print("=" * 70)
    print("ATUALIZAÇÃO DE LOTAÇÃO PARADIGMA - EDITAL 01/2026")
    print("=" * 70)
    print()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anexo3_path = os.path.join(base_dir, "edital e anexos", "Anexo III.xml")
    anexo4_path = os.path.join(base_dir, "edital e anexos", "Anexo IV.xml")

    # Parsear anexos
    paradigmas_unidades = parsear_anexo3(anexo3_path)
    paradigmas_direcoes = parsear_anexo4(anexo4_path)

    # Combinar mapeamentos
    mapeamento_paradigma = {}
    mapeamento_paradigma.update(paradigmas_unidades)
    mapeamento_paradigma.update(paradigmas_direcoes)

    print(f"\nTotal de paradigmas disponíveis: {len(mapeamento_paradigma)}")
    print()

    # Atualizar LOTACAO_POR_CODIGO
    print("Atualizando lotacao_data.py...")

    atualizados = []
    nao_encontrados = []

    novo_mapeamento = {}

    for codigo, dados in LOTACAO_POR_CODIGO.items():
        chave = criar_chave(dados['comarca'], dados['unidade'])

        novo_dados = dict(dados)  # Cópia

        if chave in mapeamento_paradigma:
            novo_paradigma = mapeamento_paradigma[chave]
            novo_dados['lotacao_paradigma'] = novo_paradigma
            novo_dados['diferenca'] = novo_dados['lotacao_real'] - novo_paradigma
            novo_dados['status'] = calcular_status(novo_dados['diferenca'])

            if dados['lotacao_paradigma'] != novo_paradigma:
                atualizados.append({
                    'codigo': codigo,
                    'comarca': dados['comarca'],
                    'unidade': dados['unidade'],
                    'antigo': dados['lotacao_paradigma'],
                    'novo': novo_paradigma
                })
        else:
            nao_encontrados.append({
                'codigo': codigo,
                'comarca': dados['comarca'],
                'unidade': dados['unidade'],
                'chave': chave
            })

        novo_mapeamento[codigo] = novo_dados

    print(f"  -> {len(atualizados)} unidades ATUALIZADAS")
    print(f"  -> {len(nao_encontrados)} unidades NÃO ENCONTRADAS nos anexos")
    print()

    # Mostrar algumas atualizações
    if atualizados:
        print("Exemplos de atualizações:")
        for item in atualizados[:10]:
            print(f"  {item['codigo']}: {item['comarca']} - {item['unidade'][:40]}...")
            print(f"      paradigma: {item['antigo']} -> {item['novo']}")
        if len(atualizados) > 10:
            print(f"  ... e mais {len(atualizados) - 10} atualizações")
        print()

    # Mostrar não encontrados
    if nao_encontrados:
        print("Unidades NÃO encontradas nos anexos (mantendo paradigma atual):")
        for item in nao_encontrados[:15]:
            print(f"  {item['codigo']}: {item['comarca']} - {item['unidade'][:50]}...")
        if len(nao_encontrados) > 15:
            print(f"  ... e mais {len(nao_encontrados) - 15} unidades")
        print()

    # Gerar novo arquivo
    print("Gerando novo lotacao_data.py...")

    output_lines = []
    output_lines.append('"""')
    output_lines.append('Dados de Lotação Paradigma - TJPR')
    output_lines.append(f'Atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    output_lines.append('Fonte: Anexos III e IV do Edital 01/2026')
    output_lines.append('')
    output_lines.append('Campos:')
    output_lines.append('  - lotacao_real: Mantido do arquivo anterior (atualizar manualmente)')
    output_lines.append('  - lotacao_paradigma: Atualizado dos Anexos III e IV')
    output_lines.append('  - diferenca: lotacao_real - lotacao_paradigma')
    output_lines.append('  - status: SUPERAVITÁRIA (>0), EQUILIBRADA (=0), DEFICITÁRIA (<0)')
    output_lines.append('')
    output_lines.append(f'Estatísticas:')
    output_lines.append(f'  - Total de unidades: {len(novo_mapeamento)}')
    output_lines.append(f'  - Paradigmas atualizados: {len(atualizados)}')
    output_lines.append(f'  - Não encontrados nos anexos: {len(nao_encontrados)}')
    output_lines.append('"""')
    output_lines.append('')
    output_lines.append('# Mapeamento: Código Anexo II -> Dados de Lotação')
    output_lines.append('LOTACAO_POR_CODIGO = {')

    for codigo in sorted(novo_mapeamento.keys(), key=lambda x: int(x.split('-')[1])):
        dados = novo_mapeamento[codigo]
        output_lines.append(f'    "{codigo}": {{')
        output_lines.append(f'        "comarca": "{dados["comarca"]}",')
        output_lines.append(f'        "unidade": "{dados["unidade"]}",')
        output_lines.append(f'        "lotacao_real": {dados["lotacao_real"]},')
        output_lines.append(f'        "lotacao_paradigma": {dados["lotacao_paradigma"]},')
        output_lines.append(f'        "diferenca": {dados["diferenca"]},')
        output_lines.append(f'        "status": "{dados["status"]}",')
        output_lines.append('    },')

    output_lines.append('}')
    output_lines.append('')

    # Escrever arquivo
    output_path = os.path.join(base_dir, 'lotacao_data.py')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"  -> Arquivo salvo: {output_path}")
    print()

    # Resumo final
    print("=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    print(f"  Total de unidades: {len(novo_mapeamento)}")
    print(f"  Paradigmas atualizados: {len(atualizados)}")
    print(f"  Não encontrados: {len(nao_encontrados)}")

    # Contar status
    status_count = {}
    for dados in novo_mapeamento.values():
        status = dados['status']
        status_count[status] = status_count.get(status, 0) + 1

    print(f"\nDistribuição de status:")
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count}")

    print("\nCONCLUÍDO!")

    return len(atualizados), len(nao_encontrados)

if __name__ == "__main__":
    main()
