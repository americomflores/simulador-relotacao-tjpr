"""
Serviço de lógica de simulação de relotação.
"""
import pandas as pd
from data import ANEXO_I, ANEXO_II
from lotacao_data import LOTACAO_POR_CODIGO
# DATA_LIMITE_ESTAGIO removido - Edital 01/2026 permite servidores em estágio probatório
from exceptions import SimulationError
from utils.logger import log_error


def obter_status_lotacao(codigo_unidade):
    """
    Retorna o status de lotação de uma unidade.
    
    Args:
        codigo_unidade: Código da unidade
        
    Returns:
        Status: SUPERAVITÁRIA, EQUILIBRADA, DEFICITÁRIA ou NÃO IDENTIFICADA
    """
    if codigo_unidade in LOTACAO_POR_CODIGO:
        return LOTACAO_POR_CODIGO[codigo_unidade]["status"]
    return "NÃO IDENTIFICADA"


def obter_dados_lotacao(codigo_unidade):
    """
    Retorna todos os dados de lotação de uma unidade.
    
    Args:
        codigo_unidade: Código da unidade
        
    Returns:
        Dicionário com dados de lotação ou None
    """
    if codigo_unidade in LOTACAO_POR_CODIGO:
        return LOTACAO_POR_CODIGO[codigo_unidade]
    return None


def calcular_lotacao_dinamica(codigo_unidade, ajuste=0):
    """
    Calcula a lotação considerando ajustes dinâmicos.
    
    Args:
        codigo_unidade: Código da unidade
        ajuste: Número de servidores a adicionar (+) ou remover (-)
        
    Returns:
        Dicionário com lotação calculada ou None
    """
    dados = obter_dados_lotacao(codigo_unidade)
    if not dados:
        return None
    
    nova_lotacao_real = dados["lotacao_real"] + ajuste
    nova_diferenca = nova_lotacao_real - dados["lotacao_paradigma"]
    
    if nova_diferenca > 0:
        novo_status = "SUPERAVITÁRIA"
    elif nova_diferenca == 0:
        novo_status = "EQUILIBRADA"
    else:
        novo_status = "DEFICITÁRIA"
    
    return {
        "lotacao_real": nova_lotacao_real,
        "lotacao_paradigma": dados["lotacao_paradigma"],
        "diferenca": nova_diferenca,
        "status": novo_status
    }


# Função verificar_estagio_probatorio removida - Edital 01/2026 permite servidores em estágio probatório


# Cache para mapeamento A1->A2 (calculado uma vez)
_mapeamento_a1_para_a2_cache = None


def _obter_mapeamento_a1_para_a2():
    """
    Obtém mapeamento de Anexo I para Anexo II (cacheado).
    
    Returns:
        Dicionário mapeando códigos A1 para A2
    """
    global _mapeamento_a1_para_a2_cache
    
    if _mapeamento_a1_para_a2_cache is None:
        mapeamento = {}
        # Criar índice reverso para otimizar busca
        anexo2_index = {}
        for codigo_a2, info_a2 in ANEXO_II.items():
            chave = (info_a2['comarca'].strip().lower(), info_a2['unidade'].strip().lower())
            if chave not in anexo2_index:
                anexo2_index[chave] = codigo_a2
        
        for codigo_a1, info_a1 in ANEXO_I.items():
            chave = (info_a1['comarca'].strip().lower(), info_a1['unidade'].strip().lower())
            if chave in anexo2_index:
                mapeamento[codigo_a1] = anexo2_index[chave]
        
        _mapeamento_a1_para_a2_cache = mapeamento
    
    return _mapeamento_a1_para_a2_cache


