"""
app.py — Screener FCF Yield "Antigravity"
Dashboard profissional para Streamlit Cloud.
Dados carregados de CSVs pré-gerados (atualizados diariamente via GitHub Actions).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from engine import run_screener, COMMODITY_SECTORS

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Screener FCF Yield · Antigravity",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# Data Paths
# ─────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
CSV_NORMAL = DATA_DIR / "screener_normal.csv"
CSV_CONSERVATIVE = DATA_DIR / "screener_conservative.csv"
METADATA_FILE = DATA_DIR / "metadata.json"

# ─────────────────────────────────────────
# Custom CSS — Premium Dark Theme
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hero Header ───────────────────── */
    .hero {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        color: #ffffff;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(124, 77, 255, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #fff 60%, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero .subtitle {
        margin: 0.6rem 0 0;
        font-size: 1.05rem;
        opacity: 0.7;
        font-weight: 300;
    }

    /* ── KPI Cards ─────────────────────── */
    .kpi-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: linear-gradient(145deg, #1e1e3f, #16213e);
        border: 1px solid rgba(124, 77, 255, 0.2);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        width: 100%;
    }
    .kpi-card .value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }
    .kpi-card .label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.6;
        margin-top: 0.4rem;
    }

    /* ── Clickable KPI styling ─────────── */
    /* Target buttons to look like card secondary actions */
    div[data-testid="stColumn"] .stButton button {
        background: rgba(124, 77, 255, 0.05) !important;
        border: 1px solid rgba(124, 77, 255, 0.2) !important;
        color: #fff !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        margin-top: -0.5rem;
    }
    div[data-testid="stColumn"] .stButton button:hover {
        border-color: #7c4dff !important;
        background: rgba(124, 77, 255, 0.1) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stColumn"] .stButton button:active {
        transform: scale(0.98);
    }

    /* ── Section Headers ───────────────── */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(124, 77, 255, 0.3);
        color: #fafafa;
    }

    /* ── Sidebar ───────────────────────── */
    section[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    }

    /* ── Table polish ──────────────────── */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Tab styling ───────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 600;
    }

    /* ── Data freshness badge ──────────── */
    .freshness {
        background: rgba(124, 77, 255, 0.1);
        border: 1px solid rgba(124, 77, 255, 0.3);
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 0.85rem;
        color: #aaa;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .freshness b {
        color: #7c4dff;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🚀 Screener FCF Yield</h1>
    <p class="subtitle">
        Value Investing de verdade — saindo do lucro contábil e focando no <b>caixa real</b>.
        Powered by <b>Antigravity Engine</b>.
    </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Load cached data
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_cached_data(csv_path: str) -> pd.DataFrame:
    """Load pre-generated CSV data. Returns empty DataFrame if file doesn't exist."""
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


