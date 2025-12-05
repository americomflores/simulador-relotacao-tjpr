import pandas as pd
from difflib import SequenceMatcher
from data import ANEXO_II

# Constantes
FUZZY_THRESHOLD = 0.95

def normalizar_nome(nome):
    """Normaliza nome para matching"""
    import re
    if pd.isna(nome):
        return ""
    nome = str(nome).upper().strip()
    # Remover quebras de linha e carriage returns
    nome = nome.replace('\r', ' ').replace('\n', ' ')
    # Normalizar espaços múltiplos
    nome = ' '.join(nome.split())
    # Remover acentos comuns que podem diferir
    nome = nome.replace('Á', 'A').replace('Â', 'A').replace('Ã', 'A')
    nome = nome.replace('É', 'E').replace('Ê', 'E')
    nome = nome.replace('Í', 'I').replace('Î', 'I')
    nome = nome.replace('Ó', 'O').replace('Ô', 'O').replace('Õ', 'O')
    nome = nome.replace('Ú', 'U').replace('Û', 'U')
    nome = nome.replace('Ç', 'C')
    # Normalizar ordinais preservando o número: 1a/1ª/1º/1o → 1 VARA (adiciona espaço para manter estrutura)
    nome = re.sub(r'(\d+)[AªOº°]', r'\1 ', nome)
    # Normalizar espaços múltiplos novamente (pode ter criado espaços duplos)
    nome = ' '.join(nome.split())
    return nome

def criar_indice_anexo2():
    """Cria índice normalizado do ANEXO_II"""
    indice = {}
    for codigo, info in ANEXO_II.items():
        comarca_norm = normalizar_nome(info['comarca'])
        unidade_norm = normalizar_nome(info['unidade'])
        chave = (comarca_norm, unidade_norm)
        indice[chave] = {
            'codigo': codigo,
            'comarca_original': info['comarca'],
            'unidade_original': info['unidade']
        }
    return indice

def extrair_numeros(texto):
    """Extrai todos os números de um texto"""
    import re
    numeros = re.findall(r'\d+', texto)
    return tuple(numeros)

def matching_robusto(comarca, unidade, anexo2_index):
    """
    Tenta fazer match com ANEXO_II usando 3 estratégias

    Returns: (codigo_anexo2, match_type, score)
        - codigo_anexo2: código do ANEXO_II ou None
        - match_type: 'exact', 'fuzzy' ou 'not_found'
        - score: similaridade (0-1)
    """
    comarca_norm = normalizar_nome(comarca)
    unidade_norm = normalizar_nome(unidade)
    numeros_unidade = extrair_numeros(unidade_norm)

    # Tentativa 1: MATCH EXATO
    chave_exata = (comarca_norm, unidade_norm)
    if chave_exata in anexo2_index:
        return (anexo2_index[chave_exata]['codigo'], 'exact', 1.0)

    # Tentativa 2: FUZZY MATCH (comarca deve ser exata, apenas unidade fuzzy)
    # IMPORTANTE: Os números na unidade devem ser IDÊNTICOS (ex: 1ª Vara não pode virar 2ª Vara)
    best_match = None
    best_score = 0

    for (c_norm, u_norm), info in anexo2_index.items():
        # Comarca deve ser exata
        if c_norm != comarca_norm:
            continue

        # VALIDAÇÃO CRÍTICA: Números devem ser idênticos
        numeros_anexo2 = extrair_numeros(u_norm)
        if numeros_unidade != numeros_anexo2:
            continue  # Pula se os números não são exatamente iguais

        # Calcular similaridade da unidade
        score = SequenceMatcher(None, unidade_norm, u_norm).ratio()

        if score >= FUZZY_THRESHOLD and score > best_score:
            best_score = score
            best_match = info['codigo']

    if best_match:
        return (best_match, 'fuzzy', best_score)

    # Tentativa 3: NÃO ENCONTRADO
    return (None, 'not_found', 0.0)

