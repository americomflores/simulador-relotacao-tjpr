"""
Script de Correção de Dados de Lotação
Atualiza lotacao_data.py com:
  - Lotação REAL: Planilha BI (Tabela de Lotação de Pessoal das Unidades - BI.xlsx)
  - Lotação PARADIGMA: Mapeamento PDF (anexo-i-quadros-tjpr.pdf via mapeamento_pdf_anexo2.xlsx)

Uso:
    python scripts/corrigir_lotacao.py [--dry-run] [--backup-dir DIR]

Flags:
    --dry-run: Executa sem sobrescrever arquivos (apenas relatórios)
    --backup-dir: Diretório para backup (padrão: ./backups)
    --output: Arquivo de saída (padrão: lotacao_data.py)
"""

import sys
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
import shutil
import argparse

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data import ANEXO_II
from lotacao_data import LOTACAO_POR_CODIGO

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

CAMINHO_PLANILHA = "planilhas/Tabela de Lotação de Pessoal das Unidades - BI.xlsx"
CAMINHO_PDF_MAPPING = "planilhas/mapeamento_pdf_anexo2.xlsx"  # Mapeamento PDF -> ANEXO_II
FUZZY_THRESHOLD = 95  # Percentual mínimo para fuzzy matching (ajustado de 85% para 95%)
ARQUIVO_SAIDA = "lotacao_data.py"
DIR_BACKUP = "backups"

# ============================================================================
# FUNÇÕES DE NORMALIZAÇÃO
# ============================================================================

def normalizar_nome(texto):
    """Normaliza nome para comparação (case-insensitive, sem acentos, sem espaços extras)."""
    if not texto or pd.isna(texto):
        return ""

    # Converter para string e uppercase
    texto = str(texto).upper().strip()

    # Normalizar espaços múltiplos
    import re
    texto = re.sub(r'\s+', ' ', texto)

    # Remover acentos
    import unicodedata
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')

    return texto

# ============================================================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================================================

class ValidationError(Exception):
    """Erro de validação."""
    pass

def validar_dados_entrada():
    """Validações antes de iniciar processamento."""
    print("\nValidando dados de entrada...")

    checks = {}

    # Verificar planilha BI
    checks['planilha_existe'] = os.path.exists(CAMINHO_PLANILHA)
    if not checks['planilha_existe']:
        raise ValidationError(f"Planilha BI não encontrada: {CAMINHO_PLANILHA}")

    # Verificar mapeamento PDF
    checks['pdf_mapping_existe'] = os.path.exists(CAMINHO_PDF_MAPPING)
    if not checks['pdf_mapping_existe']:
        raise ValidationError(f"Mapeamento PDF não encontrado: {CAMINHO_PDF_MAPPING}")

    # Verificar ANEXO_II
    checks['anexo2_carregado'] = len(ANEXO_II) > 0
    if not checks['anexo2_carregado']:
        raise ValidationError("ANEXO_II não foi carregado corretamente")

    print(f"  [OK] Planilha BI encontrada: {CAMINHO_PLANILHA}")
    print(f"  [OK] Mapeamento PDF encontrado: {CAMINHO_PDF_MAPPING}")
    print(f"  [OK] ANEXO_II carregado: {len(ANEXO_II)} códigos")

    # Verificar LOTACAO_POR_CODIGO
    checks['lotacao_data_carregado'] = len(LOTACAO_POR_CODIGO) > 0
    if not checks['lotacao_data_carregado']:
        raise ValidationError("LOTACAO_POR_CODIGO não foi carregado corretamente")

    print(f"  [OK] LOTACAO_POR_CODIGO atual: {len(LOTACAO_POR_CODIGO)} códigos")

    return True

