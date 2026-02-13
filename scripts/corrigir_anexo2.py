"""
Script para corrigir ANEXO_II: remover entradas inválidas, normalizar nomes e deduplicar.
"""
import re
import sys
sys.path.insert(0, r'C:\Users\ameri\Desktop\cursor\relotacao\simulador-relotacao-tjpr')

from data import ANEXO_II

# Correções manuais de comarcas conhecidas com problemas
CORRECOES_COMARCA = {
    "1 baiti": None,  # Remover - entrada inválida
    "1 rati": None,   # Remover - entrada inválida
    "Assis Chatea ubria nd": "Assis Chateaubriand",
    "Canta galo": "Cantagalo",
}

def normalizar_comarca(nome):
    """Normaliza nome de comarca para Title Case consistente."""
    # Primeiro aplica correções conhecidas
    if nome in CORRECOES_COMARCA:
        return CORRECOES_COMARCA[nome]

    # Palavras que devem ficar em minúsculo (preposições, artigos)
    minusculas = {'de', 'do', 'da', 'dos', 'das', 'e'}

    # Divide em palavras e processa
    palavras = nome.split()
    resultado = []
    for i, palavra in enumerate(palavras):
        # Primeira palavra sempre capitalizada, demais seguem regra
        if i == 0:
            resultado.append(palavra.capitalize())
        elif palavra.lower() in minusculas:
            resultado.append(palavra.lower())
        else:
            resultado.append(palavra.capitalize())

    return ' '.join(resultado)

def main():
    print(f"ANEXO_II original tem {len(ANEXO_II)} entradas")

    # Coletar entradas válidas com nomes normalizados
    entradas_validas = []
    removidas = 0

    for codigo, info in ANEXO_II.items():
        comarca_orig = info['comarca']
        comarca_corrigida = normalizar_comarca(comarca_orig)

        if comarca_corrigida is None:
            print(f"  REMOVENDO: {codigo} - {comarca_orig}")
            removidas += 1
            continue

        unidade = info['unidade'].strip()
        entradas_validas.append((comarca_corrigida, unidade))

    print(f"\nRemovidas {removidas} entradas inválidas")
    print(f"Entradas válidas: {len(entradas_validas)}")

    # Remover duplicatas (mesma comarca + unidade)
    unicas = list(set(entradas_validas))
    duplicatas = len(entradas_validas) - len(unicas)
    print(f"Duplicatas encontradas: {duplicatas}")
    print(f"Entradas únicas: {len(unicas)}")

    # Ordenar: primeiro por comarca, depois por unidade
    unicas.sort(key=lambda x: (x[0].lower(), x[1].lower()))

    # Gerar novo ANEXO_II
    linhas = []
    linhas.append('ANEXO_II = {')
    for i, (comarca, unidade) in enumerate(unicas, 1):
        codigo = f"A2-{i:03d}"
        # Escapar aspas nas strings
        comarca_escaped = comarca.replace('"', '\\"')
        unidade_escaped = unidade.replace('"', '\\"')
        linhas.append(f'    "{codigo}": {{"comarca": "{comarca_escaped}", "unidade": "{unidade_escaped}"}},')
    linhas.append('}')

    novo_anexo2 = '\n'.join(linhas)

    # Ler data.py original
    with open(r'C:\Users\ameri\Desktop\cursor\relotacao\simulador-relotacao-tjpr\data.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontrar e substituir ANEXO_II
    padrao = r'ANEXO_II = \{[^}]+(?:\{[^}]*\}[^}]*)*\}'

    # Usar abordagem mais simples: encontrar início e fim
    inicio = conteudo.find('ANEXO_II = {')
    if inicio == -1:
        print("ERRO: Não encontrou ANEXO_II no arquivo!")
        return

    # Encontrar o fechamento do dicionário
    nivel = 0
    fim = inicio
    for i, c in enumerate(conteudo[inicio:]):
        if c == '{':
            nivel += 1
        elif c == '}':
            nivel -= 1
            if nivel == 0:
                fim = inicio + i + 1
                break

    # Substituir
    novo_conteudo = conteudo[:inicio] + novo_anexo2 + conteudo[fim:]

    # Salvar
    with open(r'C:\Users\ameri\Desktop\cursor\relotacao\simulador-relotacao-tjpr\data.py', 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)

    print(f"\nArquivo data.py atualizado!")
    print(f"ANEXO_II agora tem {len(unicas)} unidades (limpo, normalizado, sem duplicatas)")

    # Também atualizar anexo2_convertido.py
    with open(r'C:\Users\ameri\Desktop\cursor\relotacao\simulador-relotacao-tjpr\edital 2026\anexo2_convertido.py', 'w', encoding='utf-8') as f:
        f.write('"""Anexo II do Edital 01/2026 - Convertido e Corrigido"""\n\n')
        f.write(novo_anexo2)
        f.write('\n')

    print("Arquivo anexo2_convertido.py também atualizado!")

if __name__ == "__main__":
    main()
