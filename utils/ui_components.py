"""
Componentes UI reutilizáveis para Streamlit.
"""
import streamlit as st
import pandas as pd
from typing import Optional


def alert_box(message: str, alert_type: str = "info", dismissible: bool = False):
    """
    Caixa de alerta customizada com melhor visual.

    Args:
        message: Mensagem do alerta
        alert_type: Tipo (success, warning, error, info)
        dismissible: Se pode ser fechado (não implementado no Streamlit)
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


def loading_spinner(message: str = "Carregando..."):
    """
    Context manager para spinner de loading.

    Args:
        message: Mensagem durante o loading
    """
    return st.spinner(message)


def empty_state(message: str, icon: str = "📭", suggestion: str = ""):
    """
    Estado vazio quando não há dados.

    Args:
        message: Mensagem principal
        icon: Ícone grande
        suggestion: Sugestão de ação
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
