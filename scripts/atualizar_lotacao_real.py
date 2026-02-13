"""
Script para atualizar lotacao_real em lotacao_data.py
usando os dados do arquivo LotacaoReal.csv

Estratégia de mapeamento em 3 níveis:
1. Correspondência exata (normalizada)
2. Heurísticas por tipo de unidade
3. Fuzzy matching (difflib)

Regras especiais:
- Secretarias da Direção: IGNORAR (não estão no CSV)
- Unidades com Lotacao Real = 0: MANTER valor atual, registrar em arquivo separado
"""

import sys
import os
import csv
import re
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lotacao_data import LOTACAO_POR_CODIGO, LOTACAO_COMPLETA


def normalizar_texto(texto):
    """Normaliza texto para comparação: remove acentos, maiúscula, espaços extras"""
    if not texto:
        return ""
    # Remove acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Maiúscula e remove espaços extras
    texto = texto.upper().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def extrair_numero_vara(texto):
    """Extrai número da vara (1ª, 2ª, etc.)"""
    match = re.search(r'(\d+)[ªº]', texto)
    if match:
        return int(match.group(1))
    return None


def extrair_tipo_unidade(texto):
    """Extrai o tipo principal da unidade"""
    texto_norm = normalizar_texto(texto)

    if 'JUIZO UNICO' in texto_norm:
        return 'JUIZO_UNICO'
    elif 'JUIZADO ESPECIAL' in texto_norm:
        return 'JUIZADO'
    elif 'VARA CRIMINAL' in texto_norm:
        num = extrair_numero_vara(texto)
        return f'VARA_CRIMINAL_{num}' if num else 'VARA_CRIMINAL'
    elif 'VARA CIVEL' in texto_norm or 'VARA DA FAZENDA' in texto_norm:
        num = extrair_numero_vara(texto)
        return f'VARA_CIVEL_{num}' if num else 'VARA_CIVEL'
    elif 'VARA DE FAMILIA' in texto_norm or 'FAMILIA E SUCESSOES' in texto_norm:
        return 'VARA_FAMILIA'
    elif 'INFANCIA E JUVENTUDE' in texto_norm:
        return 'INFANCIA_JUVENTUDE'
    elif 'EXECUCOES PENAIS' in texto_norm:
        return 'EXECUCOES_PENAIS'
    elif 'VIOLENCIA DOMESTICA' in texto_norm:
        return 'VIOLENCIA_DOMESTICA'

    return None


def similaridade(s1, s2):
    """Calcula similaridade entre duas strings (0-100)"""
    return SequenceMatcher(None, normalizar_texto(s1), normalizar_texto(s2)).ratio() * 100


