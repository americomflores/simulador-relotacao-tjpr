import tabula
import pandas as pd

print('Extraindo e consolidando todas as tabelas do PDF...\n')

dfs = tabula.read_pdf('planilhas/anexo-i-quadros-tjpr.pdf', pages='all', multiple_tables=True)

# Consolidar todas as tabelas que têm COMARCA e UNIDADE JUDICIÁRIA
dados_consolidados = []

for i, df in enumerate(dfs):
    # Verificar se tem as colunas necessárias (coluna Unnamed: 0 é a COMARCA real)
    if 'Unnamed: 0' not in df.columns or 'COMARCA' not in df.columns:
        continue

    # Remover linhas de cabeçalho (primeiras 2 linhas de cada tabela)
    df_limpo = df.iloc[2:].copy()

    # ANTES de renomear: preencher Unnamed: 0 vazio com comarca anterior
    # Quando Unnamed: 0 está vazio (NaN), significa que é a mesma comarca da linha anterior
    df_limpo['Unnamed: 0'] = df_limpo['Unnamed: 0'].ffill()

    # CORRIGIR o mapeamento das colunas (descoberto pela análise do PDF)
    # Unnamed: 0 → COMARCA (real)
    # COMARCA → UNIDADE JUDICIÁRIA (real)
    # UNIDADE JUDICIÁRIA → REGIME (real)
    df_limpo = df_limpo.rename(columns={
        'Unnamed: 0': 'COMARCA',
        'COMARCA': 'UNIDADE_JUDICIARIA',
        'Unnamed: 1': 'BAL_DIREITO',
        'Unnamed: 2': 'TECNICOS',
        'Unnamed: 3': 'GAB_EFET',
        'Unnamed: 4': 'TOTAL_COMIS'
    })

    # Converter colunas numéricas
    for col in ['BAL_DIREITO', 'TECNICOS', 'GAB_EFET']:
        df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce').fillna(0).astype(int)

    # Calcular lotação paradigma (efetivos apenas)
    df_limpo['LOTACAO_PARADIGMA'] = df_limpo['BAL_DIREITO'] + df_limpo['TECNICOS'] + df_limpo['GAB_EFET']

    # Selecionar apenas as colunas que queremos (evitar duplicatas)
    df_limpo = df_limpo[['COMARCA', 'UNIDADE_JUDICIARIA', 'BAL_DIREITO', 'TECNICOS', 'GAB_EFET', 'LOTACAO_PARADIGMA']].copy()

    # Manter apenas linhas válidas (que têm comarca preenchida)
    df_limpo = df_limpo[df_limpo['COMARCA'].notna()]

    # Limpar comarcas que possam ter ficado como unidades (detecção de erro de extração)
    # Se comarca contém palavras típicas de unidades, provavelmente houve erro
    palavras_unidade = ['vara', 'juízo', 'juizado', 'secretaria', 'central']
    df_limpo = df_limpo[~df_limpo['COMARCA'].str.lower().str.contains('|'.join(palavras_unidade), na=False)]

    # Resetar index para evitar conflitos no concat
    df_limpo = df_limpo.reset_index(drop=True)

    # Adicionar à lista
    dados_consolidados.append(df_limpo)
    print(f'Tabela {i+1}: {len(df_limpo)} unidades extraídas')

# Consolidar tudo em um único DataFrame
df_final = pd.concat(dados_consolidados, ignore_index=True)

# Selecionar apenas colunas relevantes
df_resultado = df_final[['COMARCA', 'UNIDADE_JUDICIARIA', 'BAL_DIREITO', 'TECNICOS', 'GAB_EFET', 'LOTACAO_PARADIGMA']].copy()

# Remover duplicatas
df_resultado = df_resultado.drop_duplicates(subset=['COMARCA', 'UNIDADE_JUDICIARIA'])

print(f'\n{'='*80}')
print(f'CONSOLIDAÇÃO CONCLUÍDA')
print(f'{'='*80}')
print(f'Total de unidades: {len(df_resultado)}')
print(f'\nPrimeiras 10 unidades:')
print(df_resultado.head(10).to_string())

# Salvar em Excel
df_resultado.to_excel('planilhas/lotacao_paradigma_consolidada.xlsx', index=False)
print(f'\nArquivo salvo: planilhas/lotacao_paradigma_consolidada.xlsx')
