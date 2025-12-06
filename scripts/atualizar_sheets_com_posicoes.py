"""
Script para atualizar Google Sheets com coluna posicao_lista_classificatoria

Adiciona coluna K e preenche com posições da lista classificatória usando fuzzy matching.
"""

import sys
from pathlib import Path
from fuzzywuzzy import fuzz

# Adicionar pasta parent ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from services.sheets_service import conectar_sheets
from lista_classificatoria import LISTA_CLASSIFICATORIA


def buscar_posicao_por_nome(nome_inscricao: str, threshold: int = 85):
    """
    Busca posição na lista classificatória por nome usando fuzzy matching.

    Args:
        nome_inscricao: Nome do servidor na inscrição
        threshold: Limite mínimo de similaridade (0-100)

    Returns:
        Tupla (posicao, score, nome_display) ou None se não encontrar
    """
    melhor_match = None
    melhor_score = 0
    melhor_nome = ""

    nome_busca = nome_inscricao.upper().strip()

    for posicao, dados in LISTA_CLASSIFICATORIA.items():
        # Tenta match com nome original (sem numeração)
        score_original = fuzz.ratio(nome_busca, dados["nome_original"].upper())

        # Tenta match com nome display (com numeração se houver)
        score_display = fuzz.ratio(nome_busca, dados["nome_display"].upper())

        # Usa o melhor score
        score = max(score_original, score_display)

        if score > melhor_score:
            melhor_score = score
            melhor_match = posicao
            melhor_nome = dados["nome_display"]

    if melhor_score >= threshold:
        return (melhor_match, melhor_score, melhor_nome)

    return None


def main():
    """Função principal"""
    # Configure encoding for Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("ATUALIZAÇÃO DO GOOGLE SHEETS - COLUNA POSICAO_LISTA_CLASSIFICATORIA")
    print("=" * 80)
    print()

    # Conectar ao Google Sheets
    print("[CONECTANDO] Conectando ao Google Sheets...")
    try:
        sheet = conectar_sheets()
        print("   [OK] Conexão estabelecida")
    except Exception as e:
        print(f"   [ERRO] Falha na conexão: {e}")
        return
    print()

    # Verificar cabeçalhos atuais
    print("[VERIFICANDO] Lendo cabeçalhos...")
    cabecalhos = sheet.row_values(1)
    print(f"   [OK] {len(cabecalhos)} colunas encontradas")
    print(f"   Colunas: {', '.join(cabecalhos)}")
    print()

    # Adicionar coluna K se não existir
    if "posicao_lista_classificatoria" not in cabecalhos:
        print("[ATUALIZANDO] Adicionando coluna K 'posicao_lista_classificatoria'...")
        try:
            sheet.update('K1', [["posicao_lista_classificatoria"]])
            print("   [OK] Coluna K adicionada")
        except Exception as e:
            print(f"   [ERRO] Falha ao adicionar coluna: {e}")
            return
    else:
        print("[INFO] Coluna 'posicao_lista_classificatoria' já existe")
    print()

    # Carregar todos os registros
    print("[LENDO] Carregando registros existentes...")
    try:
        registros = sheet.get_all_records()
        print(f"   [OK] {len(registros)} registros encontrados")
    except Exception as e:
        print(f"   [ERRO] Falha ao carregar registros: {e}")
        return
    print()

    # Processar cada registro
    print("[PROCESSANDO] Fazendo matching de nomes e atualizando posições...")
    print()

    atualizados = 0
    nao_encontrados = []
    revisao_manual = []

    for i, registro in enumerate(registros, start=2):  # Linha 2 em diante (1 é cabeçalho)
        nome = registro.get("nome", "").strip()

        if not nome:
            print(f"   [AVISO] Linha {i}: Nome vazio, pulando")
            continue

        # Buscar posição
        resultado = buscar_posicao_por_nome(nome)

        if resultado:
            posicao, score, nome_lista = resultado

            if score >= 95:  # Match excelente
                # Atualizar célula K
                try:
                    sheet.update(f'K{i}', [[posicao]])
                    atualizados += 1
                    print(f"   [OK] Linha {i:3d} | Pos {posicao:4d} | {score}% | {nome}")
                    if nome.upper() != nome_lista.upper():
                        print(f"             → Lista: {nome_lista}")
                except Exception as e:
                    print(f"   [ERRO] Linha {i}: Falha ao atualizar - {e}")

            else:  # Match bom mas requer revisão (85-94%)
                # Atualizar mesmo assim, mas marcar para revisão
                try:
                    sheet.update(f'K{i}', [[posicao]])
                    atualizados += 1
                    revisao_manual.append({
                        "linha": i,
                        "nome_inscricao": nome,
                        "posicao": posicao,
                        "score": score,
                        "nome_lista": nome_lista
                    })
                    print(f"   [ATENÇÃO] Linha {i:3d} | Pos {posicao:4d} | {score}% | {nome}")
                    print(f"             → Lista: {nome_lista}")
                except Exception as e:
                    print(f"   [ERRO] Linha {i}: Falha ao atualizar - {e}")

        else:
            nao_encontrados.append({
                "linha": i,
                "nome_inscricao": nome
            })
            print(f"   [NÃO ENCONTRADO] Linha {i}: {nome}")

    print()
    print("=" * 80)
    print("RELATÓRIO DE ATUALIZAÇÃO")
    print("=" * 80)
    print(f"Total de registros processados: {len(registros)}")
    print(f"Atualizados com sucesso: {atualizados}")
    print(f"Requer revisão manual (85-94%): {len(revisao_manual)}")
    print(f"Não encontrados (<85%): {len(nao_encontrados)}")
    print()

    if revisao_manual:
        print("[ATENÇÃO] REGISTROS QUE REQUEREM REVISÃO MANUAL:")
        print()
        for item in revisao_manual:
            print(f"   Linha {item['linha']}: '{item['nome_inscricao']}'")
            print(f"   → Match {item['score']}% com Pos {item['posicao']}: '{item['nome_lista']}'")
            print()

    if nao_encontrados:
        print("[ERRO] REGISTROS NÃO ENCONTRADOS:")
        print()
        for item in nao_encontrados:
            print(f"   Linha {item['linha']}: '{item['nome_inscricao']}'")

            # Buscar top 3 matches
            matches = []
            nome_busca = item['nome_inscricao'].upper().strip()
            for pos, dados in LISTA_CLASSIFICATORIA.items():
                score = fuzz.ratio(nome_busca, dados["nome_original"].upper())
                matches.append((pos, score, dados["nome_display"]))
            matches.sort(key=lambda x: x[1], reverse=True)

            print(f"      Top 3 sugestões:")
            for pos, score, nome in matches[:3]:
                print(f"         {score}% - Pos {pos}: {nome}")
            print()

    print("=" * 80)
    print("[CONCLUÍDO] ATUALIZAÇÃO FINALIZADA")
    print("=" * 80)
    print()

    if revisao_manual or nao_encontrados:
        print("⚠️  ATENÇÃO: Há registros que precisam de revisão manual!")
        print("   Por favor, verifique os casos listados acima.")
    else:
        print("✓ Todos os registros foram atualizados com sucesso!")


if __name__ == "__main__":
    main()
