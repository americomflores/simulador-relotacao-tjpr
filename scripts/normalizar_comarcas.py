"""
Script para normalizar comarcas em lotacao_data.py
Converte todas as comarcas para Title Case consistente.
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import shutil

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lotacao_data import LOTACAO_POR_CODIGO

def normalizar_comarca(comarca):
    """
    Normaliza nome da comarca para Title Case.

    Regras especiais:
    - "do", "da", "de", "dos", "das" em minúsculo (exceto no início)
    - Preservar "SÃO" e "SANTO"
    """
    # Converter para title case
    nome = comarca.title()

    # Corrigir preposições
    palavras = nome.split()
    resultado = [palavras[0]]  # Primeira palavra sempre capitalizada

    for palavra in palavras[1:]:
        if palavra.lower() in ['Do', 'Da', 'De', 'Dos', 'Das', 'E']:
            resultado.append(palavra.lower())
        else:
            resultado.append(palavra)

    return ' '.join(resultado)

def main():
    print("=" * 80)
    print("NORMALIZAÇÃO DE COMARCAS")
    print("=" * 80)

    # Identificar comarcas duplicadas
    comarcas_dict = {}
    for codigo, dados in LOTACAO_POR_CODIGO.items():
        comarca_upper = dados['comarca'].upper()
        comarcas_dict.setdefault(comarca_upper, []).append(dados['comarca'])

    duplicadas = {k: list(set(v)) for k, v in comarcas_dict.items() if len(set(v)) > 1}

    print(f"\nComarcas com case duplicado: {len(duplicadas)}")
    if duplicadas:
        for comarca_upper, variantes in sorted(duplicadas.items()):
            print(f"  {comarca_upper}: {variante}" for variante in variantes)

    # Normalizar todas as comarcas
    print("\nNormalizando comarcas para Title Case...")

    novos_dados = {}
    mudancas = 0

    for codigo, dados in LOTACAO_POR_CODIGO.items():
        comarca_original = dados['comarca']
        comarca_normalizada = normalizar_comarca(comarca_original)

        if comarca_original != comarca_normalizada:
            mudancas += 1
            print(f"  {codigo}: '{comarca_original}' -> '{comarca_normalizada}'")

        novos_dados[codigo] = {
            'comarca': comarca_normalizada,
            'unidade': dados['unidade'],
            'lotacao_real': dados['lotacao_real'],
            'lotacao_paradigma': dados['lotacao_paradigma'],
            'diferenca': dados['diferenca'],
            'status': dados['status']
        }

    print(f"\nTotal de mudanças: {mudancas}")

    # Gerar LOTACAO_COMPLETA
    lotacao_completa = [
        {
            'comarca': dados['comarca'],
            'unidade': dados['unidade'],
            'lotacao_real': dados['lotacao_real'],
            'lotacao_paradigma': dados['lotacao_paradigma'],
            'diferenca': dados['diferenca'],
            'status': dados['status']
        }
        for dados in novos_dados.values()
    ]

    # Criar backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    arquivo_backup = f"backups/lotacao_data_backup_comarcas_{timestamp}.py"
    shutil.copy2("lotacao_data.py", arquivo_backup)
    print(f"\n[OK] Backup criado: {arquivo_backup}")

    # Gerar novo arquivo
    linhas = []
    linhas.append('"""')
    linhas.append('Dados de Lotação Paradigma - TJPR')
    linhas.append(f'Atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    linhas.append('Comarcas normalizadas para Title Case')
    linhas.append('"""')
    linhas.append('')
    linhas.append('# Mapeamento: Código Anexo II -> Dados de Lotação')
    linhas.append('LOTACAO_POR_CODIGO = {')

    for codigo in sorted(novos_dados.keys()):
        dados = novos_dados[codigo]
        linhas.append(f'    "{codigo}": {{')
        linhas.append(f'        "comarca": "{dados["comarca"]}",')
        linhas.append(f'        "unidade": "{dados["unidade"]}",')
        linhas.append(f'        "lotacao_real": {dados["lotacao_real"]},')
        linhas.append(f'        "lotacao_paradigma": {dados["lotacao_paradigma"]},')
        linhas.append(f'        "diferenca": {dados["diferenca"]},')
        linhas.append(f'        "status": "{dados["status"]}",')
        linhas.append('    },')

    linhas.append('}')
    linhas.append('')
    linhas.append('# Lista completa de lotações (espelhada de LOTACAO_POR_CODIGO)')
    linhas.append('LOTACAO_COMPLETA = [')

    for entrada in lotacao_completa:
        linhas.append('    {')
        linhas.append(f'        "comarca": "{entrada["comarca"]}",')
        linhas.append(f'        "unidade": "{entrada["unidade"]}",')
        linhas.append(f'        "lotacao_real": {entrada["lotacao_real"]},')
        linhas.append(f'        "lotacao_paradigma": {entrada["lotacao_paradigma"]},')
        linhas.append(f'        "diferenca": {entrada["diferenca"]},')
        linhas.append(f'        "status": "{entrada["status"]}",')
        linhas.append('    },')

    linhas.append(']')

    # Escrever arquivo
    with open("lotacao_data.py", 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))

    print(f"[OK] Arquivo atualizado: lotacao_data.py")
    print("\n" + "=" * 80)
    print("NORMALIZAÇÃO CONCLUÍDA!")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    sys.exit(main())