def validar_dados_saida(novos_dados, lotacao_completa):
    """Validações críticas antes de sobrescrever lotacao_data.py."""
    print("\nValidando dados de saída...")

    warnings = []
    errors = []

    # 1. Quantidade de códigos não pode diminuir drasticamente
    tamanho_antigo = len(LOTACAO_POR_CODIGO)
    tamanho_novo = len(novos_dados)

    if tamanho_novo < tamanho_antigo * 0.9:
        errors.append(f"ERRO: Perda significativa de códigos ({tamanho_antigo} -> {tamanho_novo})")
    else:
        print(f"  [OK] Quantidade de códigos: {tamanho_antigo} -> {tamanho_novo}")

    # 2. Todos os códigos devem estar no ANEXO_II ou serem legacy
    codigos_invalidos = [c for c in novos_dados if c not in ANEXO_II and not c.startswith("A2-")]
    if codigos_invalidos:
        warnings.append(f"AVISO: {len(codigos_invalidos)} códigos não estão no ANEXO_II")

    # 3. Estrutura de cada entrada deve estar completa
    required_keys = {'comarca', 'unidade', 'lotacao_real', 'lotacao_paradigma', 'diferenca', 'status'}
    for codigo, dados in novos_dados.items():
        if not required_keys.issubset(dados.keys()):
            errors.append(f"ERRO: Código {codigo} com estrutura incompleta")
            break  # Apenas um exemplo de erro

    if not errors:
        print(f"  [OK] Estrutura de dados: completa")

    # 4. Valores numéricos devem ser válidos
    valores_invalidos = 0
    for codigo, dados in novos_dados.items():
        if not isinstance(dados['lotacao_real'], int):
            valores_invalidos += 1
        if dados['lotacao_real'] < 0:
            valores_invalidos += 1

    if valores_invalidos > 0:
        errors.append(f"ERRO: {valores_invalidos} códigos com valores numéricos inválidos")
    else:
        print(f"  [OK] Valores numéricos: válidos")

    # 5. Status deve estar correto
    status_inconsistentes = 0
    for codigo, dados in novos_dados.items():
        status_esperado = calcular_status(dados['lotacao_real'], dados['lotacao_paradigma'])
        if dados['status'] != status_esperado:
            status_inconsistentes += 1

    if status_inconsistentes > 0:
        errors.append(f"ERRO: {status_inconsistentes} códigos com status inconsistente")
    else:
        print(f"  [OK] Status: consistente")

    # 6. Sincronia entre LOTACAO_POR_CODIGO e LOTACAO_COMPLETA
    if len(lotacao_completa) != len(novos_dados):
        errors.append(f"ERRO: Dessincronização entre dict ({len(novos_dados)}) e list ({len(lotacao_completa)})")
    else:
        print(f"  [OK] Sincronização LOTACAO_POR_CODIGO <-> LOTACAO_COMPLETA: 100%")

    if errors:
        raise ValidationError("\n".join(errors))

    return warnings

# ============================================================================
# FUNÇÕES DE MATCHING
# ============================================================================

def similarity_ratio(a, b):
    """Calcula similaridade entre duas strings (0-100)."""
    return SequenceMatcher(None, normalizar_nome(a), normalizar_nome(b)).ratio() * 100

def matching_robusto(comarca_planilha, unidade_planilha, anexo2_index):
    """
    Encontra código do ANEXO_II correspondente à entrada da planilha.

    Returns:
        (codigo_anexo2, match_type, score)
    """
    comarca_norm = normalizar_nome(comarca_planilha)
    unidade_norm = normalizar_nome(unidade_planilha)

    # Tentativa 1: MATCH EXATO (normalizado)
    chave = (comarca_norm, unidade_norm)
    if chave in anexo2_index:
        return anexo2_index[chave], 'exact', 100

    # Tentativa 2: FUZZY MATCH (comarca exata + unidade similar)
    melhor_match = None
    melhor_score = 0

    for (comarca_a2_norm, unidade_a2_norm), codigo_a2 in anexo2_index.items():
        # Comarca deve ser exata
        if comarca_a2_norm != comarca_norm:
            continue

        # Calcular similaridade da unidade
        score = similarity_ratio(unidade_planilha, unidade_a2_norm)

        if score >= FUZZY_THRESHOLD and score > melhor_score:
            melhor_score = score
            melhor_match = codigo_a2

    if melhor_match:
        return melhor_match, 'fuzzy', melhor_score

    # Tentativa 3: NÃO ENCONTRADO
    return None, 'not_found', 0

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================================

