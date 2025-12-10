"""
Serviço de exportação de dados para Excel.

Gera arquivos Excel formatados para download com resultados de simulação,
inscrições e logs de atividades.
"""
import pandas as pd
from io import BytesIO
from datetime import datetime
from data import ANEXO_I, ANEXO_II


def gerar_excel_resultado(df_resultado):
    """
    Gera arquivo Excel formatado com resultado da simulação.

    Cria planilha Excel com colunas selecionadas do resultado, incluindo:
    - Dados do servidor (posição, nome, matrícula)
    - Lotação atual e vaga obtida
    - Status (APROVADO/DESCLASSIFICADO/NÃO OBTEVE VAGA)
    - Designação na origem (se necessário permanecer até substituição)

    Args:
        df_resultado: DataFrame retornado por calcular_resultado()

    Returns:
        bytes: Arquivo Excel em bytes pronto para download

    Example:
        >>> from services.simulacao_service import calcular_resultado
        >>> df_resultado, _, _, _ = calcular_resultado(df_inscricoes)
        >>> excel_bytes = gerar_excel_resultado(df_resultado)
        >>> # Use com st.download_button
    """
    output = BytesIO()

    # Adicionar unidade de origem formatada
    df_resultado_copy = df_resultado.copy()
    df_resultado_copy["unidade_origem"] = df_resultado_copy["lotacao_atual"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
    )

    # Preparar DataFrame para exportação
    df_export = df_resultado_copy[[
        "posicao_antiguidade", "nome", "matricula", "data_admissao",
        "unidade_origem", "status", "resultado", "vaga_obtida", "designacao_origem", "observacao"
    ]].copy()

    # Formatar data
    df_export["data_admissao"] = df_export["data_admissao"].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
    )

    # Renomear colunas
    df_export.columns = [
        "Posição", "Nome", "Matrícula", "Data Admissão",
        "Unidade de Origem", "Status", "Resultado", "Vaga Obtida", "Designação Origem", "Observação"
    ]

    # Criar Excel com pandas
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Resultado Simulação', index=False)

        # Aplicar formatação básica
        worksheet = writer.sheets['Resultado Simulação']
        _aplicar_formatacao_basica(worksheet, len(df_export))

    output.seek(0)
    return output.getvalue()


def gerar_excel_inscricoes(df_inscricoes):
    """
    Gera arquivo Excel com todas as inscrições.

    Args:
        df_inscricoes: DataFrame com inscrições dos servidores

    Returns:
        bytes: Arquivo Excel em bytes

    Example:
        >>> excel_bytes = gerar_excel_inscricoes(df_inscricoes)
    """
    output = BytesIO()

    df_export = df_inscricoes.copy()

    # Formatar data
    if "data_admissao" in df_export.columns:
        df_export["data_admissao"] = df_export["data_admissao"].apply(
            lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""
        )

    # Adicionar descrições das unidades
    df_export["lotacao_desc"] = df_export["lotacao_atual"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x in ANEXO_II else x
    )
    df_export["escolha_a1_desc"] = df_export["escolha_anexo1"].apply(
        lambda x: f"{ANEXO_I[x]['comarca']} - {ANEXO_I[x]['unidade']}" if x and x in ANEXO_I else "-"
    )
    df_export["escolha_a2_desc"] = df_export["escolha_anexo2"].apply(
        lambda x: f"{ANEXO_II[x]['comarca']} - {ANEXO_II[x]['unidade']}" if x and x in ANEXO_II else "-"
    )

    # Criar Excel com pandas
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Inscrições', index=False)

        worksheet = writer.sheets['Inscrições']
        _aplicar_formatacao_basica(worksheet, len(df_export))

    output.seek(0)
    return output.getvalue()


def gerar_excel_logs(df_inscricoes):
    """
    Gera arquivo Excel com logs de alterações.

    Args:
        df_inscricoes: DataFrame com inscrições (contém colunas de auditoria)

    Returns:
        bytes: Arquivo Excel em bytes

    Example:
        >>> excel_bytes = gerar_excel_logs(df_inscricoes)
    """
    output = BytesIO()

    colunas_log = ["nome", "matricula", "registrado_por", "alterado_por", "data_alteracao", "data_inscricao"]
    df_export = df_inscricoes[[c for c in colunas_log if c in df_inscricoes.columns]].copy()

    # Renomear colunas para português
    renomear = {
        "nome": "Nome",
        "matricula": "Matrícula",
        "registrado_por": "Registrado Por",
        "alterado_por": "Alterado Por",
        "data_alteracao": "Data Alteração",
        "data_inscricao": "Data Inscrição"
    }
    df_export.columns = [renomear.get(c, c) for c in df_export.columns]

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Logs de Alterações', index=False)

        worksheet = writer.sheets['Logs de Alterações']
        _aplicar_formatacao_basica(worksheet, len(df_export))

    output.seek(0)
    return output.getvalue()


