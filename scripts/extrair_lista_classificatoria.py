"""
Script para extrair dados dos 7 PDFs da Lista Classificatória de Relotação
Edital nº 04/2025 - Técnico Judiciário

Gera o arquivo lista_classificatoria.py com todos os servidores consolidados.
"""

import pdfplumber
import re
from pathlib import Path
from typing import Dict, List
from collections import Counter


def extrair_dados_pdf(pdf_path: str) -> List[Dict]:
    """
    Extrai dados de um PDF da lista classificatória.

    Retorna lista de dicionários com:
    - posicao: int
    - nome: str
    - inicio_cargo: str
    - tempo_cargo: str
    - tempo_poder_judiciario: str
    - tempo_servico_publico: str
    - data_nascimento: str
    - lotacao: str
    - localizacao_principal: str
    """
    servidores = []

    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # Extrair tabela da página
            tabelas = pagina.extract_tables()

            for tabela in tabelas:
                # Pular cabeçalhos (2 primeiras linhas)
                for linha in tabela[2:]:
                    # Verificar se tem dados válidos
                    if not linha or len(linha) < 17:
                        continue

                    # Tentar extrair posição (coluna 0)
                    try:
                        posicao_str = linha[0]
                        if not posicao_str or posicao_str.strip() == '':
                            continue
                        posicao = int(posicao_str.strip())
                    except (ValueError, AttributeError):
                        continue

                    # Extrair nome (coluna 3) - remover quebras de linha
                    nome = linha[3].strip().replace('\n', ' ') if linha[3] else ""
                    if not nome:
                        continue

                    # Extrair dados das colunas corretas
                    servidor = {
                        "posicao": posicao,
                        "nome": nome,
                        "inicio_cargo": linha[4].strip() if linha[4] else "",
                        "tempo_cargo": linha[5].strip().replace('\n', ' ') if linha[5] else "",
                        "tempo_poder_judiciario": linha[6].strip().replace('\n', ' ') if linha[6] else "",
                        "tempo_servico_publico": linha[9].strip().replace('\n', ' ') if linha[9] else "",
                        "data_nascimento": linha[12].strip() if linha[12] else "",
                        "lotacao": linha[15].strip().replace('\n', ' ') if linha[15] else "",
                        "localizacao_principal": linha[16].strip().replace('\n', ' ') if linha[16] else "",
                    }

                    servidores.append(servidor)

    return servidores


def adicionar_numeracao_homonimos(lista_servidores: List[Dict]) -> List[Dict]:
    """
    Adiciona numeração a nomes duplicados.

    Exemplo:
    - Posição 50: AMANDA DA SILVA → "AMANDA DA SILVA 1"
    - Posição 120: AMANDA DA SILVA → "AMANDA DA SILVA 2"
    """
    # Ordenar por posição para garantir numeração correta
    lista_servidores = sorted(lista_servidores, key=lambda x: x["posicao"])

    # Contar ocorrências de cada nome
    contador_nomes = Counter(s["nome"] for s in lista_servidores)

    # Identificar nomes duplicados
    nomes_duplicados = {nome for nome, count in contador_nomes.items() if count > 1}

    # Adicionar numeração aos duplicados
    contador_ocorrencias = {}

    for servidor in lista_servidores:
        nome_original = servidor["nome"]

        if nome_original in nomes_duplicados:
            # Incrementar contador para este nome
            contador_ocorrencias[nome_original] = contador_ocorrencias.get(nome_original, 0) + 1
            servidor["nome_display"] = f"{nome_original} {contador_ocorrencias[nome_original]}"
        else:
            servidor["nome_display"] = nome_original

        # Sempre guardar original
        servidor["nome_original"] = nome_original

    return lista_servidores