def carregar_e_agregar_planilha(caminho_excel):
    """
    Carrega planilha e agrega LR_Efet por unidade.

    Returns:
        DataFrame com colunas: Comarca, Unidade, LR_Efet_Total
    """
    print(f"\nCarregando planilha: {caminho_excel}")

    # Carregar Excel
    df = pd.read_excel(caminho_excel)

    print(f"  [OK] {len(df)} linhas carregadas")

    # Verificar colunas necessárias
    required_cols = ['Comarca', 'Unidade Judicial', 'LR_Efet']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValidationError(f"Colunas faltando na planilha: {missing}")

    # Filtrar linhas onde LR_Efet == "-"
    df_clean = df[df['LR_Efet'] != '-'].copy()

    # Converter LR_Efet e LP Unid Jud para numérico
    df_clean['LR_Efet_num'] = pd.to_numeric(df_clean['LR_Efet'], errors='coerce')
    df_clean['LP_Unid_Jud_num'] = pd.to_numeric(df_clean['LP Unid Jud'], errors='coerce')

    # Remover NaN de LR_Efet
    df_clean = df_clean.dropna(subset=['LR_Efet_num'])

    print(f"  [OK] {len(df_clean)} linhas válidas após filtrar valores '-' e inválidos")

    # Agrupar por (Comarca, Unidade Judicial) e somar LR_Efet + pegar max de LP
    df_agregado = df_clean.groupby(['Comarca', 'Unidade Judicial']).agg({
        'LR_Efet_num': 'sum',
        'LP_Unid_Jud_num': 'max'  # Pegar o máximo (geralmente é o mesmo valor)
    }).reset_index()

    df_agregado.rename(columns={
        'LR_Efet_num': 'LR_Efet_Total',
        'LP_Unid_Jud_num': 'LP_Total'
    }, inplace=True)

    # Converter para int
    df_agregado['LR_Efet_Total'] = df_agregado['LR_Efet_Total'].astype(int)
    df_agregado['LP_Total'] = df_agregado['LP_Total'].fillna(0).astype(int)  # Se NaN, usar 0

    print(f"  [OK] {len(df_agregado)} unidades únicas após agregação")

    return df_agregado

def carregar_mapeamento_pdf(caminho_excel):
    """
    Carrega mapeamento PDF -> ANEXO_II com dados de lotação paradigma.

    Returns:
        Dict: {codigo_anexo2: {'paradigma': X, 'bal_direito': Y, 'tecnicos': Z, 'gab_efet': W}}
    """
    print(f"\nCarregando mapeamento PDF: {caminho_excel}")

    # Carregar Excel
    df = pd.read_excel(caminho_excel)

    print(f"  [OK] {len(df)} unidades mapeadas carregadas")

    # Verificar colunas necessárias
    required_cols = ['codigo_anexo2', 'paradigma', 'bal_direito', 'tecnicos', 'gab_efet']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValidationError(f"Colunas faltando no mapeamento PDF: {missing}")

    # Criar dicionário de paradigma por código
    paradigma_dict = {}
    for _, row in df.iterrows():
        codigo = row['codigo_anexo2']
        paradigma_dict[codigo] = {
            'paradigma': int(row['paradigma']),
            'bal_direito': int(row['bal_direito']),
            'tecnicos': int(row['tecnicos']),
            'gab_efet': int(row['gab_efet'])
        }

    print(f"  [OK] {len(paradigma_dict)} códigos com dados de paradigma do PDF")

    return paradigma_dict

def calcular_status(lotacao_real, lotacao_paradigma):
    """Calcula status da unidade baseado na diferença."""
    diferenca = lotacao_real - lotacao_paradigma

    if diferenca > 0:
        return "SUPERAVITÁRIA"
    elif diferenca == 0:
        return "EQUILIBRADA"
    else:
        return "DEFICITÁRIA"