def get_last_updated() -> str:
    """Read the last update timestamp from metadata."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE) as f:
                meta = json.load(f)
            dt = datetime.fromisoformat(meta.get("last_updated", ""))
            return dt.strftime("%d/%m/%Y às %H:%M UTC")
        except Exception:
            pass
    return "Desconhecido"


# ─────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚀 Antigravity")
    st.caption("Screener de Fluxo de Caixa Livre")
    st.markdown("---")

    # Conservative Mode
    st.subheader("⚙️ Modo de Análise")
    conservative = st.toggle(
        "Modo Conservador",
        value=False,
        help=(
            "**Ajuste de Capital de Giro**: Subtrai Δ Working Capital do FCO.\n\n"
            "**Ajuste de Expansão**: Se Capex > 1.5× Depreciação → Capex = Depreciação."
        ),
    )

    st.markdown("---")

    # Filter preference
    st.subheader("🎯 Filtro de Exibição")
    filter_options = ["Todos", "🟢 Apenas Baratos", "🔴 Apenas Caros", "🟡 Apenas Justos"]

    # Initialize session state for filter
    if "kpi_filter" not in st.session_state:
        st.session_state.kpi_filter = "Todos"

    view_filter = st.radio(
        "Exibir na tela:",
        filter_options,
        key="kpi_filter", # Single source of truth
    )

    st.markdown("---")

    # Market filter
    st.subheader("🌎 Mercado")
    market_filter = st.radio(
        "Exibir ativos de:",
        ["Todos", "🇧🇷 Apenas B3", "🇺🇸 Apenas NYSE/NASDAQ"],
        index=0,
    )

    st.markdown("---")

    # Manual refresh button
    st.subheader("🔄 Atualizar Dados")
    refresh_btn = st.button(
        "🔄 Atualizar Dados Agora",
        use_container_width=True,
        type="primary",
        help="Busca dados atualizados do Yahoo Finance para todos os ativos."
    )
    st.caption(f"📅 Última atualização: **{get_last_updated()}**")
    st.info(
        "💡 Os dados são atualizados **automaticamente a cada 24 horas** "
        "(às 03:00 BRT via GitHub Actions).\n\n"
        "Use o botão acima apenas se precisar de dados em tempo real.",
        icon="ℹ️"
    )

# ─────────────────────────────────────────
# Load Data (from CSV or live refresh)
# ─────────────────────────────────────────
csv_path = str(CSV_CONSERVATIVE if conservative else CSV_NORMAL)

if refresh_btn:
    # ── Live refresh from Yahoo Finance ──
    from update_data import ALL_TICKERS
    st.cache_data.clear()

    progress_bar = st.progress(0, text="⏳ Conectando ao Yahoo Finance...")
    status_text = st.empty()
    total = len(ALL_TICKERS)

    def update_progress(current, total_count):
        pct = current / total_count
        progress_bar.progress(pct, text=f"⏳ Processando {current}/{total_count} ativos...")

    # Fetch data for the selected mode
    status_text.info(f"🔄 Buscando dados {'(Modo Conservador)' if conservative else '(Modo Normal)'}...")
    df = run_screener(ALL_TICKERS, conservative=conservative, progress_callback=update_progress)

    if not df.empty:
        # Save to CSV
        os.makedirs(str(DATA_DIR), exist_ok=True)
        df.to_csv(csv_path, index=False)

        # Also fetch the other mode
        other_conservative = not conservative
        other_csv = str(CSV_CONSERVATIVE if other_conservative else CSV_NORMAL)
        status_text.info(f"🔄 Buscando dados {'(Modo Conservador)' if other_conservative else '(Modo Normal)'}...")
        progress_bar.progress(0, text="⏳ Buscando segundo modo...")
        df_other = run_screener(ALL_TICKERS, conservative=other_conservative, progress_callback=update_progress)
        if not df_other.empty:
            df_other.to_csv(other_csv, index=False)

        # Update metadata
        now = datetime.now(timezone.utc)
        meta = {
            "last_updated": now.isoformat(),
            "tickers_total": len(ALL_TICKERS),
            "tickers_normal_ok": len(df) if not conservative else len(df_other) if not df_other.empty else 0,
            "tickers_conservative_ok": len(df) if conservative else len(df_other) if not df_other.empty else 0,
        }
        pd.Series(meta).to_json(str(METADATA_FILE))

        progress_bar.empty()
        status_text.success(f"✅ Dados atualizados! {len(df)} ativos processados.")
    else:
        progress_bar.empty()
        status_text.error("❌ Erro ao buscar dados. Tente novamente em alguns minutos.")
        st.stop()
else:
    # ── Load from cached CSV ──
    df = load_cached_data(csv_path)

    if df.empty:
        st.error(
            "❌ Dados ainda não disponíveis.\n\n"
            "Clique em **🔄 Atualizar Dados Agora** na barra lateral para buscar os dados."
        )
        st.stop()

# Show data freshness
last_updated = get_last_updated()
st.markdown(f'<div class="freshness">📅 Dados de: <b>{last_updated}</b> · {len(df)} ativos analisados · Atualização automática a cada 24h</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# Methodology (collapsible)
# ─────────────────────────────────────────
with st.expander("📐 Metodologia — Como o FCF Yield é calculado?", expanded=False):
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
**Fórmula:**
```
FCF = FCO − Capex − Juros − Impostos − Arrendamentos
Yield = FCF ÷ Market Cap
```

**Modo Conservador:**
- FCO ajustado (remove variação do Capital de Giro)
- Capex limitado à Depreciação se > 1.5× Deprec.
        """)
    with col_m2:
        st.markdown("""
**Benchmarks de Status:**

| Tipo | Yield para "Barato" |
|------|-------------------|
| Geral | ≥ 10% |
| Commodities | ≥ 15% |

> Diferente de P/L ou EV/EBITDA, o FCF Yield usa **caixa real** — imune a manobras contábeis.
        """)

# ─────────────────────────────────────────
# Apply Market Filter
# ─────────────────────────────────────────
if market_filter == "🇧🇷 Apenas B3":
    df = df[df['Ticker'].str.endswith('.SA')].copy()
elif market_filter == "🇺🇸 Apenas NYSE/NASDAQ":
    df = df[~df['Ticker'].str.endswith('.SA')].copy()

if df.empty:
    st.info("Nenhum ativo encontrado para esse mercado.")
    st.stop()

# ─────────────────────────────────────────
# Apply View Filter + Smart Sorting
# ─────────────────────────────────────────
# Baratos → do mais barato (maior yield) ao menos barato
# Caros   → do mais caro (menor yield) ao menos caro
# Justos  → yield descendente
# Todos   → yield descendente
if view_filter == "🟢 Apenas Baratos":
    filtered = df[df['Status'].str.contains('Barato')].copy()
    filtered.sort_values('FCF Yield', ascending=False, inplace=True)
