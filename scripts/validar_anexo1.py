"""
Script para validar consistência entre Anexo I e lotacao_data.py

Lógica:
- Anexo I oferece vagas para unidades DEFICITÁRIAS
- Se oferece 2 vagas → déficit deveria ser -2
- Se oferece 4 vagas → déficit deveria ser -4

Fórmula: diferenca_esperada = -vagas_oferecidas

Saída:
- discrepancias_anexo1.csv: Unidades onde o déficit não bate com as vagas oferecidas
"""

import sys
import os
import csv
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import ANEXO_I
from lotacao_data import LOTACAO_POR_CODIGO


def main():
    print("=" * 70)
    print("VALIDAÇÃO DE CONSISTÊNCIA: ANEXO I vs LOTACAO_DATA")
    print("=" * 70)
    print()

    consistentes = []
    discrepancias = []

    for codigo_a1, dados_a1 in ANEXO_I.items():
        comarca = dados_a1['comarca']
        unidade = dados_a1['unidade']
        vagas_oferecidas = dados_a1['quantidade']
        deficit_esperado = -vagas_oferecidas

        # Buscar no lotacao_data pela comarca + unidade (case insensitive)
        encontrado = None
        for codigo_a2, dados_a2 in LOTACAO_POR_CODIGO.items():
            if (dados_a2['comarca'].upper() == comarca.upper() and
                dados_a2['unidade'].upper() == unidade.upper()):
                encontrado = (codigo_a2, dados_a2)
                break

        if encontrado:
            codigo_a2, dados_a2 = encontrado
            diferenca_atual = dados_a2['diferenca']

            if diferenca_atual == deficit_esperado:
                consistentes.append({
                    'codigo_a1': codigo_a1,
                    'codigo_a2': codigo_a2,
                    'comarca': comarca,
                    'unidade': unidade,
                    'vagas_oferecidas': vagas_oferecidas,
                    'diferenca': diferenca_atual
                })
            else:
                discrepancias.append({
                    'codigo_a1': codigo_a1,
                    'codigo_a2': codigo_a2,
                    'comarca': comarca,
                    'unidade': unidade,
                    'vagas_oferecidas': vagas_oferecidas,
                    'deficit_esperado': deficit_esperado,
                    'diferenca_atual': diferenca_atual,
                    'lotacao_real': dados_a2['lotacao_real'],
                    'lotacao_paradigma': dados_a2['lotacao_paradigma'],
                    'tipo_discrepancia': 'NAO_BATE'
                })
        else:
            discrepancias.append({
                'codigo_a1': codigo_a1,
                'codigo_a2': 'NAO_ENCONTRADO',
                'comarca': comarca,
                'unidade': unidade,
                'vagas_oferecidas': vagas_oferecidas,
                'deficit_esperado': deficit_esperado,
                'diferenca_atual': 'N/A',
                'lotacao_real': 'N/A',
                'lotacao_paradigma': 'N/A',
                'tipo_discrepancia': 'NAO_ENCONTRADO'
            })

    # Relatório
    print(f"Total no Anexo I: {len(ANEXO_I)}")
    print(f"Consistentes:     {len(consistentes)} ({100*len(consistentes)/len(ANEXO_I):.1f}%)")
    print(f"Discrepâncias:    {len(discrepancias)} ({100*len(discrepancias)/len(ANEXO_I):.1f}%)")
    print()

    # Separar por tipo
    nao_bate = [d for d in discrepancias if d['tipo_discrepancia'] == 'NAO_BATE']
    nao_encontrado = [d for d in discrepancias if d['tipo_discrepancia'] == 'NAO_ENCONTRADO']

    print(f"  Diferença não bate:    {len(nao_bate)}")
    print(f"  Unidade não encontrada: {len(nao_encontrado)}")
    print()

    # Mostrar discrepâncias
    if discrepancias:
        print("=" * 70)
        print("DISCREPÂNCIAS ENCONTRADAS")
        print("=" * 70)
        print()

        print("### DIFERENÇA NÃO BATE ###")
        for d in nao_bate[:15]:
            print(f"{d['codigo_a1']} -> {d['codigo_a2']}: {d['comarca']} - {d['unidade'][:45]}...")
            print(f"   Vagas oferecidas: {d['vagas_oferecidas']} -> deficit esperado: {d['deficit_esperado']}")
            print(f"   Diferença atual: {d['diferenca_atual']} (real: {d['lotacao_real']}, paradigma: {d['lotacao_paradigma']})")
            print()
        if len(nao_bate) > 15:
            print(f"... e mais {len(nao_bate) - 15} discrepâncias deste tipo")
        print()

        print("### UNIDADE NÃO ENCONTRADA ###")
        for d in nao_encontrado[:15]:
            print(f"{d['codigo_a1']}: {d['comarca']} - {d['unidade'][:50]}...")
            print(f"   Vagas oferecidas: {d['vagas_oferecidas']}")
            print()
        if len(nao_encontrado) > 15:
            print(f"... e mais {len(nao_encontrado) - 15} unidades não encontradas")
        print()

    # Salvar CSV de discrepâncias
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "discrepancias_anexo1.csv")

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'codigo_a1', 'codigo_a2', 'comarca', 'unidade',
            'vagas_oferecidas', 'deficit_esperado', 'diferenca_atual',
            'lotacao_real', 'lotacao_paradigma', 'tipo_discrepancia'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(discrepancias)

    print(f"Arquivo de discrepâncias salvo: {csv_path}")
    print()

    # Resumo final
    print("=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"Total no Anexo I:      {len(ANEXO_I)}")
    print(f"Consistentes:          {len(consistentes)}")
    print(f"Discrepâncias:         {len(discrepancias)}")
    print(f"  - Diferença não bate:    {len(nao_bate)}")
    print(f"  - Unidade não encontrada: {len(nao_encontrado)}")
    print()
    print("CONCLUÍDO!")

    return len(consistentes), len(discrepancias)


if __name__ == "__main__":
    main()