def calcular_resultado(df_inscricoes):
    """
    Calcula o resultado da simulação com lotação dinâmica.
    Inclui cálculo de "Designação na Origem" baseado no status da unidade.
    
    Implementa item 3.11 do Edital:
    "Se, durante a análise do Anexo II, for possível o deferimento em ambas as unidades,
    será concedido o deferimento para a unidade originalmente indicada no Anexo I."
    
    Args:
        df_inscricoes: DataFrame com inscrições
        
    Returns:
        Tupla (df_resultado, vagas_anexo1, vagas_anexo2, ajustes_lotacao)
    """
    if df_inscricoes.empty:
        return pd.DataFrame(), {}, {}, {}
    
    try:
        df = df_inscricoes.copy()

        # Garantir que posicao_lista_classificatoria está como Int64
        df["posicao_lista_classificatoria"] = pd.to_numeric(
            df["posicao_lista_classificatoria"],
            errors="coerce"
        ).astype("Int64")

        # Ordenar por posição na lista classificatória (posição 1 = maior prioridade)
        df = df.sort_values("posicao_lista_classificatoria", ascending=True, na_position='last').reset_index(drop=True)

        # Manter coluna posicao_antiguidade para compatibilidade (agora reflete posição da lista)
        df["posicao_antiguidade"] = df["posicao_lista_classificatoria"]
        df["status"] = ""
        df["resultado"] = ""
        df["vaga_obtida"] = ""
        df["observacao"] = ""
        df["designacao_origem"] = ""
        df["status_origem_inicial"] = ""
        df["status_origem_final"] = ""
        
        # Usar mapeamento cacheado
        mapeamento_a1_para_a2 = _obter_mapeamento_a1_para_a2()
        
        # Edital 01/2026: Servidores em estágio probatório PODEM participar
        # (Validação de estágio probatório removida)

        # Controle de vagas Anexo I
        vagas_anexo1 = {}
        for codigo, info in ANEXO_I.items():
            vagas_anexo1[codigo] = info["quantidade"]
        
        # Controle dinâmico de lotação das unidades
        # Começar com os valores originais e ajustar conforme movimentações
        ajustes_lotacao = {}  # codigo_unidade -> ajuste acumulado
        
        vagas_anexo2 = {}
        servidores_para_anexo2 = []
        
        # FASE 1: Processar Anexo I
        for row in df.itertuples():
            idx = row.Index
            if df.at[idx, "status"] == "DESCLASSIFICADO":
                continue

            escolha_a1 = row.escolha_anexo1
            lotacao_origem = row.lotacao_atual

            # Registrar status inicial da origem (cachear para evitar recálculo)
            if lotacao_origem and not df.at[idx, "status_origem_inicial"]:
                dados_origem = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao.get(lotacao_origem, 0))
                if dados_origem:
                    df.at[idx, "status_origem_inicial"] = dados_origem["status"]

            if escolha_a1 and escolha_a1 in vagas_anexo1:
                if vagas_anexo1[escolha_a1] > 0:
                    vagas_anexo1[escolha_a1] -= 1
                    df.at[idx, "status"] = "APROVADO"
                    df.at[idx, "resultado"] = "Anexo I (vaga deficitária disponibilizada - item 2.1)"
                    info_a1 = ANEXO_I.get(escolha_a1)
                    if info_a1:
                        df.at[idx, "vaga_obtida"] = f"{info_a1['comarca']} - {info_a1['unidade']}"
                    else:
                        df.at[idx, "vaga_obtida"] = f"Código {escolha_a1} (dados não encontrados)"

                    # Atualizar ajustes de lotação
                    if lotacao_origem:
                        # Servidor sai da origem (-1)
                        ajustes_lotacao[lotacao_origem] = ajustes_lotacao.get(lotacao_origem, 0) - 1

                        # Calcular status final da origem após saída
                        dados_origem_final = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao[lotacao_origem])
                        if dados_origem_final:
                            df.at[idx, "status_origem_final"] = dados_origem_final["status"]

                            # Determinar se precisa designação na origem
                            # Conforme item 3.14 do Edital: designação apenas se a saída OCASIONAR DÉFICIT
                            if dados_origem_final["status"] == "DEFICITÁRIA":
                                df.at[idx, "designacao_origem"] = "SIM"
                            else:
                                df.at[idx, "designacao_origem"] = "NÃO"

                        # REGRA: Liberar vaga no Anexo II APENAS se a origem ficar DEFICITÁRIA
                        if dados_origem_final and dados_origem_final["status"] == "DEFICITÁRIA":
                            if lotacao_origem in vagas_anexo2:
                                vagas_anexo2[lotacao_origem] += 1
                            else:
                                vagas_anexo2[lotacao_origem] = 1
                else:
                    servidores_para_anexo2.append(idx)
            elif escolha_a1:
                df.at[idx, "observacao"] = "Código Anexo I inválido"
                servidores_para_anexo2.append(idx)
            else:
                servidores_para_anexo2.append(idx)
        
        # FASE 2: Processar Anexo II
        # Conforme item 3.11: se possível deferimento em ambas as unidades (A1 e A2),
        # será concedido deferimento para a unidade originalmente indicada no Anexo I
        for idx in servidores_para_anexo2:
            row = df.loc[idx]
            escolha_a1 = row["escolha_anexo1"]  # Escolha original do Anexo I
            escolha_a2 = row["escolha_anexo2"]  # Escolha do Anexo II
            lotacao_origem = row["lotacao_atual"]
            
            # Registrar status inicial da origem (se ainda não registrado)
            if lotacao_origem and not df.at[idx, "status_origem_inicial"]:
                dados_origem = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao.get(lotacao_origem, 0))
                if dados_origem:
                    df.at[idx, "status_origem_inicial"] = dados_origem["status"]
            
            # Mapear escolha A1 para código A2 (mesma unidade) - usar cache
            codigo_a1_no_a2 = mapeamento_a1_para_a2.get(escolha_a1) if escolha_a1 else None
            
            # Verificar disponibilidade das vagas
            vaga_a1_disponivel = codigo_a1_no_a2 and codigo_a1_no_a2 in vagas_anexo2 and vagas_anexo2[codigo_a1_no_a2] > 0
            vaga_a2_disponivel = escolha_a2 and escolha_a2 in vagas_anexo2 and vagas_anexo2[escolha_a2] > 0
            
            # Determinar qual vaga conceder (prioridade para A1 conforme item 3.11)
            vaga_escolhida = None
            origem_vaga = None  # "A1" ou "A2"
            
            if vaga_a1_disponivel and vaga_a2_disponivel:
                # Ambas disponíveis: prioridade para A1 (item 3.11)
                vaga_escolhida = codigo_a1_no_a2
                origem_vaga = "ANEXO I (via A2)"
            elif vaga_a1_disponivel:
                # Apenas A1 disponível
                vaga_escolhida = codigo_a1_no_a2
                origem_vaga = "ANEXO I (via A2)"
            elif vaga_a2_disponivel:
                # Apenas A2 disponível
                vaga_escolhida = escolha_a2
                origem_vaga = "ANEXO II"
            
            if vaga_escolhida:
                vagas_anexo2[vaga_escolhida] -= 1

                # Atribuir resultado baseado no tipo de vaga
                if origem_vaga == "ANEXO I (via A2)":
                    resultado_final = "Anexo I (vaga primária incluída na análise do Anexo II - item 3.13)"
                else:
                    resultado_final = "Anexo II (vaga de servidor a relotar - item 3.11)"

                df.at[idx, "status"] = "APROVADO"
                df.at[idx, "resultado"] = resultado_final
                info_a2 = ANEXO_II.get(vaga_escolhida)
                if info_a2:
                    df.at[idx, "vaga_obtida"] = f"{info_a2['comarca']} - {info_a2['unidade']}"
                else:
                    df.at[idx, "vaga_obtida"] = f"Código {vaga_escolhida} (dados não encontrados)"
                
                # Atualizar ajustes de lotação
                if lotacao_origem and lotacao_origem != vaga_escolhida:
                    # Servidor sai da origem (-1)
                    ajustes_lotacao[lotacao_origem] = ajustes_lotacao.get(lotacao_origem, 0) - 1
                    
                    # Calcular status final da origem após saída
                    dados_origem_final = calcular_lotacao_dinamica(lotacao_origem, ajustes_lotacao[lotacao_origem])
                    if dados_origem_final:
                        df.at[idx, "status_origem_final"] = dados_origem_final["status"]
                        
                        # Determinar se precisa designação na origem
                        # Conforme item 3.14 do Edital: designação apenas se a saída OCASIONAR DÉFICIT
                        if dados_origem_final["status"] == "DEFICITÁRIA":
                            df.at[idx, "designacao_origem"] = "SIM"
                        else:
                            df.at[idx, "designacao_origem"] = "NÃO"
                    
                    # Liberar vaga no Anexo II APENAS se origem ficar DEFICITÁRIA (item 3.11)
                    if dados_origem_final and dados_origem_final["status"] == "DEFICITÁRIA":
                        if lotacao_origem in vagas_anexo2:
                            vagas_anexo2[lotacao_origem] += 1
                        else:
                            vagas_anexo2[lotacao_origem] = 1
                else:
                    df.at[idx, "designacao_origem"] = "-"
            else:
                # Nenhuma vaga disponível
                df.at[idx, "status"] = "NÃO OBTEVE VAGA"

                # Determinar motivo detalhado no resultado
                if escolha_a1 and escolha_a2:
                    motivo_a1 = "todas as vagas já foram preenchidas" if (escolha_a1 in ANEXO_I) else f"código inválido ({escolha_a1})"
                    motivo_a2 = "nenhum servidor saiu da unidade escolhida" if (escolha_a2 in ANEXO_II) else f"código inválido ({escolha_a2})"
                    df.at[idx, "resultado"] = f"Anexo I ({motivo_a1}) · Anexo II ({motivo_a2})"
                    df.at[idx, "observacao"] = "Vagas do Anexo I e II não disponíveis"
                elif escolha_a1:
                    motivo_a1 = "todas as vagas já foram preenchidas" if (escolha_a1 in ANEXO_I) else f"código inválido ({escolha_a1})"
                    df.at[idx, "resultado"] = f"Anexo I ({motivo_a1}) · Anexo II (não escolheu unidade)"
                    df.at[idx, "observacao"] = df.at[idx, "resultado"]
                elif escolha_a2:
                    motivo_a2 = "nenhum servidor saiu da unidade escolhida" if (escolha_a2 in ANEXO_II) else f"código inválido ({escolha_a2})"
                    df.at[idx, "resultado"] = f"Anexo I (não escolheu unidade) · Anexo II ({motivo_a2})"
                    df.at[idx, "observacao"] = df.at[idx, "resultado"]
                else:
                    df.at[idx, "resultado"] = "Anexo I (não escolheu unidade) · Anexo II (não escolheu unidade)"
                    df.at[idx, "observacao"] = df.at[idx, "resultado"]
                
                df.at[idx, "designacao_origem"] = "-"
        
        return df, vagas_anexo1, vagas_anexo2, ajustes_lotacao
    except Exception as e:
        log_error(e, "calcular_resultado")
        raise SimulationError(f"Erro ao calcular resultado: {e}")


def calcular_demanda(df_inscricoes):
    """
    Calcula a demanda por vaga (quantos servidores escolheram cada vaga).

    Args:
        df_inscricoes: DataFrame com inscrições

    Returns:
        Tupla (demanda_a1, demanda_a2) com dicionários de contagem por código
    """
    if df_inscricoes.empty:
        return {}, {}

    demanda_a1 = (
        df_inscricoes["escolha_anexo1"]
        .replace("", pd.NA).dropna()
        .value_counts().to_dict()
    )
    demanda_a2 = (
        df_inscricoes["escolha_anexo2"]
        .replace("", pd.NA).dropna()
        .value_counts().to_dict()
    )
    return demanda_a1, demanda_a2

