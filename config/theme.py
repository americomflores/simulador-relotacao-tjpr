"""
Tema visual e CSS do Simulador de Relotação TJPR.
"""
import streamlit as st


TEMAS = {
    "light": {
        "row_approved": "#d4edda",
        "row_waiting": "#fff3cd",
        "row_rejected": "#f8d7da",
        "row_no_vacancy": "#e2e3e5",
        "status_superavit": "#d4edda",
        "status_equilibrada": "#fff3cd",
        "status_deficitaria": "#f8d7da",
        "text_positive": "green",
        "text_negative": "red",
        "chart_green": "#28a745",
        "chart_red": "#dc3545",
        "chart_gray": "#6c757d",
        "chart_blue": "#2563EB",
        "chart_green2": "#43A047",
        "chart_yellow": "#ffc107",
        "chart_scale": "Blues",
        "plotly_template": "plotly_white",
    },
    "dark": {
        "row_approved": "#1a3d2e",
        "row_waiting": "#3d3419",
        "row_rejected": "#3d1f1f",
        "row_no_vacancy": "#2d2d2d",
        "status_superavit": "#1a3d2e",
        "status_equilibrada": "#3d3419",
        "status_deficitaria": "#3d1f1f",
        "text_positive": "#4ade80",
        "text_negative": "#f87171",
        "chart_green": "#4ade80",
        "chart_red": "#f87171",
        "chart_gray": "#9ca3af",
        "chart_blue": "#60a5fa",
        "chart_green2": "#86efac",
        "chart_yellow": "#fbbf24",
        "chart_scale": "Teal",
        "plotly_template": "plotly_dark",
    },
}


def _is_dark_mode():
    """Detecta se o tema escuro está ativo."""
    try:
        return getattr(st.context.theme, "type", "light") == "dark"
    except Exception:
        return st.session_state.get("dark_mode", False)


def get_tema():
    """Retorna o dicionário de cores do tema atual."""
    return TEMAS["dark"] if _is_dark_mode() else TEMAS["light"]


_CSS_VARS_LIGHT = """
:root {
    --card-bg: white;
    --card-shadow: rgba(0,0,0,0.08);
    --card-blue-bg: #EFF6FF;
    --card-green-bg: #F0FDF4;
    --card-red-bg: #FEF2F2;
    --card-yellow-bg: #FEFCE8;
    --card-gray-bg: #F8FAFC;
    --card-orange-bg: #FFF7ED;
    --border-accent: #2563EB;
    --text-primary: #1E293B;
    --text-secondary: #64748B;
    --text-muted: #94A3B8;
    --text-accent: #2563EB;
    --empty-bg: #F8FAFC;
    --divider-line: #E2E8F0;
    --progress-bg: #E2E8F0;
    --alert-info-bg: #EFF6FF;
    --alert-success-bg: #F0FDF4;
    --alert-warning-bg: #FFF7ED;
    --alert-error-bg: #FEF2F2;
    --raj-border: #E2E8F0;
}
"""

_CSS_VARS_DARK = """
:root {
    --card-bg: #1e1e2e;
    --card-shadow: rgba(0,0,0,0.3);
    --card-blue-bg: #1a2744;
    --card-green-bg: #1a3d2e;
    --card-red-bg: #3d1f1f;
    --card-yellow-bg: #3d3419;
    --card-gray-bg: #2d2d2d;
    --card-orange-bg: #3d2e1a;
    --border-accent: #60a5fa;
    --text-primary: #e0e0e0;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --text-accent: #60a5fa;
    --empty-bg: #1a1a2e;
    --divider-line: #444;
    --progress-bg: #333;
    --alert-info-bg: #1a2744;
    --alert-success-bg: #1a3d2e;
    --alert-warning-bg: #3d2e1a;
    --alert-error-bg: #3d1f1f;
    --raj-border: #444;
}
"""

_CSS_DARK_OVERRIDES = """
.stApp {
    background-color: #0e0e1a !important;
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] {
    background-color: #161625 !important;
}
[data-testid="stHeader"] {
    background-color: #0e0e1a !important;
}
input, textarea, select, [data-baseweb="select"],
[data-baseweb="input"], [data-baseweb="textarea"] {
    background-color: #1e1e2e !important;
    color: #e0e0e0 !important;
}
[data-testid="metric-container"] {
    background-color: #1e1e2e !important;
    color: #e0e0e0 !important;
}
[data-testid="metric-container"] label {
    color: #9ca3af !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e0e0e0 !important;
}
h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
    color: #e0e0e0 !important;
}
[data-testid="stDataFrame"] {
    border-radius: 8px;
}
.stTabs [data-baseweb="tab"] {
    color: #9ca3af !important;
}
.stTabs [aria-selected="true"] {
    color: #60a5fa !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #60a5fa !important;
}
.stCaption, caption {
    color: #6b7280 !important;
}
hr {
    border-color: #333 !important;
}
"""

_CSS_RESPONSIVE = """
@media (max-width: 768px) {
    .stColumn {
        padding: 0 5px !important;
    }
    [data-testid="metric-container"] {
        padding: 10px 5px !important;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
    }
    h3 {
        font-size: 1rem !important;
    }
    .stDataFrame {
        overflow-x: auto !important;
    }
}

/* Cards de RAJ */
.raj-box {
    border: 1px solid var(--raj-border);
    border-radius: 8px;
    padding: 10px;
    margin: 5px 0;
    text-align: center;
}

/* Transições suaves */
* {
    transition: background-color 0.2s ease, color 0.2s ease;
}
"""


def inject_css():
    """Injeta todo o CSS do tema na página."""
    is_dark = _is_dark_mode()

    css_vars = _CSS_VARS_DARK if is_dark else _CSS_VARS_LIGHT
    dark_overrides = _CSS_DARK_OVERRIDES if is_dark else ""

    st.markdown(f"""
    <style>
    {css_vars}
    {dark_overrides}
    {_CSS_RESPONSIVE}
    </style>
    """, unsafe_allow_html=True)

    # Dica de dark mode na sidebar
    try:
        getattr(st.context.theme, "type", "light")
    except Exception:
        st.sidebar.toggle("Modo Escuro", key="dark_mode")
    else:
        st.sidebar.caption("Modo escuro: Settings > Theme > Dark")
