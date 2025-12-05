import tabula
import pandas as pd

print('Extraindo tabela 3 (primeira com COMARCA/UNIDADE)...')
dfs = tabula.read_pdf('planilhas/anexo-i-quadros-tjpr.pdf', pages='all', multiple_tables=True)

# Examinar tabela 3 (índice 2)
df = dfs[2]

print('='*80)
print('TABELA 3 - Estrutura completa')
print('='*80)
print(f'Colunas: {df.columns.tolist()}')
print(f'\nTotal de linhas: {len(df)}')
print('\nPrimeiras 20 linhas:')
print(df.head(20).to_string())

print('\n' + '='*80)
print('Valores únicos da coluna REGIME:')
print(df['REGIME'].unique()[:20])
