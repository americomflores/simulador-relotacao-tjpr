from lotacao_data import LOTACAO_POR_CODIGO

zeradas = [codigo for codigo, dados in LOTACAO_POR_CODIGO.items() if dados['lotacao_paradigma'] == 0]

print(f'Total de lotacoes_paradigma zeradas: {len(zeradas)}')
print(f'\nCodigos com lotacao_paradigma = 0:')
for codigo in zeradas:
    print(f'  {codigo}: {LOTACAO_POR_CODIGO[codigo]["comarca"]} - {LOTACAO_POR_CODIGO[codigo]["unidade"][:60]}')