def processar_atualizacao(df_planilha, paradigma_dict):
    """
    Lógica principal de atualização.

    Args:
        df_planilha: DataFrame com lotação real (BI.xlsx)
        paradigma_dict: Dict com lotação paradigma (PDF)

    Returns:
        (novos_dados, estatisticas, divergencias, nao_mapeados, fuzzy_matches)
    """
    print("\nProcessando atualização...")

    # Criar índice normalizado do ANEXO_II
    anexo2_index = {}
    for codigo_a2, info_a2 in ANEXO_II.items():
        comarca_norm = normalizar_nome(info_a2['comarca'])
        unidade_norm = normalizar_nome(info_a2['unidade'])
        chave = (comarca_norm, unidade_norm)
        if chave not in anexo2_index:
            anexo2_index[chave] = codigo_a2

    print(f"  [OK] Índice de matching criado: {len(anexo2_index)} entradas")

    # Inicializar estruturas
    novos_dados = {}
    codigos_atualizados = set()

    estatisticas = {
        'total_planilha': len(df_planilha),
        'exact_match': 0,
        'fuzzy_match': 0,
        'not_found': 0,
        'atualizados': 0,
        'mantidos': 0,
        'novos': 0,
    }

    divergencias = []
    nao_mapeados = []
    fuzzy_matches = []

    # Processar cada linha da planilha (para lotação REAL)
    for idx, row in df_planilha.iterrows():
        comarca = row['Comarca']
        unidade = row['Unidade Judicial']
        lr_efet = int(row['LR_Efet_Total'])

        # Fazer matching
        codigo, match_type, score = matching_robusto(comarca, unidade, anexo2_index)

        # Atualizar estatísticas
        if match_type == 'exact':
            estatisticas['exact_match'] += 1
        elif match_type == 'fuzzy':
            estatisticas['fuzzy_match'] += 1
            fuzzy_matches.append({
                'codigo': codigo,
                'comarca': comarca,
                'unidade': unidade,
                'score': score,
                'unidade_anexo2': ANEXO_II[codigo]['unidade'],
                'lr_efet': lr_efet
            })
        else:
            estatisticas['not_found'] += 1
            nao_mapeados.append({
                'comarca': comarca,
                'unidade': unidade,
                'lr_efet': lr_efet,
                'motivo': 'Não encontrado no ANEXO_II'
            })
            continue

        # Processar código encontrado
        codigos_atualizados.add(codigo)

        # Obter paradigma do PDF (se disponível) ou manter atual
        if codigo in paradigma_dict:
            lp_paradigma = paradigma_dict[codigo]['paradigma']
        elif codigo in LOTACAO_POR_CODIGO:
            lp_paradigma = LOTACAO_POR_CODIGO[codigo]['lotacao_paradigma']
        else:
            lp_paradigma = 0  # Nova unidade sem paradigma no PDF

        # Verificar se código existe em LOTACAO_POR_CODIGO
        if codigo in LOTACAO_POR_CODIGO:
            dados_atuais = LOTACAO_POR_CODIGO[codigo]
            lotacao_antiga = dados_atuais['lotacao_real']
            paradigma_antigo = dados_atuais['lotacao_paradigma']

            # Registrar divergência se houver diferença
            if lotacao_antiga != lr_efet or paradigma_antigo != lp_paradigma:
                divergencias.append({
                    'codigo': codigo,
                    'comarca': comarca,
                    'unidade': unidade,
                    'planilha_real': lr_efet,
                    'pdf_paradigma': lp_paradigma,
                    'lotacao_atual': lotacao_antiga,
                    'paradigma_atual': paradigma_antigo,
                    'diferenca_real': lr_efet - lotacao_antiga,
                    'diferenca_paradigma': lp_paradigma - paradigma_antigo,
                    'match_type': match_type
                })

            # Atualizar dados
            novos_dados[codigo] = {
                'comarca': ANEXO_II[codigo]['comarca'],  # Usar nome oficial do ANEXO_II
                'unidade': ANEXO_II[codigo]['unidade'],  # Usar nome oficial do ANEXO_II
                'lotacao_real': lr_efet,  # ATUALIZADO do BI.xlsx
                'lotacao_paradigma': lp_paradigma,  # ATUALIZADO do PDF ou mantido
                'diferenca': lr_efet - lp_paradigma,  # RECALCULADO
                'status': calcular_status(lr_efet, lp_paradigma)  # RECALCULADO
            }

            estatisticas['atualizados'] += 1
        else:
            # Criar nova entrada
            novos_dados[codigo] = {
                'comarca': ANEXO_II[codigo]['comarca'],
                'unidade': ANEXO_II[codigo]['unidade'],
                'lotacao_real': lr_efet,
                'lotacao_paradigma': lp_paradigma,
                'diferenca': lr_efet - lp_paradigma,
                'status': calcular_status(lr_efet, lp_paradigma)
            }

            estatisticas['novos'] += 1

    # Processar códigos que só estão no PDF (atualizar apenas paradigma)
    for codigo, paradigma_info in paradigma_dict.items():
        if codigo not in codigos_atualizados and codigo in LOTACAO_POR_CODIGO:
            dados_atuais = LOTACAO_POR_CODIGO[codigo]
            lp_paradigma = paradigma_info['paradigma']
            lr_efet = dados_atuais['lotacao_real']  # Manter lotacao_real atual

            # Atualizar apenas paradigma
            novos_dados[codigo] = {
                'comarca': dados_atuais['comarca'],
                'unidade': dados_atuais['unidade'],
                'lotacao_real': lr_efet,  # MANTIDO
                'lotacao_paradigma': lp_paradigma,  # ATUALIZADO do PDF
                'diferenca': lr_efet - lp_paradigma,
                'status': calcular_status(lr_efet, lp_paradigma)
            }

            codigos_atualizados.add(codigo)
            estatisticas['atualizados'] += 1

            # Registrar divergência se houver mudança no paradigma
            if dados_atuais['lotacao_paradigma'] != lp_paradigma:
                divergencias.append({
                    'codigo': codigo,
                    'comarca': dados_atuais['comarca'],
                    'unidade': dados_atuais['unidade'],
                    'planilha_real': lr_efet,
                    'pdf_paradigma': lp_paradigma,
                    'lotacao_atual': lr_efet,
                    'paradigma_atual': dados_atuais['lotacao_paradigma'],
                    'diferenca_real': 0,
                    'diferenca_paradigma': lp_paradigma - dados_atuais['lotacao_paradigma'],
                    'match_type': 'pdf_only'
                })

    # Processar códigos não atualizados (manter dados atuais)
    for codigo, dados_atuais in LOTACAO_POR_CODIGO.items():
        if codigo not in codigos_atualizados:
            novos_dados[codigo] = dados_atuais.copy()
            estatisticas['mantidos'] += 1

    print(f"  [OK] Processamento concluído:")
    print(f"    - Exact match: {estatisticas['exact_match']}")
    print(f"    - Fuzzy match: {estatisticas['fuzzy_match']}")
    print(f"    - Not found: {estatisticas['not_found']}")
    print(f"    - Atualizados: {estatisticas['atualizados']}")
    print(f"    - Mantidos (sem atualização): {estatisticas['mantidos']}")
    print(f"    - Novos: {estatisticas['novos']}")

    return novos_dados, estatisticas, divergencias, nao_mapeados, fuzzy_matches