def gerar_excel_comparacao(df_comparacao, df_nao_encontrados):
    """
    Gera Excel com comparação entre edital oficial e simulador.

    Args:
        df_comparacao: DataFrame com comparação lado a lado
        df_nao_encontrados: DataFrame com servidores não encontrados

    Returns:
        bytes: Arquivo Excel em bytes com múltiplas abas

    Example:
        >>> resultado = comparar_edital_simulador(df_csv, df_inscricoes)
        >>> excel_bytes = gerar_excel_comparacao(
        ...     resultado['df_comparacao'],
        ...     resultado['df_nao_encontrados']
        ... )
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Aba 1: Comparação
        df_comparacao.to_excel(writer, sheet_name='Comparação', index=False)
        worksheet1 = writer.sheets['Comparação']
        _aplicar_formatacao_basica(worksheet1, len(df_comparacao))

        # Aba 2: Não encontrados
        if not df_nao_encontrados.empty:
            df_nao_encontrados.to_excel(writer, sheet_name='Não Encontrados', index=False)
            worksheet2 = writer.sheets['Não Encontrados']
            _aplicar_formatacao_basica(worksheet2, len(df_nao_encontrados))

    output.seek(0)
    return output.getvalue()


def gerar_excel_vagas_disponiveis(vagas_restantes_a1, vagas_disponiveis_a2):
    """
    Gera Excel com vagas disponíveis após simulação.

    Args:
        vagas_restantes_a1: Dict com vagas restantes do Anexo I
        vagas_disponiveis_a2: Dict com vagas disponíveis do Anexo II

    Returns:
        bytes: Arquivo Excel em bytes

    Example:
        >>> df_resultado, vagas_a1, vagas_a2, _ = calcular_resultado(df_inscricoes)
        >>> excel_bytes = gerar_excel_vagas_disponiveis(vagas_a1, vagas_a2)
    """
    output = BytesIO()

    # Preparar dados Anexo I
    dados_a1 = []
    for codigo, qtd in vagas_restantes_a1.items():
        if qtd > 0 and codigo in ANEXO_I:
            dados_a1.append({
                'Código': codigo,
                'Comarca': ANEXO_I[codigo]['comarca'],
                'Unidade': ANEXO_I[codigo]['unidade'],
                'Vagas Disponíveis': qtd
            })

    df_a1 = pd.DataFrame(dados_a1)

    # Preparar dados Anexo II
    dados_a2 = []
    for codigo, qtd in vagas_disponiveis_a2.items():
        if qtd > 0 and codigo in ANEXO_II:
            dados_a2.append({
                'Código': codigo,
                'Comarca': ANEXO_II[codigo]['comarca'],
                'Unidade': ANEXO_II[codigo]['unidade'],
                'Vagas Disponíveis': qtd
            })

    df_a2 = pd.DataFrame(dados_a2)

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Anexo I
        df_a1.to_excel(writer, sheet_name='Anexo I Disponível', index=False)
        worksheet1 = writer.sheets['Anexo I Disponível']
        _aplicar_formatacao_basica(worksheet1, len(df_a1))

        # Anexo II
        df_a2.to_excel(writer, sheet_name='Anexo II Disponível', index=False)
        worksheet2 = writer.sheets['Anexo II Disponível']
        _aplicar_formatacao_basica(worksheet2, len(df_a2))

    output.seek(0)
    return output.getvalue()


def _aplicar_formatacao_basica(worksheet, num_rows):
    """
    Aplica formatação básica a uma worksheet do openpyxl.

    Args:
        worksheet: Worksheet do openpyxl
        num_rows: Número de linhas de dados (sem contar cabeçalho)
    """
    from openpyxl.styles import Font, PatternFill, Alignment

    # Formatação do cabeçalho
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Auto-ajustar largura das colunas
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        # Limitar largura máxima
        adjusted_width = min(max_length + 2, 50)
        worksheet.column_dimensions[column_letter].width = adjusted_width
