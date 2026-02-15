"""
Componentes UI reutilizáveis para Streamlit.

Fornece componentes customizados para melhorar a experiência do usuário,
incluindo cards, badges, alertas e tabelas formatadas.
"""
import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any


def card(title: str, content: str, icon: str = "📄", color: str = "blue"):
    """
    Renderiza um card informativo com título e conteúdo.

    Args:
        title: Título do card
        content: Conteúdo do card
        icon: Emoji ou ícone para o título
        color: Cor do card (blue, green, red, yellow, gray)

    Example:
        >>> card("Total de Inscritos", "156 servidores", icon="👥", color="blue")
    """
    color_var_map = {
        "blue": "var(--card-blue-bg)",
        "green": "var(--card-green-bg)",
        "red": "var(--card-red-bg)",
        "yellow": "var(--card-yellow-bg)",
        "gray": "var(--card-gray-bg)",
        "orange": "var(--card-orange-bg)"
    }

    bg_color = color_var_map.get(color, color_var_map["blue"])

    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: 20px;
        border-radius: 10px;
        border-left: 3px solid var(--border-accent);
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    ">
        <h3 style="margin: 0 0 10px 0; color: var(--text-accent);">
            {icon} {title}
        </h3>
        <p style="margin: 0; color: var(--text-primary); font-size: 16px;">
            {content}
        </p>
    </div>
    """, unsafe_allow_html=True)


def info_card(title: str, value: str, subtitle: str = "", icon: str = "ℹ️"):
    """
    Card compacto para exibir métricas ou informações chave.

    Args:
        title: Título/label da informação
        value: Valor principal (grande)
        subtitle: Texto adicional pequeno
        icon: Ícone do card

    Example:
        >>> info_card("Aprovados", "145", subtitle="de 200 inscritos", icon="✅")
    """
    st.markdown(f"""
    <div style="
        background-color: var(--border-accent);
        padding: 20px;
        border-radius: 8px;
        color: white;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    ">
        <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">{title}</div>
        <div style="font-size: 32px; font-weight: bold; margin-bottom: 5px;">{value}</div>
        {f'<div style="font-size: 12px; opacity: 0.8;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, status: str = "info"):
    """
    Renderiza um badge/tag inline.

    Args:
        text: Texto do badge
        status: Tipo do badge (success, warning, error, info, default)

    Returns:
        HTML string do badge

    Example:
        >>> st.markdown(f"Status: {badge('APROVADO', 'success')}", unsafe_allow_html=True)
    """
    status_colors = {
        "success": {"bg": "#4CAF50", "text": "#FFFFFF"},
        "warning": {"bg": "#FF9800", "text": "#FFFFFF"},
        "error": {"bg": "#F44336", "text": "#FFFFFF"},
        "info": {"bg": "#2196F3", "text": "#FFFFFF"},
        "default": {"bg": "#9E9E9E", "text": "#FFFFFF"},
    }

    colors = status_colors.get(status, status_colors["default"])

    return f"""
    <span style="
        background-color: {colors['bg']};
        color: {colors['text']};
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    ">{text}</span>
    """


def alert_box(message: str, alert_type: str = "info", dismissible: bool = False):
    """
    Caixa de alerta customizada com melhor visual.

    Args:
        message: Mensagem do alerta
        alert_type: Tipo (success, warning, error, info)
        dismissible: Se pode ser fechado (não implementado no Streamlit)

    Example:
        >>> alert_box("Dados salvos com sucesso!", "success")
    """
    type_config = {
        "success": {"icon": "✅", "color": "#4CAF50", "bg_var": "var(--alert-success-bg)"},
        "warning": {"icon": "⚠️", "color": "#FF9800", "bg_var": "var(--alert-warning-bg)"},
        "error": {"icon": "❌", "color": "#F44336", "bg_var": "var(--alert-error-bg)"},
        "info": {"icon": "ℹ️", "color": "#2196F3", "bg_var": "var(--alert-info-bg)"},
    }

    config = type_config.get(alert_type, type_config["info"])

    st.markdown(f"""
    <div style="
        background-color: {config['bg_var']};
        border-left: 4px solid {config['color']};
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
        display: flex;
        align-items: center;
    ">
        <span style="font-size: 24px; margin-right: 15px;">{config['icon']}</span>
        <span style="color: var(--text-primary); font-size: 14px;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def progress_bar(current: int, total: int, label: str = ""):
    """
    Barra de progresso customizada.

    Args:
        current: Valor atual
        total: Valor total
        label: Label descritivo

    Example:
        >>> progress_bar(45, 100, "Vagas preenchidas")
    """
    percentage = (current / total * 100) if total > 0 else 0

    st.markdown(f"""
    <div style="margin: 15px 0;">
        {f'<div style="font-size: 14px; margin-bottom: 5px; color: var(--text-primary);">{label}</div>' if label else ''}
        <div style="
            background-color: var(--progress-bg);
            border-radius: 10px;
            overflow: hidden;
            height: 25px;
            position: relative;
        ">
            <div style="
                background-color: var(--border-accent);
                height: 100%;
                width: {percentage}%;
                border-radius: 10px;
                transition: width 0.3s ease;
            "></div>
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: {'white' if percentage > 50 else 'var(--text-primary)'};
                font-weight: bold;
                font-size: 12px;
            ">{current}/{total} ({percentage:.1f}%)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def status_badge_for_resultado(status: str) -> str:
    """
    Badge específico para status de resultado.

    Args:
        status: Status do servidor (APROVADO, DESCLASSIFICADO, NÃO OBTEVE VAGA)

    Returns:
        HTML do badge

    Example:
        >>> st.markdown(status_badge_for_resultado("APROVADO"), unsafe_allow_html=True)
    """
    if status == "APROVADO":
        return badge("✅ APROVADO", "success")
    elif status == "DESCLASSIFICADO":
        return badge("❌ DESCLASSIFICADO", "error")
    elif status == "NÃO OBTEVE VAGA":
        return badge("⚠️ NÃO OBTEVE VAGA", "warning")
    else:
        return badge(status, "default")


def metric_card(label: str, value: str, delta: Optional[str] = None,
                icon: str = "📊", color: str = "blue"):
    """
    Card de métrica estilizado (similar ao st.metric mas customizado).

    Args:
        label: Label da métrica
        value: Valor principal
        delta: Mudança/comparação (opcional)
        icon: Ícone
        color: Cor do card

    Example:
        >>> metric_card("Total Inscritos", "156", delta="+12 hoje", icon="👥")
    """
    color_map = {
        "blue": "#2196F3",
        "green": "#4CAF50",
        "red": "#F44336",
        "orange": "#FF9800",
        "purple": "#9C27B0"
    }

    main_color = color_map.get(color, color_map["blue"])

    st.markdown(f"""
    <div style="
        background-color: var(--card-bg);
        padding: 24px;
        border-radius: 8px;
        border-top: 3px solid {main_color};
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin: 10px 0;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
            <span style="color: var(--text-secondary); font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">
                {label}
            </span>
        </div>
        <div style="font-size: 32px; font-weight: bold; color: {main_color}; margin-bottom: 5px;">
            {value}
        </div>
        {f'<div style="font-size: 13px; color: var(--text-muted);">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def styled_dataframe(df: pd.DataFrame, height: int = 400,
                     highlight_col: Optional[str] = None,
                     tema: Optional[Dict[str, str]] = None):
    """
    DataFrame com estilo melhorado.

    Args:
        df: DataFrame a exibir
        height: Altura da tabela
        highlight_col: Coluna para destacar
        tema: Dicionário de cores do tema (opcional, usa cores light como fallback)

    Example:
        >>> styled_dataframe(df_resultado, height=500, highlight_col="status")
    """
    if highlight_col and highlight_col in df.columns:
        approved_bg = tema["row_approved"] if tema else "#E8F5E9"
        rejected_bg = tema["row_rejected"] if tema else "#FFEBEE"
        no_vacancy_bg = tema.get("row_no_vacancy", "#FFF3E0") if tema else "#FFF3E0"

        def highlight_status(row):
            if row[highlight_col] == "APROVADO":
                return [f'background-color: {approved_bg}'] * len(row)
            elif row[highlight_col] == "DESCLASSIFICADO":
                return [f'background-color: {rejected_bg}'] * len(row)
            elif row[highlight_col] == "NÃO OBTEVE VAGA":
                return [f'background-color: {no_vacancy_bg}'] * len(row)
            return [''] * len(row)

        styled_df = df.style.apply(highlight_status, axis=1)
        st.dataframe(styled_df, height=height, use_container_width=True)
    else:
        st.dataframe(df, height=height, use_container_width=True)


def section_header(title: str, icon: str = "📌", subtitle: str = ""):
    """
    Cabeçalho de seção estilizado.

    Args:
        title: Título da seção
        icon: Ícone
        subtitle: Subtítulo opcional

    Example:
        >>> section_header("Resultado da Simulação", icon="🏆", subtitle="Edital 01/2026")
    """
    st.markdown(f"""
    <div style="
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid var(--border-accent);
    ">
        <h2 style="margin: 0; color: var(--text-accent); display: flex; align-items: center;">
            <span style="margin-right: 10px; font-size: 32px;">{icon}</span>
            {title}
        </h2>
        {f'<p style="margin: 5px 0 0 42px; color: var(--text-secondary); font-size: 14px;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def loading_spinner(message: str = "Carregando..."):
    """
    Context manager para spinner de loading.

    Args:
        message: Mensagem durante o loading

    Example:
        >>> with loading_spinner("Processando inscrições..."):
        ...     processar_dados()
    """
    return st.spinner(message)


def empty_state(message: str, icon: str = "📭", suggestion: str = ""):
    """
    Estado vazio quando não há dados.

    Args:
        message: Mensagem principal
        icon: Ícone grande
        suggestion: Sugestão de ação

    Example:
        >>> empty_state("Nenhuma inscrição encontrada", icon="📭",
        ...             suggestion="Faça sua inscrição na aba ✍️ Inscrição")
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 48px 20px;
        background-color: var(--empty-bg);
        border-radius: 8px;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 20px; opacity: 0.5;">{icon}</div>
        <h3 style="color: var(--text-secondary); margin-bottom: 10px;">{message}</h3>
        {f'<p style="color: var(--text-muted); font-size: 14px;">{suggestion}</p>' if suggestion else ''}
    </div>
    """, unsafe_allow_html=True)


def divider_with_text(text: str):
    """
    Divisor com texto no meio.

    Args:
        text: Texto do divisor

    Example:
        >>> divider_with_text("Fase 1 - Anexo I")
    """
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        margin: 25px 0;
    ">
        <div style="flex: 1; height: 1px; background-color: var(--divider-line);"></div>
        <span style="
            padding: 0 15px;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        ">{text}</span>
        <div style="flex: 1; height: 1px; background-color: var(--divider-line);"></div>
    </div>
    """, unsafe_allow_html=True)