elif view_filter == "🔴 Apenas Caros":
    filtered = df[df['Status'].str.contains('Caro')].copy()
    filtered.sort_values('FCF Yield', ascending=True, inplace=True)
elif view_filter == "🟡 Apenas Justos":
    filtered = df[df['Status'].str.contains('Justo')].copy()
    filtered.sort_values('FCF Yield', ascending=False, inplace=True)
else:
    filtered = df.copy()
    filtered.sort_values('FCF Yield', ascending=False, inplace=True)

filtered.reset_index(drop=True, inplace=True)

if filtered.empty:
    st.info(f"Nenhum ativo encontrado com o filtro '{view_filter}'.")
    st.stop()

# ─────────────────────────────────────────
# KPI Cards (Interactive)
# ─────────────────────────────────────────
n_total = len(df)
n_cheap = int(df['Status'].str.contains('Barato').sum())
n_fair = int(df['Status'].str.contains('Justo').sum())
n_expensive = int(df['Status'].str.contains('Caro').sum())
best_idx = df['FCF Yield'].idxmax()
best = df.loc[best_idx]

# Layout for KPI cards
k1, k2, k3, k4, k5 = st.columns(5)

# Helper to avoid repetitive HTML
def kpi_box(col, val, label, color="#7c4dff"):
    col.markdown(f"""
    <div class="kpi-card">
        <p class="value" style="color: {color}">{val}</p>
        <p class="label">{label}</p>
    </div>
    """, unsafe_allow_html=True)

kpi_box(k1, n_total, "Analisados")
if k1.button("🔍 Ver Tudo", key=f"btn_all_{n_total}", use_container_width=True):
    st.session_state.kpi_filter = "Todos"
    st.rerun()

kpi_box(k2, n_cheap, "🟢 Baratos", "#00e676")
if k2.button("🟢 Filtrar", key=f"btn_cheap_{n_cheap}", use_container_width=True):
    st.session_state.kpi_filter = "🟢 Apenas Baratos"
    st.rerun()

kpi_box(k3, n_fair, "🟡 Justos", "#ffab00")
if k3.button("🟡 Filtrar", key=f"btn_fair_{n_fair}", use_container_width=True):
    st.session_state.kpi_filter = "🟡 Apenas Justos"
    st.rerun()

kpi_box(k4, n_expensive, "🔴 Caros", "#ff1744")
if k4.button("🔴 Filtrar", key=f"btn_exp_{n_expensive}", use_container_width=True):
    st.session_state.kpi_filter = "🔴 Apenas Caros"
    st.rerun()

kpi_box(k5, best['Ticker'], f"🏆 Maior Yield ({best['FCF Yield']:.1%})")
if k5.button("🎯 Ver Ativo", key="btn_top", use_container_width=True):
    st.session_state.kpi_filter = "Todos"
    # We could add an asset-specific filter here if requested
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Main Content Tabs
# ─────────────────────────────────────────
tab_table, tab_chart, tab_detail = st.tabs(["📋 Ranking", "📊 Gráfico de Bolhas", "🔍 Breakdown"])

# ── Tab 1: Table ─────────────────────
with tab_table:
    st.markdown(f'<div class="section-title">Ranking por FCF Yield — {view_filter}</div>', unsafe_allow_html=True)

    # Sector sub-filter
    available_sectors = sorted(filtered['Setor'].dropna().unique())
    if len(available_sectors) > 1:
        selected_sectors = st.multiselect(
            "Filtrar por Setor:",
            available_sectors,
            default=available_sectors,
            key="sector_filter"
        )
        table_df = filtered[filtered['Setor'].isin(selected_sectors)].copy()
    else:
        table_df = filtered.copy()

    # Columns to display
    display_cols = ['Ticker', 'Preço', 'FCF Yield', 'Status',
                    'Rev Growth 5Y', 'Setor', 'Market Cap', 'FCF']
    if 'Ajuste Expansão' in table_df.columns:
        display_cols.append('Ajuste Expansão')

    display = table_df[[c for c in display_cols if c in table_df.columns]].copy()

    # Format
    def fmt_pct(v):
        try:
            return f"{float(v):.2%}" if pd.notna(v) else "–"
        except (ValueError, TypeError):
            return "–"

    def fmt_brl(v):
        try:
            v = float(v)
            if pd.isna(v) or v == 0:
                return "–"
            return f"{v/1e9:,.2f} B"
        except (ValueError, TypeError):
            return "–"

    display['FCF Yield'] = table_df['FCF Yield'].map(fmt_pct)
    display['Rev Growth 5Y'] = table_df['Rev Growth 5Y'].map(fmt_pct)
    display['Market Cap'] = table_df['Market Cap'].map(fmt_brl)
    display['FCF'] = table_df['FCF'].map(fmt_brl)
    display['Preço'] = table_df['Preço'].map(lambda v: f"{v:,.2f}" if pd.notna(v) and v else "–")
    if 'Ajuste Expansão' in display.columns:
        display['Ajuste Expansão'] = display['Ajuste Expansão'].map(
            lambda v: "⚠️ Sim" if v is True or v == "True" else "–"
        )

    col_config = {
        "Ticker": st.column_config.TextColumn("Ativo", width="small"),
        "Preço": st.column_config.TextColumn("Preço", width="small"),
        "FCF Yield": st.column_config.TextColumn("FCF Yield", width="small"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "Rev Growth 5Y": st.column_config.TextColumn("Cresc. Receita 5A", width="small"),
        "Setor": st.column_config.TextColumn("Setor", width="medium"),
        "Market Cap": st.column_config.TextColumn("Market Cap", width="small"),
        "FCF": st.column_config.TextColumn("FCF", width="small"),
    }
    if 'Ajuste Expansão' in display.columns:
        col_config["Ajuste Expansão"] = st.column_config.TextColumn("Ajuste Capex", width="small")

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=min(700, 35 * len(display) + 38),
        column_config=col_config,
    )

    st.caption(f"Exibindo {len(display)} de {n_total} ativos · Dados atualizados diariamente")