def gerar_arquivo_python(servidores: List[Dict], output_path: str):
    """
    Gera arquivo lista_classificatoria.py com os dados.
    """
    # Ordenar por posição
    servidores = sorted(servidores, key=lambda x: x["posicao"])

    # Gerar código Python
    codigo = '''"""
Lista Classificatória de Relotação - TÉCNICO JUDICIÁRIO
Edital nº 04/2025

Auto-gerado a partir dos 7 PDFs da lista classificatória.
Total de servidores: {total}
"""

LISTA_CLASSIFICATORIA = {{
'''.format(total=len(servidores))

    for servidor in servidores:
        codigo += f'''    {servidor["posicao"]}: {{
        "nome": "{servidor["nome"]}",
        "nome_original": "{servidor["nome_original"]}",
        "nome_display": "{servidor["nome_display"]}",
        "inicio_cargo": "{servidor["inicio_cargo"]}",
        "tempo_cargo": "{servidor["tempo_cargo"]}",
        "tempo_poder_judiciario": "{servidor["tempo_poder_judiciario"]}",
        "tempo_servico_publico": "{servidor["tempo_servico_publico"]}",
        "data_nascimento": "{servidor["data_nascimento"]}",
        "lotacao": "{servidor["lotacao"]}",
        "localizacao_principal": "{servidor["localizacao_principal"]}",
    }},
'''

    codigo += "}\n"

    # Escrever arquivo
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(codigo)


def main():
    """Função principal"""
    # Configure encoding for Windows
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("EXTRAÇÃO DA LISTA CLASSIFICATÓRIA - EDITAL 04/2025")
    print("=" * 60)
    print()

    # Diretório dos PDFs
    lista_dir = Path(__file__).parent.parent / "lista"

    # Listar PDFs
    pdfs = sorted(lista_dir.glob("Lista Classificatória de Relotação_Edital nº 04.2025_Técnicos deficitárias-*.pdf"))

    if not pdfs:
        print("[X] ERRO: Nenhum PDF encontrado na pasta 'lista/'")
        return

    print(f"[OK] Encontrados {len(pdfs)} PDFs:")
    for pdf in pdfs:
        print(f"   - {pdf.name}")
    print()

    # Extrair dados de todos os PDFs
    todos_servidores = []

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Processando PDF: {pdf_path.name}...")

        servidores_pdf = extrair_dados_pdf(str(pdf_path))
        todos_servidores.extend(servidores_pdf)

        print(f"   [OK] Extraídos {len(servidores_pdf)} servidores")

    print()
    print(f"[TOTAL] Servidores extraídos: {len(todos_servidores)}")
    print()

    # Validações
    print("[VALIDAÇÃO] Validando dados...")

    # Verificar posições sequenciais
    posicoes = sorted([s["posicao"] for s in todos_servidores])
    esperadas = list(range(1, len(todos_servidores) + 1))

    if posicoes == esperadas:
        print(f"   [OK] Posições sequenciais: 1 a {len(todos_servidores)}")
    else:
        print(f"   [ATENÇÃO] Posições não são sequenciais!")
        faltando = set(esperadas) - set(posicoes)
        duplicadas = [p for p in posicoes if posicoes.count(p) > 1]
        if faltando:
            print(f"      Faltando: {sorted(faltando)}")
        if duplicadas:
            print(f"      Duplicadas: {sorted(set(duplicadas))}")

    # Detectar homônimos
    contador_nomes = Counter(s["nome"] for s in todos_servidores)
    homonimos = {nome: count for nome, count in contador_nomes.items() if count > 1}

    if homonimos:
        print(f"   [ATENÇÃO] Encontrados {len(homonimos)} nomes duplicados (homônimos):")
        for nome, count in sorted(homonimos.items()):
            print(f"      - '{nome}': {count} ocorrências")
    else:
        print("   [OK] Nenhum homônimo detectado")

    print()

    # Adicionar numeração a homônimos
    print("[PROCESSAMENTO] Adicionando numeração a homônimos...")
    todos_servidores = adicionar_numeracao_homonimos(todos_servidores)
    print("   [OK] Numeração adicionada")
    print()

    # Gerar arquivo Python
    output_path = Path(__file__).parent.parent / "lista_classificatoria.py"
    print(f"[SALVANDO] Gerando arquivo: {output_path}...")
    gerar_arquivo_python(todos_servidores, str(output_path))
    print("   [OK] Arquivo gerado com sucesso!")
    print()

    # Resumo final
    print("=" * 60)
    print("[CONCLUÍDO] EXTRAÇÃO CONCLUÍDA")
    print("=" * 60)
    print(f"Total de servidores: {len(todos_servidores)}")
    print(f"Homônimos encontrados: {len(homonimos)}")
    print(f"Arquivo gerado: lista_classificatoria.py")
    print()
    print("Próximos passos:")
    print("1. Revisar o arquivo lista_classificatoria.py")
    print("2. Executar migração de inscrições existentes")
    print("3. Gerar mapeamento telefone → posição")


if __name__ == "__main__":
    main()