print('='*80)
print('MAPEAMENTO PDF -> ANEXO_II')
print('='*80)

# Carregar dados consolidados do PDF
df_pdf = pd.read_excel('planilhas/lotacao_paradigma_consolidada.xlsx')
print(f'\nTotal de unidades no PDF: {len(df_pdf)}')
print(f'Total de códigos no ANEXO_II: {len(ANEXO_II)}')

# Criar índice do ANEXO_II
anexo2_index = criar_indice_anexo2()

# Fazer matching
resultados = {
    'exact': [],
    'fuzzy': [],
    'not_found': [],
    'paradigma_zero': []
}

for idx, row in df_pdf.iterrows():
    comarca = row['COMARCA']
    unidade = row['UNIDADE_JUDICIARIA']
    paradigma = row['LOTACAO_PARADIGMA']

    # Filtrar unidades com paradigma = 0
    if paradigma == 0:
        resultados['paradigma_zero'].append({
            'comarca': comarca,
            'unidade': unidade,
            'paradigma': paradigma
        })
        continue

    # Fazer matching
    codigo, match_type, score = matching_robusto(comarca, unidade, anexo2_index)

    resultados[match_type].append({
        'comarca': comarca,
        'unidade': unidade,
        'paradigma': paradigma,
        'bal_direito': row['BAL_DIREITO'],
        'tecnicos': row['TECNICOS'],
        'gab_efet': row['GAB_EFET'],
        'codigo_anexo2': codigo,
        'score': score
    })

# Relatório
print('\n' + '='*80)
print('RESULTADOS DO MATCHING')
print('='*80)

print(f'\nMatch EXATO: {len(resultados["exact"])} unidades')
print(f'Match FUZZY (>={FUZZY_THRESHOLD*100}%): {len(resultados["fuzzy"])} unidades')
print(f'NAO ENCONTRADO: {len(resultados["not_found"])} unidades')
print(f'PARADIGMA ZERO (ignoradas): {len(resultados["paradigma_zero"])} unidades')

total_matched = len(resultados['exact']) + len(resultados['fuzzy'])
total_valido = len(df_pdf) - len(resultados['paradigma_zero'])
print(f'\nTotal matched: {total_matched}/{total_valido} ({total_matched/total_valido*100:.1f}%)')

# Detalhes do fuzzy matching
if resultados['fuzzy']:
    print('\n' + '='*80)
    print('FUZZY MATCHES (VALIDAR MANUALMENTE):')
    print('='*80)
    for item in resultados['fuzzy']:
        anexo2_info = ANEXO_II[item['codigo_anexo2']]
        print(f'\n[{item["score"]*100:.1f}%] {item["codigo_anexo2"]}')
        print(f'  PDF: {item["comarca"]} / {item["unidade"]}')
        print(f'  ANEXO_II: {anexo2_info["comarca"]} / {anexo2_info["unidade"]}')
        print(f'  Paradigma: {item["paradigma"]} (bal={item["bal_direito"]}, tec={item["tecnicos"]}, gab={item["gab_efet"]})')

# Detalhes das não encontradas
if resultados['not_found']:
    print('\n' + '='*80)
    print('NAO ENCONTRADO (TOP 20):')
    print('='*80)
    for item in resultados['not_found'][:20]:
        print(f'\n{item["comarca"]} / {item["unidade"]}')
        print(f'  Paradigma: {item["paradigma"]} (bal={item["bal_direito"]}, tec={item["tecnicos"]}, gab={item["gab_efet"]})')

# Salvar resultados detalhados
df_matched = pd.DataFrame(resultados['exact'] + resultados['fuzzy'])
if not df_matched.empty:
    df_matched.to_excel('planilhas/mapeamento_pdf_anexo2.xlsx', index=False)
    print(f'\n\nArquivo de mapeamento salvo: planilhas/mapeamento_pdf_anexo2.xlsx')

print('\n' + '='*80)