# ============================================================================
# FUNÇÕES DE SINCRONIZAÇÃO
# ============================================================================

def gerar_lotacao_completa(lotacao_por_codigo):
    """
    Gera LOTACAO_COMPLETA a partir de LOTACAO_POR_CODIGO.
    Garante 100% de sincronia.
    """
    lotacao_completa = []

    for codigo in sorted(lotacao_por_codigo.keys()):
        dados = lotacao_por_codigo[codigo]
        entrada = {
            'comarca': dados['comarca'],
            'unidade': dados['unidade'],
            'lotacao_real': dados['lotacao_real'],
            'lotacao_paradigma': dados['lotacao_paradigma'],
            'diferenca': dados['diferenca'],
            'status': dados['status'],
            'codigo_anexo2': codigo
        }
        lotacao_completa.append(entrada)

    return lotacao_completa

# ============================================================================
# FUNÇÕES DE RELATÓRIO
# ============================================================================

def gerar_relatorio_completo(estatisticas, divergencias, nao_mapeados, fuzzy_matches, warnings):
    """Gera relatório detalhado da atualização."""

    relatorio = []
    relatorio.append("=" * 80)
    relatorio.append("RELATÓRIO DE ATUALIZAÇÃO DE LOTAÇÃO")
    relatorio.append("=" * 80)
    relatorio.append(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Estatísticas gerais
    relatorio.append("\n" + "=" * 80)
    relatorio.append("ESTATÍSTICAS GERAIS")
    relatorio.append("=" * 80)
    relatorio.append(f"Total de unidades na planilha: {estatisticas['total_planilha']}")
    relatorio.append(f"Match exato: {estatisticas['exact_match']}")
    relatorio.append(f"Match fuzzy (>={FUZZY_THRESHOLD}%): {estatisticas['fuzzy_match']}")
    relatorio.append(f"Não encontrados: {estatisticas['not_found']}")
    relatorio.append(f"Total de códigos atualizados: {estatisticas['atualizados']}")
    relatorio.append(f"Códigos mantidos (sem atualização): {estatisticas['mantidos']}")
    relatorio.append(f"Novas entradas criadas: {estatisticas['novos']}")

    # Fuzzy matches (REVISÃO MANUAL OBRIGATÓRIA)
    if fuzzy_matches:
        relatorio.append("\n" + "=" * 80)
        relatorio.append(f"[!] FUZZY MATCHES - REVISÃO MANUAL OBRIGATÓRIA ({len(fuzzy_matches)})")
        relatorio.append("=" * 80)
        relatorio.append("\nCód.    | Score | Planilha -> Anexo II")
        relatorio.append("-" * 80)

        for fm in sorted(fuzzy_matches, key=lambda x: x['score']):
            relatorio.append(
                f"{fm['codigo']:7} | {fm['score']:5.1f}% | {fm['unidade'][:35]}\n"
                f"{'':7} | {'':6} | -> {fm['unidade_anexo2'][:35]} (ANEXO_II)\n"
            )

    # Divergências encontradas
    if divergencias:
        relatorio.append("\n" + "=" * 80)
        relatorio.append(f"DIVERGÊNCIAS ENCONTRADAS ({len(divergencias)})")
        relatorio.append("=" * 80)
        relatorio.append("\nCod.    | Real P->A (d) | Parad P->A (d) | Match    | Comarca - Unidade")
        relatorio.append("-" * 80)

        for div in sorted(divergencias, key=lambda x: abs(x.get('diferenca_real', 0)), reverse=True)[:50]:
            relatorio.append(
                f"{div['codigo']:7} | {div['planilha_real']:3}->{div['lotacao_atual']:3} "
                f"({div['diferenca_real']:+2}) | "
                f"{div['pdf_paradigma']:3}->{div['paradigma_atual']:3} "
                f"({div['diferenca_paradigma']:+2}) | "
                f"{div['match_type']:8} | "
                f"{div['comarca']} - {div['unidade'][:30]}"
            )

        if len(divergencias) > 50:
            relatorio.append(f"\n... e mais {len(divergencias) - 50} divergências")

    # Unidades não mapeadas
    if nao_mapeados:
        relatorio.append("\n" + "=" * 80)
        relatorio.append(f"UNIDADES NÃO MAPEADAS ({len(nao_mapeados)})")
        relatorio.append("=" * 80)

        for nm in nao_mapeados[:30]:
            relatorio.append(f"- {nm['comarca']} - {nm['unidade'][:60]} (LR_Efet={nm['lr_efet']})")

        if len(nao_mapeados) > 30:
            relatorio.append(f"\n... e mais {len(nao_mapeados) - 30} não mapeados")

    # Warnings
    if warnings:
        relatorio.append("\n" + "=" * 80)
        relatorio.append(f"AVISOS ({len(warnings)})")
        relatorio.append("=" * 80)
        for w in warnings:
            relatorio.append(f"- {w}")

    relatorio.append("\n" + "=" * 80)
    relatorio.append("FIM DO RELATÓRIO")
    relatorio.append("=" * 80)

    return "\n".join(relatorio)

# ============================================================================
# FUNÇÃO DE GERAÇÃO DO ARQUIVO
# ============================================================================

def gerar_arquivo_lotacao_data(lotacao_por_codigo, lotacao_completa, arquivo_saida):
    """Gera novo arquivo lotacao_data.py com formatação correta."""

    linhas = []
    linhas.append('"""')
    linhas.append('Dados de Lotação Paradigma - TJPR')
    linhas.append(f'Atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    linhas.append('Fonte: Tabela de Lotação de Pessoal das Unidades - BI.xlsx')
    linhas.append('Script: scripts/corrigir_lotacao.py')
    linhas.append('"""')
    linhas.append('')
    linhas.append('# Mapeamento: Código Anexo II -> Dados de Lotação')
    linhas.append('LOTACAO_POR_CODIGO = {')

    # Gerar LOTACAO_POR_CODIGO
    for codigo in sorted(lotacao_por_codigo.keys()):
        dados = lotacao_por_codigo[codigo]
        linhas.append(f'    "{codigo}": {{')
        linhas.append(f'        "comarca": "{dados["comarca"]}",')
        linhas.append(f'        "unidade": "{dados["unidade"]}",')
        linhas.append(f'        "lotacao_real": {dados["lotacao_real"]},')
        linhas.append(f'        "lotacao_paradigma": {dados["lotacao_paradigma"]},')
        linhas.append(f'        "diferenca": {dados["diferenca"]},')
        linhas.append(f'        "status": "{dados["status"]}",')
        linhas.append('    },')

    linhas.append('}')
    linhas.append('')
    linhas.append('# Lista completa de lotações (espelhada de LOTACAO_POR_CODIGO)')
    linhas.append('LOTACAO_COMPLETA = [')

    # Gerar LOTACAO_COMPLETA
    for entrada in lotacao_completa:
        linhas.append('    {')
        linhas.append(f'        "comarca": "{entrada["comarca"]}",')
        linhas.append(f'        "unidade": "{entrada["unidade"]}",')
        linhas.append(f'        "lotacao_real": {entrada["lotacao_real"]},')
        linhas.append(f'        "lotacao_paradigma": {entrada["lotacao_paradigma"]},')
        linhas.append(f'        "diferenca": {entrada["diferenca"]},')
        linhas.append(f'        "status": "{entrada["status"]}",')
        linhas.append(f'        "codigo_anexo2": "{entrada["codigo_anexo2"]}"')
        linhas.append('    },')

    linhas.append(']')
    linhas.append('')

    # Escrever arquivo
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))

    return arquivo_saida

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Corrigir dados de lotação')
    parser.add_argument('--dry-run', action='store_true', help='Executar sem sobrescrever arquivos')
    parser.add_argument('--backup-dir', default=DIR_BACKUP, help='Diretório para backups')
    parser.add_argument('--output', default=ARQUIVO_SAIDA, help='Arquivo de saída')
    args = parser.parse_args()

    print("=" * 80)
    print("SCRIPT DE CORREÇÃO DE DADOS DE LOTAÇÃO")
    print("=" * 80)
    print(f"\nModo: {'DRY-RUN (sem alterações)' if args.dry_run else 'PRODUÇÃO (vai sobrescrever)'}")
    print(f"Planilha BI (Lotação REAL): {CAMINHO_PLANILHA}")
    print(f"Mapeamento PDF (Lotação PARADIGMA): {CAMINHO_PDF_MAPPING}")
    print(f"Arquivo saída: {args.output}")

    try:
        # 1. Validar dados de entrada
        print("\n[1/8] Validando dados de entrada...")
        validar_dados_entrada()

        # 2. Carregar e agregar planilha (lotação REAL)
        print("\n[2/8] Carregando e agregando planilha BI (lotação REAL)...")
        df_agregado = carregar_e_agregar_planilha(CAMINHO_PLANILHA)

        # 3. Carregar mapeamento PDF (lotação PARADIGMA)
        print("\n[3/8] Carregando mapeamento PDF (lotação PARADIGMA)...")
        paradigma_dict = carregar_mapeamento_pdf(CAMINHO_PDF_MAPPING)

        # 4. Processar atualização
        print("\n[4/8] Processando matching e atualização...")
        novos_dados, estatisticas, divergencias, nao_mapeados, fuzzy_matches = processar_atualizacao(df_agregado, paradigma_dict)

        # 5. Gerar LOTACAO_COMPLETA
        print("\n[5/8] Gerando LOTACAO_COMPLETA...")
        lotacao_completa = gerar_lotacao_completa(novos_dados)
        print(f"  [OK] {len(lotacao_completa)} entradas (100% sincronizado)")

        # 6. Validar dados de saída
        print("\n[6/8] Validando dados de saída...")
        warnings = validar_dados_saida(novos_dados, lotacao_completa)
        if warnings:
            print(f"  [AVISO] {len(warnings)} avisos")
            for w in warnings[:5]:  # Mostrar apenas primeiros 5
                print(f"    - {w}")

        # 7. Gerar relatório
        print("\n[7/8] Gerando relatório...")
        relatorio = gerar_relatorio_completo(estatisticas, divergencias, nao_mapeados, fuzzy_matches, warnings)

        # Salvar relatório
        Path(args.backup_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_relatorio = f"{args.backup_dir}/relatorio_correcao_{timestamp}.txt"
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f"  [OK] Relatório salvo: {arquivo_relatorio}")

        # 8. Backup e sobrescrita
        if not args.dry_run:
            print("\n[8/8] Criando backup e sobrescrevendo arquivo...")

            # Backup
            if os.path.exists(args.output):
                arquivo_backup = f"{args.backup_dir}/lotacao_data_backup_{timestamp}.py"
                shutil.copy2(args.output, arquivo_backup)
                print(f"  [OK] Backup criado: {arquivo_backup}")

            # Gerar novo arquivo
            gerar_arquivo_lotacao_data(novos_dados, lotacao_completa, args.output)
            print(f"  [OK] Arquivo atualizado: {args.output}")

            print("\n" + "=" * 80)
            print("ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 80)
            print(f"\nArquivos gerados:")
            print(f"  - {args.output} (atualizado)")
            if os.path.exists(f"{args.backup_dir}/lotacao_data_backup_{timestamp}.py"):
                print(f"  - {args.backup_dir}/lotacao_data_backup_{timestamp}.py (backup)")
            print(f"  - {arquivo_relatorio} (relatório)")

            if fuzzy_matches:
                print(f"\n[ATENCAO] {len(fuzzy_matches)} fuzzy matches foram aplicados.")
                print(f"    Revise o relatório para verificar se estão corretos!")
        else:
            print("\n[8/8] MODO DRY-RUN - Nenhum arquivo foi modificado")
            print("\n" + "=" * 80)
            print("SIMULAÇÃO CONCLUÍDA")
            print("=" * 80)
            print("\nPara aplicar as alterações, execute sem --dry-run:")
            print(f"  python scripts/corrigir_lotacao.py")

        # Exibir resumo do relatório
        print("\n" + "=" * 80)
        print("RESUMO DO RELATÓRIO")
        print("=" * 80)
        print(relatorio)

    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
