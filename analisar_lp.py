import pandas as pd

df = pd.read_excel('planilhas/Tabela de Lotação de Pessoal das Unidades - BI.xlsx')

print('Todas as colunas da planilha:')
for col in df.columns:
    print(f'  - {col}')

print('\n' + '='*80)
print('Exemplo: ALMIRANTE TAMANDARÉ - Primeiras 5 linhas')
print('='*80)
exemplo = df[df['Comarca'] == 'ALMIRANTE TAMANDARÉ'].head(5)
print(exemplo[['Comarca', 'Unidade Judicial', 'Grupo', 'LR_Efet', 'LP Sec', 'LP Unid Jud']].to_string())

print('\n' + '='*80)
print('Valores únicos de LP Sec e LP Unid Jud para a mesma unidade:')
print('='*80)
unidade_exemplo = df[(df['Comarca'] == 'ALMIRANTE TAMANDARÉ') &
                      (df['Unidade Judicial'].str.contains('1ª Vara Criminal', na=False))]
print(unidade_exemplo[['Comarca', 'Unidade Judicial', 'Grupo', 'LR_Efet', 'LP Sec', 'LP Unid Jud']].to_string())
