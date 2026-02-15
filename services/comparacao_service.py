"""
Serviço de comparação entre resultado oficial do TJPR e simulação.
"""
import streamlit as st
import pandas as pd
from data import ANEXO_II
from utils.normalizers import normalizar_nome, nomes_sao_iguais, tentar_match_anexo2


def processar_csv_edital(uploaded_file):
    """
    Processa o CSV do edital oficial e retorna DataFrame tratado.
    """
    try:
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')
        df.columns = ['tipo', 'servidor', 'vaga', 'processo', 'data', 'situacao']
        df['servidor'] = df['servidor'].str.strip()
        df['vaga'] = df['vaga'].str.strip()
        df['situacao'] = df['situacao'].str.strip()
        df['servidor_normalizado'] = df['servidor'].apply(normalizar_nome)
        return df
    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
        return None


def comparar_edital_simulador(df_csv, df_inscricoes):
    """
    Compara resultado oficial do TJPR com simulação.

    Realiza fuzzy matching entre servidores do CSV oficial e inscrições do simulador
    para identificar acertos, erros e discrepâncias.
    """
    resultados = {
        'coincidentes': [],
        'faltam_simulador': [],
        'remover_simulador': [],
        'csv_finalizados': [],
        'csv_nao_finalizados': []
    }

    # 1. Filtrar apenas inscrições finalizadas do CSV
    df_finalizados = df_csv[df_csv['situacao'] == 'Finalizado'].copy()

    # 2. Pegar lista única de servidores com inscrição finalizada
    servidores_finalizados = df_finalizados.groupby('servidor_normalizado').agg({
        'servidor': 'first',
        'vaga': lambda x: list(x.unique()),
        'processo': lambda x: list(x.unique()),
        'data': 'max'
    }).reset_index()

    resultados['csv_finalizados'] = servidores_finalizados.to_dict('records')

    # 3. Servidores que só têm inscrições não finalizadas
    servidores_todos = set(df_csv['servidor_normalizado'].unique())
    servidores_ok = set(df_finalizados['servidor_normalizado'].unique())
    servidores_problema = servidores_todos - servidores_ok

    for nome_norm in servidores_problema:
        registros = df_csv[df_csv['servidor_normalizado'] == nome_norm]
        nome_original = registros['servidor'].iloc[0]
        situacoes = registros['situacao'].unique().tolist()
        resultados['csv_nao_finalizados'].append({
            'nome': nome_original,
            'nome_normalizado': nome_norm,
            'situacoes': situacoes
        })

    # 4. Preparar dados do simulador
    if not df_inscricoes.empty:
        df_inscricoes = df_inscricoes.copy()
        df_inscricoes['nome_normalizado'] = df_inscricoes['nome'].apply(normalizar_nome)
        lista_simulador = [
            {
                'nome': row['nome'],
                'nome_normalizado': row['nome_normalizado'],
                'matricula': row['matricula']
            }
            for _, row in df_inscricoes.iterrows()
        ]
    else:
        lista_simulador = []

    # 5. Lista de servidores finalizados no CSV
    lista_csv = [
        {
            'nome': row['servidor'],
            'nome_normalizado': row['servidor_normalizado'],
            'vagas': row['vaga'],
            'data': row['data']
        }
        for _, row in servidores_finalizados.iterrows()
    ]

    # 6. Comparar usando função flexível
    csv_encontrados = set()
    simulador_encontrados = set()

    for i, srv_csv in enumerate(lista_csv):
        for j, srv_sim in enumerate(lista_simulador):
            if nomes_sao_iguais(srv_csv['nome'], srv_sim['nome']):
                csv_encontrados.add(i)
                simulador_encontrados.add(j)
                resultados['coincidentes'].append({
                    'nome_csv': srv_csv['nome'],
                    'nome_simulador': srv_sim['nome'],
                    'matricula': srv_sim['matricula'],
                    'vagas_csv': srv_csv['vagas']
                })
                break

    # 7. Servidores do CSV não encontrados no simulador
    for i, srv_csv in enumerate(lista_csv):
        if i not in csv_encontrados:
            vagas_match = []
            for vaga in srv_csv['vagas']:
                codigo, score = tentar_match_anexo2(vaga)
                vagas_match.append({
                    'vaga_csv': vaga,
                    'codigo_anexo2': codigo,
                    'score': score,
                    'unidade_anexo2': f"{ANEXO_II[codigo]['comarca']} - {ANEXO_II[codigo]['unidade']}" if codigo else None
                })

            resultados['faltam_simulador'].append({
                'nome': srv_csv['nome'],
                'nome_normalizado': srv_csv['nome_normalizado'],
                'vagas': vagas_match,
                'data': srv_csv['data']
            })

    # 8. Servidores do simulador não encontrados no CSV finalizado
    for j, srv_sim in enumerate(lista_simulador):
        if j not in simulador_encontrados:
            encontrado_nao_finalizado = False
            for srv_nf in resultados['csv_nao_finalizados']:
                if nomes_sao_iguais(srv_sim['nome'], srv_nf['nome']):
                    encontrado_nao_finalizado = True
                    break

            motivo = ("Inscrição NÃO FINALIZADA no edital oficial" if encontrado_nao_finalizado
                      else "NÃO ENCONTRADO no edital oficial")

            resultados['remover_simulador'].append({
                'nome': srv_sim['nome'],
                'matricula': srv_sim['matricula'],
                'motivo': motivo
            })

    return resultados
