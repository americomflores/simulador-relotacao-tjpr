import tabula

dfs = tabula.read_pdf('planilhas/anexo-i-quadros-tjpr.pdf', pages='all', multiple_tables=True)

# Examinar tabela 3 (índice 2) com mais detalhes
df = dfs[2]

print('='*80)
print('ESTRUTURA ORIGINAL DA TABELA 3')
print('='*80)
print('\nColunas:', df.columns.tolist())
print(f'\nTotal de linhas: {len(df)}')

print('\nPrimeiras 25 linhas RAW (sem processamento):')
print(df.head(25).to_string())

print('\n' + '='*80)
print('Análise:')
print('  - Coluna "Unnamed: 0" parece ser a COMARCA')
print('  - Coluna "COMARCA" parece ser a UNIDADE JUDICIÁRIA')
print('  - Coluna "UNIDADE JUDICIÁRIA" parece ser o REGIME')
print('='*80)
