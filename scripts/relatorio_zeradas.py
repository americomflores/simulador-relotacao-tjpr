"""
Script para gerar relatório de unidades com lotação zerada
Analisa lotação_real=0 e/ou lotacao_paradigma=0
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lotacao_data import LOTACAO_POR_CODIGO

def gerar_relatorio():
    print("=" * 80)
    print("RELATÓRIO DE UNIDADES COM LOTAÇÃO ZERADA")
    print("=" * 80)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Total de unidades: {len(LOTACAO_POR_CODIGO)}")

    # Categorizar unidades
    paradigma_zero = []
    real_zero = []
    ambos_zero = []
    normais = []

    for codigo, dados in LOTACAO_POR_CODIGO.items():
        if dados['lotacao_paradigma'] == 0 and dados['lotacao_real'] == 0:
            ambos_zero.append((codigo, dados))
        elif dados['lotacao_paradigma'] == 0:
            paradigma_zero.append((codigo, dados))
        elif dados['lotacao_real'] == 0:
            real_zero.append((codigo, dados))
        else:
            normais.append((codigo, dados))

    # Estatísticas
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS")
    print("=" * 80)
    print(f"Unidades com PARADIGMA = 0: {len(paradigma_zero)}")
    print(f"Unidades com REAL = 0: {len(real_zero)}")
    print(f"Unidades com AMBOS = 0: {len(ambos_zero)}")
    print(f"Unidades normais (sem zeros): {len(normais)}")

    # Relatório detalhado
    linhas_relatorio = []

    linhas_relatorio.append("=" * 80)
    linhas_relatorio.append("RELATÓRIO DE UNIDADES COM LOTAÇÃO ZERADA")
    linhas_relatorio.append("=" * 80)
    linhas_relatorio.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    linhas_relatorio.append(f"Total de unidades: {len(LOTACAO_POR_CODIGO)}")

    linhas_relatorio.append("\n" + "=" * 80)
    linhas_relatorio.append("ESTATÍSTICAS")
    linhas_relatorio.append("=" * 80)
    linhas_relatorio.append(f"Unidades com PARADIGMA = 0: {len(paradigma_zero)}")
    linhas_relatorio.append(f"Unidades com REAL = 0: {len(real_zero)}")
    linhas_relatorio.append(f"Unidades com AMBOS = 0: {len(ambos_zero)}")
    linhas_relatorio.append(f"Unidades normais (sem zeros): {len(normais)}")

    # Detalhamento: AMBOS ZERO
    if ambos_zero:
        linhas_relatorio.append("\n" + "=" * 80)
        linhas_relatorio.append(f"UNIDADES COM AMBOS ZERADOS ({len(ambos_zero)})")
        linhas_relatorio.append("=" * 80)
        linhas_relatorio.append("\nCód.    | Status        | Comarca - Unidade")
        linhas_relatorio.append("-" * 80)

        for codigo, dados in sorted(ambos_zero, key=lambda x: (x[1]['comarca'], x[1]['unidade'])):
            linhas_relatorio.append(
                f"{codigo:7} | {dados['status']:13} | {dados['comarca']} - {dados['unidade'][:45]}"
            )

    # Detalhamento: PARADIGMA ZERO
    if paradigma_zero:
        linhas_relatorio.append("\n" + "=" * 80)
        linhas_relatorio.append(f"UNIDADES COM PARADIGMA = 0 (mas real > 0) ({len(paradigma_zero)})")
        linhas_relatorio.append("=" * 80)
        linhas_relatorio.append("\nCód.    | Real | Status        | Comarca - Unidade")
        linhas_relatorio.append("-" * 80)

        for codigo, dados in sorted(paradigma_zero, key=lambda x: (x[1]['comarca'], x[1]['unidade'])):
            linhas_relatorio.append(
                f"{codigo:7} | {dados['lotacao_real']:4} | {dados['status']:13} | "
                f"{dados['comarca']} - {dados['unidade'][:40]}"
            )

    # Detalhamento: REAL ZERO
    if real_zero:
        linhas_relatorio.append("\n" + "=" * 80)
        linhas_relatorio.append(f"UNIDADES COM REAL = 0 (mas paradigma > 0) ({len(real_zero)})")
        linhas_relatorio.append("=" * 80)
        linhas_relatorio.append("\nCód.    | Parad | Status        | Comarca - Unidade")
        linhas_relatorio.append("-" * 80)

        for codigo, dados in sorted(real_zero, key=lambda x: (x[1]['comarca'], x[1]['unidade'])):
            linhas_relatorio.append(
                f"{codigo:7} | {dados['lotacao_paradigma']:5} | {dados['status']:13} | "
                f"{dados['comarca']} - {dados['unidade'][:40]}"
            )

    # Análise por Comarca
    linhas_relatorio.append("\n" + "=" * 80)
    linhas_relatorio.append("ANÁLISE POR COMARCA (comarcas com unidades zeradas)")
    linhas_relatorio.append("=" * 80)

    # Agrupar por comarca
    comarcas_afetadas = {}
    for codigo, dados in paradigma_zero + real_zero + ambos_zero:
        comarca = dados['comarca']
        comarcas_afetadas.setdefault(comarca, {'paradigma_zero': 0, 'real_zero': 0, 'ambos_zero': 0, 'unidades': []})

        if dados['lotacao_paradigma'] == 0 and dados['lotacao_real'] == 0:
            comarcas_afetadas[comarca]['ambos_zero'] += 1
        elif dados['lotacao_paradigma'] == 0:
            comarcas_afetadas[comarca]['paradigma_zero'] += 1
        elif dados['lotacao_real'] == 0:
            comarcas_afetadas[comarca]['real_zero'] += 1

        comarcas_afetadas[comarca]['unidades'].append({
            'codigo': codigo,
            'unidade': dados['unidade'],
            'real': dados['lotacao_real'],
            'paradigma': dados['lotacao_paradigma']
        })

    linhas_relatorio.append("\nComarca                     | P=0 | R=0 | Ambos | Total Afetadas")
    linhas_relatorio.append("-" * 80)

    for comarca in sorted(comarcas_afetadas.keys()):
        info = comarcas_afetadas[comarca]
        total = info['paradigma_zero'] + info['real_zero'] + info['ambos_zero']
        linhas_relatorio.append(
            f"{comarca:27} | {info['paradigma_zero']:3} | {info['real_zero']:3} | "
            f"{info['ambos_zero']:5} | {total:14}"
        )

    # Detalhamento por comarca
    linhas_relatorio.append("\n" + "=" * 80)
    linhas_relatorio.append("DETALHAMENTO POR COMARCA")
    linhas_relatorio.append("=" * 80)

    for comarca in sorted(comarcas_afetadas.keys()):
        info = comarcas_afetadas[comarca]
        linhas_relatorio.append(f"\n{comarca}")
        linhas_relatorio.append("-" * 80)

        for unidade in sorted(info['unidades'], key=lambda x: x['unidade']):
            tipo = ""
            if unidade['paradigma'] == 0 and unidade['real'] == 0:
                tipo = "[AMBOS=0]"
            elif unidade['paradigma'] == 0:
                tipo = "[PARAD=0]"
            else:
                tipo = "[REAL=0]"

            linhas_relatorio.append(
                f"  {unidade['codigo']} {tipo:11} R:{unidade['real']:3} P:{unidade['paradigma']:3} - "
                f"{unidade['unidade'][:50]}"
            )

    linhas_relatorio.append("\n" + "=" * 80)
    linhas_relatorio.append("FIM DO RELATÓRIO")
    linhas_relatorio.append("=" * 80)

    # Exibir no console
    for linha in linhas_relatorio:
        print(linha)

    # Salvar em arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    Path("relatorios").mkdir(exist_ok=True)
    arquivo_relatorio = f"relatorios/relatorio_zeradas_{timestamp}.txt"

    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas_relatorio))

    print(f"\n[OK] Relatório salvo em: {arquivo_relatorio}")

    return 0

if __name__ == '__main__':
    sys.exit(gerar_relatorio())
