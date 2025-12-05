import tabula
import pandas as pd

print('Extraindo tabela 8 para análise detalhada...')
dfs = tabula.read_pdf('planilhas/anexo-i-quadros-tjpr.pdf', pages='all', multiple_tables=True)

# Examinar tabela 8 (índice 7) - ARAPONGAS aparece aí
df = dfs[7]

print('='*80)
print('TABELA 8 - Estrutura completa RAW')
print('='*80)
print(f'Colunas: {df.columns.tolist()}')
print(f'\nTotal de linhas: {len(df)}')
print('\nPrimeiras 25 linhas (linhas 0-24):')
print(df.head(25).to_string())

print('\n' + '='*80)
print('Análise específica - Linhas com ARAPONGAS:')
print('='*80)

# Verificar linhas específicas (depois do header)
for i in range(2, min(25, len(df))):
    row = df.iloc[i]
    print(f'\nLinha {i}:')
    print(f'  Unnamed: 0 = "{row.get("Unnamed: 0", "")}"')
    print(f'  COMARCA = "{row.get("COMARCA", "")}"')
    print(f'  UNIDADE JUDICIÁRIA = "{row.get("UNIDADE JUDICIÁRIA", "")}"')
    print(f'  REGIME = "{row.get("REGIME", "")}"')
