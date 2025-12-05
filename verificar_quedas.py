import pandas as pd

df = pd.read_excel('planilhas/Tabela de Lotação de Pessoal das Unidades - BI.xlsx')

print('='*80)
print('QUEDAS DO IGUAÇU - Verificação da fórmula')
print('='*80)

quedas = df[df['Comarca'] == 'QUEDAS DO IGUAÇU']

print('\nTodas as linhas de Quedas do Iguaçu:')
print(quedas[['Comarca', 'Unidade Judicial', 'Grupo', 'Gab Efet', 'LP Sec', 'LP Unid Jud', 'LR_Efet']].to_string())

print('\n' + '='*80)
print('TESTE DA FÓRMULA: lotacao_paradigma = LP Sec + Gab Efet')
print('='*80)

# Agrupar por unidade
for unidade in quedas['Unidade Judicial'].unique():
    dados_unidade = quedas[quedas['Unidade Judicial'] == unidade]

    # Pegar valores (usando max porque geralmente é o mesmo)
    gab_efet = dados_unidade['Gab Efet'].max()
    lp_sec = dados_unidade['LP Sec'].max()
    lp_unid_jud = dados_unidade['LP Unid Jud'].max()
    lr_efet_total = dados_unidade['LR_Efet'].replace('-', 0).apply(lambda x: int(x) if x != '-' else 0).sum()

    # Calcular paradigma
    paradigma_calculado = lp_sec + gab_efet

    print(f'\n{unidade}:')
    print(f'  Gab Efet: {gab_efet}')
    print(f'  LP Sec: {lp_sec}')
    print(f'  LP Sec + Gab Efet = {paradigma_calculado}')
    print(f'  LP Unid Jud (da planilha): {lp_unid_jud}')
    print(f'  LR_Efet (total): {lr_efet_total}')

    if paradigma_calculado == 4:
        print(f'  ✓ Fórmula CORRETA! (esperado 4, calculado {paradigma_calculado})')
    else:
        print(f'  ✗ Fórmula INCORRETA (esperado 4, calculado {paradigma_calculado})')
