"""
Script para migrar inscrições existentes para o novo sistema baseado em lista classificatória

Lê o CSV com dados atuais (147 servidores)
Faz fuzzy matching com lista_classificatoria.py
Gera relatório de migração e telefone_posicao_map.py
"""

import pandas as pd
import sys
from pathlib import Path
from fuzzywuzzy import fuzz
from typing import Dict, List, Tuple, Optional

# Adicionar pasta parent ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lista_classificatoria import LISTA_CLASSIFICATORIA


def buscar_posicao_por_nome(nome_inscricao: str, threshold: int = 85) -> Optional[Tuple[int, int, str]]:
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


def extrair_telefone(registro: pd.Series) -> Optional[str]:
    """
    Extrai telefone de um registro de inscrição.
    Tenta registrado_por e alterado_por.
    """
    # Tentar registrado_por primeiro
    if pd.notna(registro.get("registrado_por")):
        tel = str(registro["registrado_por"]).strip()
        # Remover formatação se houver
        tel = tel.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        if tel.isdigit() and len(tel) == 11:
            return tel

    # Tentar alterado_por
    if pd.notna(registro.get("alterado_por")):
        tel = str(registro["alterado_por"]).strip()
        tel = tel.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        if tel.isdigit() and len(tel) == 11:
            return tel

    return None