def encontrar_correspondencia(unidade_data, unidades_csv):
    """
    Encontra a melhor correspondência para uma unidade do lotacao_data
    nas unidades do CSV da mesma comarca.

    Retorna: (unidade_csv, nivel_match, score) ou (None, None, 0)
    """
    unidade_norm = normalizar_texto(unidade_data)

    # Nível 1: Correspondência exata
    for u_csv in unidades_csv:
        if normalizar_texto(u_csv['Unidade']) == unidade_norm:
            return (u_csv, 1, 100)

    # Nível 2: Heurísticas por tipo
    tipo_data = extrair_tipo_unidade(unidade_data)

    if tipo_data == 'JUIZO_UNICO':
        # Juízo Único mapeia para qualquer "Juízo Único..." no CSV
        for u_csv in unidades_csv:
            if 'JUIZO UNICO' in normalizar_texto(u_csv['Unidade']):
                return (u_csv, 2, 95)

    elif tipo_data and tipo_data.startswith('VARA_CRIMINAL'):
        num = extrair_numero_vara(unidade_data)
        for u_csv in unidades_csv:
            csv_norm = normalizar_texto(u_csv['Unidade'])
            if 'VARA CRIMINAL' in csv_norm:
                csv_num = extrair_numero_vara(u_csv['Unidade'])
                if num == csv_num:
                    return (u_csv, 2, 95)
                elif num is None and csv_num is None:
                    return (u_csv, 2, 90)

    elif tipo_data and tipo_data.startswith('VARA_CIVEL'):
        num = extrair_numero_vara(unidade_data)
        for u_csv in unidades_csv:
            csv_norm = normalizar_texto(u_csv['Unidade'])
            if 'VARA CIVEL' in csv_norm or 'FAZENDA PUBLICA' in csv_norm:
                csv_num = extrair_numero_vara(u_csv['Unidade'])
                if num == csv_num:
                    return (u_csv, 2, 95)
                elif num is None and csv_num is None:
                    return (u_csv, 2, 85)

    elif tipo_data == 'VARA_FAMILIA':
        for u_csv in unidades_csv:
            csv_norm = normalizar_texto(u_csv['Unidade'])
            if 'FAMILIA' in csv_norm and 'SUCESSOES' in csv_norm:
                return (u_csv, 2, 90)

    elif tipo_data == 'JUIZADO':
        for u_csv in unidades_csv:
            csv_norm = normalizar_texto(u_csv['Unidade'])
            if 'JUIZADO ESPECIAL' in csv_norm:
                # Verificar se é o mesmo tipo de juizado (1º, 2º, etc.)
                num_data = extrair_numero_vara(unidade_data)
                num_csv = extrair_numero_vara(u_csv['Unidade'])
                if num_data == num_csv:
                    return (u_csv, 2, 95)
                elif num_data is None and num_csv is None:
                    return (u_csv, 2, 85)

    # Nível 3: Fuzzy matching
    melhor_score = 0
    melhor_match = None

    for u_csv in unidades_csv:
        score = similaridade(unidade_data, u_csv['Unidade'])
        if score > melhor_score:
            melhor_score = score
            melhor_match = u_csv

    if melhor_score >= 80:
        return (melhor_match, 3, melhor_score)

    return (None, None, 0)


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
    print("ATUALIZAÇÃO DE LOTAÇÃO REAL - EDITAL 01/2026")
    print("=" * 70)
    print()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "edital e anexos", "LotacaoReal.csv")

    # 1. Ler CSV
    print(f"Lendo CSV: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        csv_data = list(reader)
    print(f"  -> {len(csv_data)} linhas lidas")

    # 2. Indexar por comarca
    csv_por_comarca = {}
    for row in csv_data:
        comarca = normalizar_texto(row['Comarca'])
        if comarca not in csv_por_comarca:
            csv_por_comarca[comarca] = []
        csv_por_comarca[comarca].append(row)
    print(f"  -> {len(csv_por_comarca)} comarcas no CSV")
    print()

    # 3. Processar lotacao_data
    print("Processando lotacao_data.py...")

    mapeados = []
    nao_mapeados = []
    zerados = []
    ignorados_secretaria = []

    novo_mapeamento = {}

    for codigo, dados in LOTACAO_POR_CODIGO.items():
        novo_dados = dict(dados)
        comarca_norm = normalizar_texto(dados['comarca'])

        # Ignorar Secretarias da Direção
        if 'SECRETARIA DA DIREÇÃO' in dados['unidade'].upper():
            ignorados_secretaria.append({
                'codigo': codigo,
                'comarca': dados['comarca'],
                'unidade': dados['unidade']
            })
            novo_mapeamento[codigo] = novo_dados
            continue

        # Buscar correspondência
        if comarca_norm in csv_por_comarca:
            match, nivel, score = encontrar_correspondencia(
                dados['unidade'],
                csv_por_comarca[comarca_norm]
            )

            if match:
                lotacao_csv = int(match['Lotacao Real'])

                # Se lotação é 0, manter valor atual e registrar
                if lotacao_csv == 0:
                    zerados.append({
                        'codigo': codigo,
                        'comarca': dados['comarca'],
                        'unidade': dados['unidade'],
                        'unidade_csv': match['Unidade'],
                        'lotacao_atual': dados['lotacao_real'],
                        'nivel_match': nivel,
                        'score': score
                    })
                    # Manter valor atual
                    novo_mapeamento[codigo] = novo_dados
                else:
                    # Atualizar com valor do CSV
                    novo_dados['lotacao_real'] = lotacao_csv
                    novo_dados['diferenca'] = lotacao_csv - novo_dados['lotacao_paradigma']
                    novo_dados['status'] = calcular_status(novo_dados['diferenca'])

                    mapeados.append({
                        'codigo': codigo,
                        'comarca': dados['comarca'],
                        'unidade': dados['unidade'],
                        'unidade_csv': match['Unidade'],
                        'lotacao_anterior': dados['lotacao_real'],
                        'lotacao_nova': lotacao_csv,
                        'nivel_match': nivel,
                        'score': score
                    })
                    novo_mapeamento[codigo] = novo_dados
            else:
                nao_mapeados.append({
                    'codigo': codigo,
                    'comarca': dados['comarca'],
                    'unidade': dados['unidade']
                })
                novo_mapeamento[codigo] = novo_dados
        else:
            nao_mapeados.append({
                'codigo': codigo,
                'comarca': dados['comarca'],
                'unidade': dados['unidade'],
                'motivo': 'Comarca não encontrada no CSV'
            })
            novo_mapeamento[codigo] = novo_dados

    # 4. Relatório
    print()
    print("=" * 70)
    print("RELATÓRIO DE MAPEAMENTO")
    print("=" * 70)
    print(f"  Secretarias da Direção (ignoradas): {len(ignorados_secretaria)}")
    print(f"  Unidades mapeadas com sucesso:      {len(mapeados)}")
    print(f"  Unidades com valor 0 (mantidas):    {len(zerados)}")
    print(f"  Unidades NÃO mapeadas:              {len(nao_mapeados)}")
    print()

    # Estatísticas por nível
    nivel_1 = sum(1 for m in mapeados if m['nivel_match'] == 1)
    nivel_2 = sum(1 for m in mapeados if m['nivel_match'] == 2)
    nivel_3 = sum(1 for m in mapeados if m['nivel_match'] == 3)
    print(f"  Mapeamentos por nível:")
    print(f"    Nível 1 (exato):      {nivel_1}")
    print(f"    Nível 2 (heurística): {nivel_2}")
    print(f"    Nível 3 (fuzzy):      {nivel_3}")
    print()

    # Mostrar alguns exemplos de mapeamento
    if mapeados:
        print("Exemplos de mapeamentos (mudanças):")
        mudancas = [m for m in mapeados if m['lotacao_anterior'] != m['lotacao_nova']][:10]
        for m in mudancas:
            print(f"  {m['codigo']}: {m['comarca']} - {m['unidade'][:40]}...")
            print(f"      CSV: {m['unidade_csv'][:50]}...")
            print(f"      lotacao: {m['lotacao_anterior']} -> {m['lotacao_nova']} (nível {m['nivel_match']})")
        if len(mudancas) > 10:
            print(f"  ... e mais {len(mudancas) - 10} mudanças")
        print()

    # Mostrar não mapeados
    if nao_mapeados:
        print("Unidades NÃO mapeadas:")
        for item in nao_mapeados[:15]:
            print(f"  {item['codigo']}: {item['comarca']} - {item['unidade'][:50]}...")
        if len(nao_mapeados) > 15:
            print(f"  ... e mais {len(nao_mapeados) - 15} unidades")
        print()

    # 5. Salvar arquivo de unidades zeradas
    if zerados:
        zerados_path = os.path.join(base_dir, "unidades_zeradas.csv")
        with open(zerados_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'codigo', 'comarca', 'unidade', 'unidade_csv',
                'lotacao_atual', 'nivel_match', 'score'
            ], delimiter=';')
            writer.writeheader()
            writer.writerows(zerados)
        print(f"Arquivo de unidades zeradas salvo: {zerados_path}")
        print()

    # 6. Gerar novo lotacao_data.py
    print("Gerando novo lotacao_data.py...")

    output_lines = []
    output_lines.append('"""')
    output_lines.append('Dados de Lotação Paradigma - TJPR')
    output_lines.append(f'Atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    output_lines.append('Fonte: LotacaoReal.csv + Anexos III e IV do Edital 01/2026')
    output_lines.append('')
    output_lines.append('Campos:')
    output_lines.append('  - lotacao_real: Atualizado de LotacaoReal.csv')
    output_lines.append('  - lotacao_paradigma: Atualizado dos Anexos III e IV')
    output_lines.append('  - diferenca: lotacao_real - lotacao_paradigma')
    output_lines.append('  - status: SUPERAVITÁRIA (>0), EQUILIBRADA (=0), DEFICITÁRIA (<0)')
    output_lines.append('')
    output_lines.append(f'Estatísticas de atualização:')
    output_lines.append(f'  - Total de unidades: {len(novo_mapeamento)}')
    output_lines.append(f'  - lotacao_real atualizado: {len(mapeados)}')
    output_lines.append(f'  - Secretarias ignoradas: {len(ignorados_secretaria)}')
    output_lines.append(f'  - Unidades zeradas (mantidas): {len(zerados)}')
    output_lines.append(f'  - Não mapeadas: {len(nao_mapeados)}')
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

    # Gerar LOTACAO_COMPLETA
    output_lines.append('# Lista completa de lotação (para compatibilidade)')
    output_lines.append('LOTACAO_COMPLETA = [')
    for codigo in sorted(novo_mapeamento.keys(), key=lambda x: int(x.split('-')[1])):
        dados = novo_mapeamento[codigo]
        output_lines.append('    {')
        output_lines.append(f'        "codigo": "{codigo}",')
        output_lines.append(f'        "comarca": "{dados["comarca"]}",')
        output_lines.append(f'        "unidade": "{dados["unidade"]}",')
        output_lines.append(f'        "lotacao_real": {dados["lotacao_real"]},')
        output_lines.append(f'        "lotacao_paradigma": {dados["lotacao_paradigma"]},')
        output_lines.append(f'        "diferenca": {dados["diferenca"]},')
        output_lines.append(f'        "status": "{dados["status"]}",')
        output_lines.append('    },')
    output_lines.append(']')
    output_lines.append('')

    # Escrever arquivo
    output_path = os.path.join(base_dir, 'lotacao_data.py')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"  -> Arquivo salvo: {output_path}")
    print()

    # 7. Resumo final
    print("=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    print(f"  Total de unidades: {len(novo_mapeamento)}")
    print(f"  Lotação real atualizada: {len(mapeados)}")
    print(f"  Secretarias ignoradas: {len(ignorados_secretaria)}")
    print(f"  Unidades zeradas: {len(zerados)}")
    print(f"  Não mapeadas: {len(nao_mapeados)}")

    # Contar status
    status_count = {}
    for dados in novo_mapeamento.values():
        status = dados['status']
        status_count[status] = status_count.get(status, 0) + 1

    print(f"\nDistribuição de status:")
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count}")

    print("\nCONCLUÍDO!")

    return len(mapeados), len(nao_mapeados), len(zerados)


if __name__ == "__main__":
    main()
