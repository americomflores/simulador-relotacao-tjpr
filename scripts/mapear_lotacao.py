"""
Script para mapear lotacao_data.py com os códigos corretos de data.py

Estratégia:
1. Ler ANEXO_II de data.py (códigos corretos)
2. Ler LOTACAO_POR_CODIGO de lotacao_data.py (dados de lotação)
3. Mapear por nome normalizado (comarca + unidade)
4. Gerar novo lotacao_data.py com códigos corretos
"""

import sys
import os
import unicodedata
import re
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import ANEXO_II
from lotacao_data import LOTACAO_POR_CODIGO

def normalizar_texto(texto):
    """Normaliza texto para comparação: remove acentos, maiúscula, espaços extras"""
    if not texto:
        return ""
    # Remove acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Maiúscula e remove espaços extras
    texto = texto.upper().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def criar_chave(comarca, unidade):
    """Cria chave única para busca"""
    return f"{normalizar_texto(comarca)}|{normalizar_texto(unidade)}"

def main():
    print("=" * 70)
    print("MAPEAMENTO DE LOTACAO_DATA.PY PARA CÓDIGOS DE DATA.PY")
    print("=" * 70)
    print()

    # 1. Criar mapeamento do lotacao_data.py antigo (por nome)
    print("1. Criando mapeamento do lotacao_data.py antigo...")
    mapeamento_antigo = {}
    for codigo, dados in LOTACAO_POR_CODIGO.items():
        chave = criar_chave(dados['comarca'], dados['unidade'])
        mapeamento_antigo[chave] = {
            'codigo_antigo': codigo,
            'comarca': dados['comarca'],
            'unidade': dados['unidade'],
            'lotacao_real': dados['lotacao_real'],
            'lotacao_paradigma': dados['lotacao_paradigma'],
            'diferenca': dados['diferenca'],
            'status': dados['status']
        }
    print(f"   - {len(mapeamento_antigo)} unidades no lotacao_data.py antigo")
    print()

    # 2. Criar novo mapeamento baseado em data.py
    print("2. Mapeando para códigos de data.py (ANEXO_II)...")
    novo_mapeamento = {}
    mapeados = []
    nao_mapeados = []

    for codigo_novo, dados_novo in ANEXO_II.items():
        chave = criar_chave(dados_novo['comarca'], dados_novo['unidade'])

        if chave in mapeamento_antigo:
            # Encontrou correspondência - preservar dados de lotação
            dados_antigo = mapeamento_antigo[chave]
            novo_mapeamento[codigo_novo] = {
                'comarca': dados_novo['comarca'],  # Usar nome do data.py
                'unidade': dados_novo['unidade'],  # Usar nome do data.py
                'lotacao_real': dados_antigo['lotacao_real'],
                'lotacao_paradigma': dados_antigo['lotacao_paradigma'],
                'diferenca': dados_antigo['diferenca'],
                'status': dados_antigo['status']
            }
            mapeados.append({
                'codigo_novo': codigo_novo,
                'codigo_antigo': dados_antigo['codigo_antigo'],
                'comarca': dados_novo['comarca'],
                'unidade': dados_novo['unidade']
            })
        else:
            # Não encontrou - usar valores padrão
            novo_mapeamento[codigo_novo] = {
                'comarca': dados_novo['comarca'],
                'unidade': dados_novo['unidade'],
                'lotacao_real': 5,
                'lotacao_paradigma': 5,
                'diferenca': 0,
                'status': 'EQUILIBRADA'
            }
            nao_mapeados.append({
                'codigo_novo': codigo_novo,
                'comarca': dados_novo['comarca'],
                'unidade': dados_novo['unidade']
            })

    print(f"   - {len(ANEXO_II)} unidades no data.py (ANEXO_II)")
    print(f"   - {len(mapeados)} unidades MAPEADAS com sucesso")
    print(f"   - {len(nao_mapeados)} unidades NÃO MAPEADAS (usarão padrão 5/5)")
    print()

    # 3. Identificar unidades antigas que não existem mais
    codigos_usados = set(m['codigo_antigo'] for m in mapeados)
    unidades_removidas = [
        {'codigo': cod, 'comarca': dados['comarca'], 'unidade': dados['unidade']}
        for cod, dados in LOTACAO_POR_CODIGO.items()
        if cod not in codigos_usados and criar_chave(dados['comarca'], dados['unidade']) not in [
            criar_chave(d['comarca'], d['unidade']) for d in ANEXO_II.values()
        ]
    ]

    # 4. Gerar relatório detalhado
    print("=" * 70)
    print("RELATÓRIO DE MAPEAMENTO")
    print("=" * 70)
    print()

    if nao_mapeados:
        print(f"### UNIDADES NÃO MAPEADAS ({len(nao_mapeados)}) - Usarão padrão 5/5:")
        print("-" * 70)
        for item in nao_mapeados[:30]:  # Mostrar primeiras 30
            print(f"  {item['codigo_novo']}: {item['comarca']} - {item['unidade'][:50]}...")
        if len(nao_mapeados) > 30:
            print(f"  ... e mais {len(nao_mapeados) - 30} unidades")
        print()

    # 5. Gerar novo arquivo lotacao_data.py
    print("3. Gerando novo arquivo lotacao_data.py...")

    output_lines = []
    output_lines.append('"""')
    output_lines.append('Dados de Lotação Paradigma - TJPR')
    output_lines.append(f'Atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    output_lines.append('Fonte: Mapeamento de data.py (ANEXO_II) com dados de lotação preservados')
    output_lines.append('')
    output_lines.append('Regras de mapeamento:')
    output_lines.append('  - Códigos baseados em data.py (ANEXO_II do Edital 01/2026)')
    output_lines.append('  - Dados de lotação preservados quando unidade encontrada por nome')
    output_lines.append('  - Unidades não encontradas: lotacao_real=5, lotacao_paradigma=5, status=EQUILIBRADA')
    output_lines.append('')
    output_lines.append(f'Estatísticas:')
    output_lines.append(f'  - Total de unidades: {len(novo_mapeamento)}')
    output_lines.append(f'  - Mapeadas com dados preservados: {len(mapeados)}')
    output_lines.append(f'  - Com valores padrão (5/5): {len(nao_mapeados)}')
    output_lines.append('"""')
    output_lines.append('')
    output_lines.append('# Mapeamento: Código Anexo II -> Dados de Lotação')
    output_lines.append('LOTACAO_POR_CODIGO = {')

    for codigo in sorted(novo_mapeamento.keys(), key=lambda x: int(x.split('-')[1])):
        dados = novo_mapeamento[codigo]
        output_lines.append(f'    "{codigo}": {{')
        output_lines.append(f'        "comarca": "{dados["comarca"]}",')
        output_lines.append(f'        "unidade": "{dados["unidade"]}",')
        output_lines.append(f'        "lotacao_real": {dados["lotacao_real"]},')
        output_lines.append(f'        "lotacao_paradigma": {dados["lotacao_paradigma"]},')
        output_lines.append(f'        "diferenca": {dados["diferenca"]},')
        output_lines.append(f'        "status": "{dados["status"]}",')
        output_lines.append('    },')

    output_lines.append('}')
    output_lines.append('')

    # Escrever arquivo
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lotacao_data.py')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"   - Arquivo salvo em: {output_path}")
    print()

    # 6. Resumo final
    print("=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    print(f"  Total de unidades no novo arquivo: {len(novo_mapeamento)}")
    print(f"  Unidades com dados preservados:    {len(mapeados)} ({100*len(mapeados)/len(novo_mapeamento):.1f}%)")
    print(f"  Unidades com valores padrão:       {len(nao_mapeados)} ({100*len(nao_mapeados)/len(novo_mapeamento):.1f}%)")
    print()
    print("CONCLUÍDO!")

    return len(mapeados), len(nao_mapeados)

if __name__ == "__main__":
    main()
