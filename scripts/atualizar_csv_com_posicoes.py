"""
Script para atualizar CSV local com coluna posicao_lista_classificatoria

Lê o CSV existente, adiciona coluna com posições via fuzzy matching, e salva novo CSV.
"""

import pandas as pd
import sys
from pathlib import Path
from fuzzywuzzy import fuzz

# Adicionar pasta parent ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
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
    print("ATUALIZAÇÃO DO CSV - COLUNA POSICAO_LISTA_CLASSIFICATORIA")
    print("=" * 80)
    print()

    # Caminho do CSV
    csv_path = Path(__file__).parent.parent / "Simulador Relotação TJPR - Dados - Página1.csv"

    if not csv_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {csv_path}")
        return

    print(f"[LENDO] {csv_path.name}...")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"   [OK] {len(df)} registros encontrados")
    print(f"   Colunas: {', '.join(df.columns)}")
    print()

    # Adicionar coluna se não existir
    if "posicao_lista_classificatoria" not in df.columns:
        print("[INFO] Adicionando coluna 'posicao_lista_classificatoria'...")
        df["posicao_lista_classificatoria"] = pd.NA
        print("   [OK] Coluna adicionada")
    else:
        print("[INFO] Coluna 'posicao_lista_classificatoria' já existe, será atualizada")
    print()

    # Processar cada registro
    print("[PROCESSANDO] Fazendo matching de nomes e atualizando posições...")
    print()

    atualizados = 0
    nao_encontrados = []
    revisao_manual = []

    for idx, row in df.iterrows():
        nome = row.get("nome", "").strip() if pd.notna(row.get("nome")) else ""

        if not nome:
            print(f"   [AVISO] Linha {idx+2}: Nome vazio, pulando")
            continue

        # Buscar posição
        resultado = buscar_posicao_por_nome(nome)

        if resultado:
            posicao, score, nome_lista = resultado

            # Atualizar DataFrame
            df.at[idx, "posicao_lista_classificatoria"] = posicao

            if score >= 95:  # Match excelente
                atualizados += 1
                print(f"   [OK] Linha {idx+2:3d} | Pos {posicao:4d} | {score}% | {nome}")
                if nome.upper() != nome_lista.upper():
                    print(f"             → Lista: {nome_lista}")

            else:  # Match bom mas requer revisão (85-94%)
                atualizados += 1
                revisao_manual.append({
                    "linha": idx + 2,
                    "nome_inscricao": nome,
                    "posicao": posicao,
                    "score": score,
                    "nome_lista": nome_lista
                })
                print(f"   [ATENÇÃO] Linha {idx+2:3d} | Pos {posicao:4d} | {score}% | {nome}")
                print(f"             → Lista: {nome_lista}")

        else:
            nao_encontrados.append({
                "linha": idx + 2,
                "nome_inscricao": nome
            })
            print(f"   [NÃO ENCONTRADO] Linha {idx+2}: {nome}")

    print()

    # Salvar CSV atualizado
    output_path = Path(__file__).parent.parent / "Simulador Relotação TJPR - Dados - Página1 - ATUALIZADO.csv"
    print(f"[SALVANDO] Gerando CSV atualizado: {output_path.name}...")
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"   [OK] Arquivo salvo com sucesso!")
    print()

    # Relatório
    print("=" * 80)
    print("RELATÓRIO DE ATUALIZAÇÃO")
    print("=" * 80)
    print(f"Total de registros processados: {len(df)}")
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
    print(f"Arquivo gerado: {output_path.name}")
    print()

    if revisao_manual or nao_encontrados:
        print("PRÓXIMOS PASSOS:")
        print("1. Revisar os casos marcados para 'REVISÃO MANUAL' ou 'NÃO ENCONTRADOS'")
        print("2. Ajustar manualmente as posições no CSV se necessário")
        print("3. Importar o CSV atualizado para o Google Sheets:")
        print("   - Abrir Google Sheets")
        print("   - File → Import → Upload")
        print("   - Selecionar 'Replace spreadsheet'")
        print("   - Verificar que todas as colunas foram importadas corretamente")
    else:
        print("PRÓXIMOS PASSOS:")
        print("1. Importar o CSV atualizado para o Google Sheets:")
        print("   - Abrir Google Sheets")
        print("   - File → Import → Upload")
        print("   - Selecionar 'Replace spreadsheet'")
        print("   - Verificar que todas as colunas foram importadas corretamente")


if __name__ == "__main__":
    main()