# ── Tab 2: Bubble Chart ─────────────
with tab_chart:
    st.markdown('<div class="section-title">Joias de Crescimento — FCF Yield vs Receita 5Y</div>', unsafe_allow_html=True)

    chart_df = filtered.copy()
    chart_df['Yield %'] = chart_df['FCF Yield'] * 100
    chart_df['Rev Growth %'] = chart_df['Rev Growth 5Y'] * 100
    chart_df['MCap B'] = (chart_df['Market Cap'] / 1e9).clip(lower=1)

    fig = px.scatter(
        chart_df,
        x='Yield %',
        y='Rev Growth %',
        size='MCap B',
        color='Status',
        hover_name='Ticker',
        hover_data={
            'Yield %': ':.2f',
            'Rev Growth %': ':.2f',
            'MCap B': ':.1f',
            'Setor': True,
            'Status': False,
        },
        color_discrete_map={
            '🟢 Barato': '#00e676',
            '🟡 Justo': '#ffab00',
            '🔴 Caro': '#ff1744',
        },
        size_max=60,
        template='plotly_dark',
    )

    fig.add_vline(x=10, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                  annotation_text="10%", annotation_font_color="rgba(255,255,255,0.5)")
    fig.add_vline(x=15, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                  annotation_text="15%", annotation_font_color="rgba(255,255,255,0.5)")
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.1)")

    fig.update_layout(
        xaxis_title="FCF Yield (%)",
        yaxis_title="Crescimento Receita 5A (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={"family": "Inter", "size": 13, "color": "#ccc"},
        legend_title_text="",
        height=550,
        margin={"l": 50, "r": 30, "t": 30, "b": 50},
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "💡 **Dica:** Procure ativos no **quadrante superior-direito** — alto Yield **e** alta receita crescendo. "
        "São as verdadeiras 'Joias de Crescimento'."
    )

# ── Tab 3: Detailed Breakdown ───────
with tab_detail:
    st.markdown('<div class="section-title">Breakdown dos Componentes do FCF</div>', unsafe_allow_html=True)

    detail_cols = ['Ticker', 'FCO', 'Adjusted FCO', 'Capex', 'Capex (Raw)',
                   'Depreciação', 'Juros', 'Impostos', 'Arrendamentos', 'FCF']
    available_detail = [c for c in detail_cols if c in filtered.columns]
    detail = filtered[available_detail].copy()

    for col in detail.columns:
        if col == 'Ticker':
            continue
        detail[col] = detail[col].map(
            lambda v: f"{float(v)/1e6:,.0f} M" if pd.notna(v) and float(v) != 0 else "–"
        )

    st.dataframe(detail, use_container_width=True, hide_index=True)

    st.caption("Valores em milhões (M) na moeda local do ativo.")

# ─────────────────────────────────────────
# Footer
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; opacity:0.4; font-size:0.8rem; padding: 1rem 0">
    <b>Screener FCF Yield "Antigravity"</b> · Dados via Yahoo Finance (atualização diária) · 
    <a href="https://github.com/julianimmj/screener-fcf-yield" target="_blank" style="color:#7c4dff">github.com/julianimmj</a><br>
    Metodologia: (FCO − Capex − Juros − Impostos − Leases) ÷ Market Cap
</div>
""", unsafe_allow_html=True)
