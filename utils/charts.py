"""
Componentes de gráficos usando Charts.css (CSS puro, sem JavaScript).
https://chartscss.org/
"""

import streamlit as st


def _inject_chartscss():
    """Injeta o CSS do Charts.css via CDN uma única vez por sessão."""
    if not st.session_state.get("_chartscss_injected"):
        st.markdown(
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/charts.css/dist/charts.min.css">',
            unsafe_allow_html=True,
        )
        st.session_state["_chartscss_injected"] = True


def _chart_custom_css():
    """CSS customizado para integrar Charts.css com o tema do app."""
    return """
<style>
/* Charts.css - integração com tema */
.charts-css {
    --color-1: var(--chartscss-color-1, #1E88E5);
    --color-2: var(--chartscss-color-2, #43A047);
    --color-3: var(--chartscss-color-3, #dc3545);
    --color-4: var(--chartscss-color-4, #ffc107);
    --color-5: var(--chartscss-color-5, #6c757d);
    margin: 0 auto;
    border: none !important;
}

.charts-css caption {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary) !important;
    caption-side: top;
    text-align: center;
    padding: 0.5rem 0;
}

.charts-css tbody tr {
    border: none !important;
}

.charts-css td {
    border: none !important;
    border-radius: 4px 4px 0 0;
}

.charts-css.bar td {
    border-radius: 0 4px 4px 0;
}

/* Labels */
.charts-css th {
    color: var(--text-secondary) !important;
    font-size: 0.8rem;
    font-weight: 500;
    white-space: nowrap;
}

/* Valores sobre as barras */
.charts-css .data {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary) !important;
}

/* Coluna: valor acima da barra */
.charts-css.column .data {
    position: absolute;
    top: -1.5rem;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
}

/* Barra horizontal: valor à direita */
.charts-css.bar .data {
    position: absolute;
    right: -3rem;
    top: 50%;
    transform: translateY(-50%);
    white-space: nowrap;
}

/* Eixos */
.charts-css.show-data-axes {
    --data-axes-color: var(--divider-line, #E0E0E0);
}

/* Wrapper */
.chartscss-wrapper {
    padding: 0.5rem 0;
}

/* Legenda */
.chartscss-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    padding: 0.5rem 0;
}

.chartscss-legend-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.82rem;
    color: var(--text-secondary);
}

.chartscss-legend-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    display: inline-block;
}

/* Responsividade */
@media (max-width: 768px) {
    .charts-css th {
        font-size: 0.7rem;
    }
    .charts-css .data {
        font-size: 0.75rem;
    }
    .charts-css.column .data {
        top: -1.2rem;
    }
}
</style>
"""


def chartscss_column(data, title="", show_labels=True, show_values=True,
                     height="250px", colors=None):
    """
    Gráfico de colunas verticais com Charts.css.

    Args:
        data: dict {label: valor} ex: {"Aprovados": 10, "Sem Vaga": 5}
        title: título do gráfico
        show_labels: mostrar labels embaixo das colunas
        show_values: mostrar valores sobre as colunas
        height: altura do gráfico
        colors: lista de cores hex (uma por coluna), ou None para cores padrão
    """
    _inject_chartscss()

    if not data:
        st.info("Sem dados para exibir.")
        return

    max_val = max(data.values()) if data.values() else 1
    if max_val == 0:
        max_val = 1

    classes = ["charts-css", "column", "show-data-axes"]
    if show_labels:
        classes.append("show-labels")

    rows = []
    for i, (label, value) in enumerate(data.items()):
        size = value / max_val
        color_style = ""
        if colors and i < len(colors):
            color_style = f"background-color: {colors[i]}; opacity: 0.85;"

        data_span = f'<span class="data">{value}</span>' if show_values else ""
        rows.append(
            f'<tr>'
            f'<th scope="row">{label}</th>'
            f'<td style="--size: {size:.4f}; {color_style}">{data_span}</td>'
            f'</tr>'
        )

    caption = f"<caption>{title}</caption>" if title else ""

    html = f"""
{_chart_custom_css()}
<div class="chartscss-wrapper">
<table class="{' '.join(classes)}" style="height: {height}; max-width: 400px; margin: 0 auto;">
{caption}
<tbody>
{''.join(rows)}
</tbody>
</table>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def chartscss_bar(data, title="", show_labels=True, show_values=True,
                  height=None, colors=None):
    """
    Gráfico de barras horizontais com Charts.css.

    Args:
        data: dict {label: valor}
        title: título do gráfico
        show_labels: mostrar labels à esquerda
        show_values: mostrar valores à direita das barras
        height: altura do gráfico (auto-calculada se None)
        colors: lista de cores hex, ou None
    """
    _inject_chartscss()

    if not data:
        st.info("Sem dados para exibir.")
        return

    max_val = max(data.values()) if data.values() else 1
    if max_val == 0:
        max_val = 1

    if height is None:
        height = f"{max(len(data) * 50, 150)}px"

    classes = ["charts-css", "bar", "show-data-axes"]
    if show_labels:
        classes.append("show-labels")

    rows = []
    for i, (label, value) in enumerate(data.items()):
        size = value / max_val
        color_style = ""
        if colors and i < len(colors):
            color_style = f"background-color: {colors[i]}; opacity: 0.85;"

        data_span = f'<span class="data">{value}</span>' if show_values else ""
        rows.append(
            f'<tr>'
            f'<th scope="row">{label}</th>'
            f'<td style="--size: {size:.4f}; {color_style}">{data_span}</td>'
            f'</tr>'
        )

    caption = f"<caption>{title}</caption>" if title else ""

    html = f"""
{_chart_custom_css()}
<div class="chartscss-wrapper">
<table class="{' '.join(classes)}" style="height: {height}; max-width: 500px; margin: 0 auto;">
{caption}
<tbody>
{''.join(rows)}
</tbody>
</table>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def chartscss_legend(items):
    """
    Legenda para acompanhar gráficos.

    Args:
        items: lista de dicts {label: str, color: str}
    """
    spans = []
    for item in items:
        spans.append(
            f'<span class="chartscss-legend-item">'
            f'<span class="chartscss-legend-color" style="background-color: {item["color"]};"></span>'
            f'{item["label"]}'
            f'</span>'
        )

    html = f'<div class="chartscss-legend">{"".join(spans)}</div>'
    st.markdown(html, unsafe_allow_html=True)
