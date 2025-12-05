import tabula

print('Extraindo todas as tabelas do PDF...')
dfs = tabula.read_pdf('planilhas/anexo-i-quadros-tjpr.pdf', pages='all', multiple_tables=True)

print(f'Total de tabelas: {len(dfs)}\n')

print('Buscando tabelas com colunas relevantes (bal, tecn, gab, efet)...\n')

tabelas_encontradas = 0
for i, df in enumerate(dfs):
    colunas_str = ' '.join([str(col).lower() for col in df.columns])

    if any(palavra in colunas_str for palavra in ['bal', 'tecn', 'gab', 'efet', 'direito']):
        tabelas_encontradas += 1
        print('=' * 80)
        print(f'TABELA {i+1} ENCONTRADA')
        print('=' * 80)
        print('Colunas:', df.columns.tolist())
        print('\nPrimeiras 10 linhas:')
        print(df.head(10).to_string())
        print('\n')

if tabelas_encontradas == 0:
    print('Nenhuma tabela com as colunas esperadas foi encontrada.')
    print('\nMostrando todas as colunas de todas as tabelas para análise:')
    for i, df in enumerate(dfs):
        print(f'\nTabela {i+1}: {df.columns.tolist()}')