def main():
    """Função principal"""
    # Configure encoding for Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("MIGRAÇÃO DE INSCRIÇÕES EXISTENTES")
    print("=" * 80)
    print()

    # Ler CSV com dados existentes
    csv_path = Path(__file__).parent.parent / "Simulador Relotação TJPR - Dados - Página1.csv"

    if not csv_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {csv_path}")
        return

    print(f"[LENDO] {csv_path.name}...")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"   [OK] {len(df)} registros encontrados")
    print()

    # Estatísticas
    migrados_auto = []
    requer_revisao = []
    nao_encontrados = []
    sem_telefone = []
    telefone_posicao = {}

    # Processar cada registro
    print("[PROCESSANDO] Fazendo matching de nomes...")
    print()

    for idx, row in df.iterrows():
        nome = row.get("nome", "").strip() if pd.notna(row.get("nome")) else ""

        if not nome:
            print(f"   [AVISO] Registro {idx+1}: Nome vazio, pulando")
            continue

        # Buscar posição
        resultado = buscar_posicao_por_nome(nome)

        # Extrair telefone
        telefone = extrair_telefone(row)

        if resultado:
            posicao, score, nome_lista = resultado

            if score >= 95:  # Match excelente (>=95%)
                migrados_auto.append({
                    "nome_inscricao": nome,
                    "posicao": posicao,
                    "score": score,
                    "nome_lista": nome_lista,
                    "telefone": telefone,
                    "registro_original": row.to_dict()
                })

                # Adicionar ao mapeamento telefone → posição
                if telefone:
                    if telefone in telefone_posicao:
                        print(f"   [ATENÇÃO] Telefone {telefone} duplicado!")
                        print(f"      Posição anterior: {telefone_posicao[telefone]}")
                        print(f"      Nova posição: {posicao}")
                    telefone_posicao[telefone] = posicao

            else:  # Match bom mas requer revisão (85-94%)
                requer_revisao.append({
                    "nome_inscricao": nome,
                    "posicao": posicao,
                    "score": score,
                    "nome_lista": nome_lista,
                    "telefone": telefone,
                    "registro_original": row.to_dict()
                })
        else:
            nao_encontrados.append({
                "nome_inscricao": nome,
                "telefone": telefone,
                "registro_original": row.to_dict()
            })

        if not telefone:
            sem_telefone.append({
                "nome_inscricao": nome,
                "posicao": resultado[0] if resultado else None,
                "score": resultado[1] if resultado else None
            })

    # Relatório
    print("=" * 80)
    print("RELATÓRIO DE MIGRAÇÃO")
    print("=" * 80)
    print(f"Total de registros processados: {len(df)}")
    print(f"Migrados automaticamente (≥95%): {len(migrados_auto)} ({len(migrados_auto)/len(df)*100:.1f}%)")
    print(f"Requer revisão manual (85-94%): {len(requer_revisao)} ({len(requer_revisao)/len(df)*100:.1f}%)")
    print(f"Não encontrados (<85%): {len(nao_encontrados)} ({len(nao_encontrados)/len(df)*100:.1f}%)")
    print(f"Sem telefone cadastrado: {len(sem_telefone)}")
    print()

    # Detalhes de migrados
    if migrados_auto:
        print("[OK] MIGRADOS AUTOMATICAMENTE:")
        print()
        for item in migrados_auto[:10]:  # Mostrar primeiros 10
            print(f"   Pos {item['posicao']:4d} | Score: {item['score']}% | {item['nome_inscricao']}")
            if item['nome_inscricao'].upper() != item['nome_lista'].upper():
                print(f"            → Lista: {item['nome_lista']}")
        if len(migrados_auto) > 10:
            print(f"   ... e mais {len(migrados_auto) - 10} registros")
        print()

    # Requer revisão
    if requer_revisao:
        print("[ATENÇÃO] REQUER REVISÃO MANUAL (85-94% similaridade):")
        print()
        for item in requer_revisao:
            print(f"   Score: {item['score']}% | '{item['nome_inscricao']}'")
            print(f"            → Sugestão: Pos {item['posicao']} - '{item['nome_lista']}'")
            print()

    # Não encontrados
    if nao_encontrados:
        print("[ERRO] NÃO ENCONTRADOS NA LISTA (<85% similaridade):")
        print()
        for item in nao_encontrados:
            print(f"   '{item['nome_inscricao']}'")
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

    # Sem telefone
    if sem_telefone:
        print("[AVISO] SEM TELEFONE CADASTRADO:")
        print()
        for item in sem_telefone[:10]:
            print(f"   {item['nome_inscricao']}")
        if len(sem_telefone) > 10:
            print(f"   ... e mais {len(sem_telefone) - 10} registros")
        print()

    # Gerar telefone_posicao_map.py
    output_path = Path(__file__).parent.parent / "config" / "telefone_posicao_map.py"

    print(f"[SALVANDO] Gerando {output_path.name}...")

    codigo = '''"""
Mapeamento Telefone → Posição na Lista Classificatória
Auto-gerado a partir de "Simulador Relotação TJPR - Dados - Página1.csv"

Total de mapeamentos: {total}
"""

TELEFONE_POSICAO_MAP = {{
'''.format(total=len(telefone_posicao))

    for telefone, posicao in sorted(telefone_posicao.items(), key=lambda x: x[1]):
        # Adicionar comentário com nome do servidor
        nome_servidor = LISTA_CLASSIFICATORIA[posicao]["nome_display"]
        codigo += f'    "{telefone}": {posicao},  # {nome_servidor}\n'

    codigo += "}\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(codigo)

    print(f"   [OK] Arquivo gerado com {len(telefone_posicao)} mapeamentos")
    print()

    # Resumo final
    print("=" * 80)
    print("[CONCLUÍDO] MIGRAÇÃO FINALIZADA")
    print("=" * 80)
    print(f"Arquivo gerado: config/telefone_posicao_map.py")
    print()

    if requer_revisao or nao_encontrados:
        print("⚠️  ATENÇÃO: Há registros que precisam de revisão manual!")
        print()
        print("Próximos passos:")
        print("1. Revisar os casos marcados para 'REVISÃO MANUAL'")
        print("2. Revisar os casos 'NÃO ENCONTRADOS'")
        print("3. Atualizar manualmente o telefone_posicao_map.py se necessário")
        print("4. Prosseguir com atualização do código do sistema")
    else:
        print("✓ Todos os registros foram migrados com sucesso!")
        print()
        print("Próximos passos:")
        print("1. Atualizar services/sheets_service.py")
        print("2. Atualizar services/simulacao_service.py")
        print("3. Atualizar config/auth_config.py")
        print("4. Atualizar app.py")


if __name__ == "__main__":
    main()
