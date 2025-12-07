"""
Script para normalizar nomes na lista classificatória.

Converte nomes de MAIÚSCULAS para Title Case com preposições em minúscula.
Exemplo: "AMANDA DOS SANTOS" → "Amanda dos Santos"
"""

import sys
from pathlib import Path

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Adicionar pasta parent ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lista_classificatoria import LISTA_CLASSIFICATORIA
from utils.normalizers import normalizar_nome_pessoa


def main():
    """Normaliza todos os nomes na lista classificatória"""
    print("=" * 80)
    print("NORMALIZAÇÃO DE NOMES - LISTA CLASSIFICATÓRIA")
    print("=" * 80)
    print()

    print(f"Total de servidores: {len(LISTA_CLASSIFICATORIA)}")
    print()

    # Contar quantos precisam ser normalizados
    precisa_normalizar = 0
    for posicao, dados in LISTA_CLASSIFICATORIA.items():
        nome_original = dados['nome']
        nome_normalizado = normalizar_nome_pessoa(nome_original)
        if nome_original != nome_normalizado:
            precisa_normalizar += 1

    print(f"Servidores que precisam normalização: {precisa_normalizar}")
    print()

    # Mostrar exemplos antes/depois
    print("EXEMPLOS (antes → depois):")
    print("-" * 80)
    exemplos_mostrados = 0
    for posicao, dados in LISTA_CLASSIFICATORIA.items():
        nome_original = dados['nome']
        nome_normalizado = normalizar_nome_pessoa(nome_original)
        if nome_original != nome_normalizado and exemplos_mostrados < 10:
            print(f"Pos {posicao:4d}: {nome_original}")
            print(f"          → {nome_normalizado}")
            print()
            exemplos_mostrados += 1
            if exemplos_mostrados >= 10:
                break
    print()

    # Confirmar
    resposta = input("Deseja aplicar a normalização? (s/n): ").strip().lower()
    if resposta != 's':
        print("Operação cancelada.")
        return

    print()
    print("Normalizando nomes...")
    print()

    # Aplicar normalização
    for posicao, dados in LISTA_CLASSIFICATORIA.items():
        # Normalizar nome principal
        dados['nome'] = normalizar_nome_pessoa(dados['nome'])

        # Normalizar nome_original se existir
        if 'nome_original' in dados:
            dados['nome_original'] = normalizar_nome_pessoa(dados['nome_original'])

        # Normalizar nome_display se existir
        if 'nome_display' in dados:
            dados['nome_display'] = normalizar_nome_pessoa(dados['nome_display'])

    # Gerar novo arquivo
    output_file = Path(__file__).parent.parent / "lista_classificatoria.py"

    print(f"Gerando arquivo atualizado: {output_file.name}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('Lista Classificatória do Edital nº 04/2025 - Técnico Judiciário\n')
        f.write('Extraído dos 7 PDFs oficiais do TJPR\n')
        f.write(f'Total: {len(LISTA_CLASSIFICATORIA)} servidores (posições 1 a {len(LISTA_CLASSIFICATORIA)})\n')
        f.write('NOMES NORMALIZADOS: Title Case com preposições em minúscula\n')
        f.write('"""\n\n')
        f.write('LISTA_CLASSIFICATORIA = {\n')

        for posicao in sorted(LISTA_CLASSIFICATORIA.keys()):
            dados = LISTA_CLASSIFICATORIA[posicao]
            f.write(f'    {posicao}: {{\n')
            f.write(f'        "nome": "{dados["nome"]}",\n')
            f.write(f'        "nome_original": "{dados["nome_original"]}",\n')
            f.write(f'        "nome_display": "{dados["nome_display"]}",\n')
            f.write(f'        "inicio_cargo": "{dados["inicio_cargo"]}",\n')
            f.write(f'        "tempo_cargo": "{dados["tempo_cargo"]}",\n')
            f.write(f'        "tempo_poder_judiciario": "{dados["tempo_poder_judiciario"]}",\n')
            f.write(f'        "tempo_servico_publico": "{dados["tempo_servico_publico"]}",\n')
            f.write(f'        "data_nascimento": "{dados["data_nascimento"]}",\n')
            f.write(f'        "lotacao": "{dados["lotacao"]}",\n')
            f.write(f'        "localizacao_principal": "{dados["localizacao_principal"]}"\n')
            f.write(f'    }},\n')

        f.write('}\n')

    print(f"✅ Arquivo atualizado com sucesso!")
    print()
    print("=" * 80)
    print("RESUMO")
    print("=" * 80)
    print(f"Total de servidores: {len(LISTA_CLASSIFICATORIA)}")
    print(f"Nomes normalizados: {precisa_normalizar}")
    print(f"Arquivo gerado: {output_file.name}")
    print()
    print("✅ NORMALIZAÇÃO CONCLUÍDA!")
    print()


if __name__ == "__main__":
    main()
