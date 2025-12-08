#!/usr/bin/env python3
"""
Script para processar as inscrições reais do edital e mapear para os códigos A1 e A2
"""

import csv
import sys
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, Optional, Tuple

# Adiciona o diretório raiz ao path para importar data.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from data import ANEXO_I, ANEXO_II


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparação (maiúsculas, remove espaços extras)"""
    if not texto:
        return ""
    return " ".join(texto.upper().split())


def calcular_similaridade(str1: str, str2: str) -> float:
    """Calcula similaridade entre duas strings (0.0 a 1.0)"""
    return SequenceMatcher(None,
                          normalizar_texto(str1),
                          normalizar_texto(str2)).ratio()


def construir_indice_unidades() -> Dict[str, Dict]:
    """
    Constrói um índice de todas as unidades dos anexos I e II
    Retorna: {codigo: {comarca, unidade, anexo}}
    """
    indice = {}

    # Anexo I
    for codigo, info in ANEXO_I.items():
        indice[codigo] = {
            'comarca': info['comarca'],
            'unidade': info['unidade'],
            'anexo': 'I',
            'codigo': codigo
        }

    # Anexo II
    for codigo, info in ANEXO_II.items():
        indice[codigo] = {
            'comarca': info['comarca'],
            'unidade': info['unidade'],
            'anexo': 'II',
            'codigo': codigo
        }

    return indice


def buscar_codigo_unidade(nome_unidade: str, comarca: str, indice: Dict, anexo_preferido: str = None) -> Optional[Tuple[str, float]]:
    """
    Busca o código da unidade usando fuzzy matching

    Args:
        nome_unidade: Nome da unidade a procurar
        comarca: Nome da comarca (para ajudar no matching)
        indice: Índice de unidades
        anexo_preferido: 'I' ou 'II' para filtrar por anexo

    Returns:
        Tupla (codigo, score) ou None se não encontrar match bom
    """
    melhor_match = None
    melhor_score = 0.0

    nome_normalizado = normalizar_texto(nome_unidade)
    comarca_normalizada = normalizar_texto(comarca) if comarca else ""

    for codigo, info in indice.items():
        # Se anexo_preferido está definido, filtra por ele
        if anexo_preferido and info['anexo'] != anexo_preferido:
            continue

        # Calcula score da unidade
        score_unidade = calcular_similaridade(nome_unidade, info['unidade'])

        # Bonus se a comarca bate
        bonus_comarca = 0.0
        if comarca:
            score_comarca = calcular_similaridade(comarca, info['comarca'])
            if score_comarca > 0.8:  # Comarca muito similar
                bonus_comarca = 0.2

        score_final = score_unidade + bonus_comarca

        if score_final > melhor_score:
            melhor_score = score_final
            melhor_match = codigo

    # Só retorna se o score for razoável
    if melhor_score >= 0.75:
        return (melhor_match, melhor_score)

    return None


def processar_inscricoes_reais(csv_input: str, csv_output: str):
    """
    Processa o CSV de inscrições reais e mapeia para códigos A1/A2
    """
    indice = construir_indice_unidades()

    inscricoes = []
    erros = []

    print("🔍 Processando inscrições reais...")
    print(f"📁 Arquivo de entrada: {csv_input}")
    print(f"📁 Arquivo de saída: {csv_output}\n")

    # Lê o CSV de entrada
    with open(csv_input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        linhas = list(reader)

    print(f"📊 Total de linhas: {len(linhas)}\n")

    # Agrupa por servidor (cada servidor pode ter até 2 inscrições: I e II)
    inscricoes_por_servidor = {}

    for idx, linha in enumerate(linhas, 1):
        posicao = linha['Posição'].strip()
        servidor = linha['Servidor'].strip()
        anexo = linha['Anexo I/II'].strip()
        vaga = linha['Vaga'].strip()
        a1_preenchido = linha.get('A1', '').strip()
        a2_preenchido = linha.get('A2', '').strip()

        # Extrai comarca do nome da vaga (última parte após " - ")
        partes_vaga = vaga.split(' - ')
        comarca = partes_vaga[-1] if len(partes_vaga) > 1 else ""

        # Se já tem código preenchido manualmente, usa ele
        if anexo == 'I' and a1_preenchido:
            codigo = a1_preenchido
            score = 1.0
            print(f"✅ Linha {idx}: {servidor} - Anexo I - Código manual: {codigo}")
        elif anexo == 'II' and a2_preenchido:
            codigo = a2_preenchido
            score = 1.0
            print(f"✅ Linha {idx}: {servidor} - Anexo II - Código manual: {codigo}")
        else:
            # Busca automaticamente
            resultado = buscar_codigo_unidade(vaga, comarca, indice, anexo_preferido=anexo)

            if resultado:
                codigo, score = resultado
                info = indice[codigo]
                print(f"✅ Linha {idx}: {servidor} - Anexo {anexo}")
                print(f"   Vaga: {vaga}")
                print(f"   → Código: {codigo} ({info['unidade']}) - Score: {score:.2f}")
            else:
                codigo = None
                score = 0.0
                print(f"❌ Linha {idx}: {servidor} - Anexo {anexo} - NÃO ENCONTRADO")
                print(f"   Vaga: {vaga}")
                erros.append({
                    'linha': idx,
                    'servidor': servidor,
                    'posicao': posicao,
                    'anexo': anexo,
                    'vaga': vaga,
                    'comarca': comarca
                })

        # Armazena a inscrição
        if servidor not in inscricoes_por_servidor:
            inscricoes_por_servidor[servidor] = {
                'posicao': posicao,
                'escolha_anexo1': '',
                'escolha_anexo2': '',
                'inscricoes': []
            }

        inscricoes_por_servidor[servidor]['inscricoes'].append({
            'anexo': anexo,
            'codigo': codigo,
            'vaga': vaga,
            'score': score
        })

        if anexo == 'I' and codigo:
            inscricoes_por_servidor[servidor]['escolha_anexo1'] = codigo
        elif anexo == 'II' and codigo:
            inscricoes_por_servidor[servidor]['escolha_anexo2'] = codigo

    print("\n" + "="*80)
    print("📊 RESUMO DO PROCESSAMENTO")
    print("="*80)
    print(f"✅ Total de servidores: {len(inscricoes_por_servidor)}")
    print(f"✅ Total de mapeamentos bem-sucedidos: {len(linhas) - len(erros)}")
    print(f"❌ Total de erros: {len(erros)}\n")

    if erros:
        print("⚠️  ERROS ENCONTRADOS:")
        print("-"*80)
        for erro in erros:
            print(f"Linha {erro['linha']}: {erro['servidor']} (Pos. {erro['posicao']})")
            print(f"  Anexo {erro['anexo']}: {erro['vaga']}")
            print(f"  Comarca: {erro['comarca']}\n")

        # Salva erros em arquivo
        erro_file = csv_output.replace('.csv', '_erros.csv')
        with open(erro_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['linha', 'servidor', 'posicao', 'anexo', 'vaga', 'comarca'])
            writer.writeheader()
            writer.writerows(erros)
        print(f"📁 Erros salvos em: {erro_file}\n")

    # Gera CSV de saída no formato do Google Sheets
    print("💾 Gerando CSV de saída...")

    with open(csv_output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'nome', 'matricula', 'data_admissao', 'lotacao_atual',
            'escolha_anexo1', 'escolha_anexo2', 'data_inscricao',
            'registrado_por', 'alterado_por', 'data_alteracao',
            'posicao_lista_classificatoria'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for servidor, dados in inscricoes_por_servidor.items():
            writer.writerow({
                'nome': servidor,
                'matricula': '',  # Será preenchido manualmente ou via fuzzy matching com base existente
                'data_admissao': '',
                'lotacao_atual': '',
                'escolha_anexo1': dados['escolha_anexo1'],
                'escolha_anexo2': dados['escolha_anexo2'],
                'data_inscricao': '08/12/2025',  # Data de processamento
                'registrado_por': 'SISTEMA',
                'alterado_por': 'SISTEMA',
                'data_alteracao': '08/12/2025',
                'posicao_lista_classificatoria': dados['posicao']
            })

    print(f"✅ CSV gerado: {csv_output}")
    print(f"📊 Total de registros: {len(inscricoes_por_servidor)}")

    return len(erros) == 0


if __name__ == '__main__':
    # Paths
    script_dir = Path(__file__).parent
    input_csv = script_dir / 'inscricoes_reais.csv'
    output_csv = script_dir / 'inscricoes_reais_processadas.csv'

    if not input_csv.exists():
        print(f"❌ Arquivo não encontrado: {input_csv}")
        print("\nCrie o arquivo 'inscricoes_reais.csv' no diretório scripts/")
        sys.exit(1)

    sucesso = processar_inscricoes_reais(str(input_csv), str(output_csv))

    if sucesso:
        print("\n✅ Processamento concluído com sucesso!")
    else:
        print("\n⚠️  Processamento concluído com erros. Revise o arquivo de erros.")
