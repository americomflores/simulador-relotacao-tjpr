"""Script para debugar extração de PDF"""
import pdfplumber
from pathlib import Path

pdf_path = Path(__file__).parent.parent / "lista" / "Lista Classificatória de Relotação_Edital nº 04.2025_Técnicos deficitárias-1.pdf"

print(f"Abrindo: {pdf_path.name}")
print()

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total de páginas: {len(pdf.pages)}")
    print()

    # Analisar primeira página
    primeira_pagina = pdf.pages[0]
    print("=" * 80)
    print("PÁGINA 1 - TEXTO:")
    print("=" * 80)
    texto = primeira_pagina.extract_text()
    print(texto[:1000])  # Primeiros 1000 caracteres
    print()

    print("=" * 80)
    print("PÁGINA 1 - TABELAS:")
    print("=" * 80)
    tabelas = primeira_pagina.extract_tables()
    print(f"Número de tabelas encontradas: {len(tabelas)}")
    print()

    if tabelas:
        print("Primeira tabela:")
        print(f"Número de linhas: {len(tabelas[0])}")
        print(f"Número de colunas: {len(tabelas[0][0]) if tabelas[0] else 0}")
        print()

        print("Primeiras 5 linhas da primeira tabela:")
        for i, linha in enumerate(tabelas[0][:5]):
            print(f"Linha {i}: {linha}")
        print()

    # Analisar segunda página (pode ter dados diferentes)
    if len(pdf.pages) > 1:
        segunda_pagina = pdf.pages[1]
        print("=" * 80)
        print("PÁGINA 2 - TABELAS:")
        print("=" * 80)
        tabelas = segunda_pagina.extract_tables()
        print(f"Número de tabelas encontradas: {len(tabelas)}")
        print()

        if tabelas:
            print("Primeira tabela:")
            print(f"Número de linhas: {len(tabelas[0])}")
            print(f"Número de colunas: {len(tabelas[0][0]) if tabelas[0] else 0}")
            print()

            print("Primeiras 5 linhas da primeira tabela:")
            for i, linha in enumerate(tabelas[0][:5]):
                print(f"Linha {i}: {linha}")
