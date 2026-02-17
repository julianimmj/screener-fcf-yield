"""
app.py — Screener FCF Yield "Antigravity"
Dashboard profissional para Streamlit Cloud.
Dados carregados automaticamente com cache.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
# Default Watchlists
# ─────────────────────────────────────────
WATCHLIST_BR = [
    # Ibovespa — Blue Chips
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA",
    "ABEV3.SA", "WEGE3.SA", "RENT3.SA", "SUZB3.SA", "JBSS3.SA",
    "GGBR4.SA", "CSNA3.SA", "CMIG4.SA", "ELET3.SA", "RADL3.SA",
    "VIVT3.SA", "MGLU3.SA", "LREN3.SA", "CSAN3.SA", "BPAC11.SA",
    # Ibovespa — Mid & Large Caps
    "B3SA3.SA", "HAPV3.SA", "RDOR3.SA", "RAIL3.SA", "SBSP3.SA",
    "ENEV3.SA", "TOTS3.SA", "PRIO3.SA", "RRRP3.SA", "VBBR3.SA",
    "KLBN11.SA", "UGPA3.SA", "CCRO3.SA", "EQTL3.SA", "CPFE3.SA",
    "CPLE6.SA", "TAEE11.SA", "ENBR3.SA", "CYRE3.SA", "MRVE3.SA",
    # Financeiro
    "SANB11.SA", "BRSR6.SA", "ABCB4.SA", "BMGB4.SA", "ITSA4.SA",
    "BBSE3.SA", "SULA11.SA", "PSSA3.SA", "IRBR3.SA", "CXSE3.SA",
    # Consumo & Varejo
    "PETZ3.SA", "AMER3.SA", "SOMA3.SA", "GRND3.SA", "ALPA4.SA",
    "CRFB3.SA", "ASAI3.SA", "MDIA3.SA", "NTCO3.SA", "HYPE3.SA",
    # Indústria & Energia
    "GOAU4.SA", "USIM5.SA", "BRKM5.SA", "UNIP6.SA", "FESA4.SA",
    "AURE3.SA", "CSMG3.SA", "SAPR11.SA", "TRPL4.SA", "TIMS3.SA",
    # Imobiliário & Construção
    "EZTC3.SA", "DIRR3.SA", "EVEN3.SA", "TEND3.SA", "JHSF3.SA",
    "MULT3.SA", "IGTI11.SA", "BRML3.SA", "ALSO3.SA", "SMAL11.SA",
    # Tecnologia & Saúde
    "LWSA3.SA", "CASH3.SA", "BMOB3.SA", "POSI3.SA", "INTB3.SA",
    "FLRY3.SA", "DASA3.SA", "MATD3.SA", "QUAL3.SA", "ODPV3.SA",
    # Logística & Transporte
    "AZUL4.SA", "GOLL4.SA", "EMBR3.SA", "STBP3.SA", "HBSA3.SA",
    "MOVI3.SA", "VAMO3.SA", "SIMH3.SA", "SMTO3.SA", "SLCE3.SA",
]

WATCHLIST_US = [
    # Mega Caps — Tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "NVDA", "TSLA", "AVGO", "ORCL", "CRM",
    "ADBE", "AMD", "INTC", "QCOM", "TXN",
    "IBM", "NOW", "INTU", "AMAT", "MU",
    # Finance
    "JPM", "BAC", "WFC", "GS", "MS",
    "C", "BLK", "SCHW", "AXP", "USB",
    "V", "MA", "PYPL", "SQ", "FIS",
    # Healthcare
    "UNH", "JNJ", "PFE", "ABBV", "MRK",
    "LLY", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "ISRG", "MDT", "CI",
    # Consumer
    "PG", "KO", "PEP", "COST", "WMT",
    "MCD", "NKE", "SBUX", "TGT", "LOW",
    "HD", "DIS", "NFLX", "CMCSA", "BKNG",
    # Energy & Materials
    "XOM", "CVX", "COP", "SLB", "EOG",
    "PSX", "VLO", "MPC", "LIN", "APD",
    "FCX", "NEM", "DOW", "DD", "PPG",
    # Industrials
    "CAT", "DE", "HON", "UPS", "RTX",
    "LMT", "BA", "GE", "MMM", "EMR",
    "FDX", "WM", "CSX", "NSC", "UNP",
    # REITs & Utilities
    "AMT", "PLD", "CCI", "EQIX", "PSA",
    "NEE", "DUK", "SO", "D", "AEP",
]

WATCHLIST_FULL = WATCHLIST_BR + WATCHLIST_US

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
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        flex: 1;
        background: linear-gradient(145deg, #1e1e3f, #16213e);
        border: 1px solid rgba(124, 77, 255, 0.2);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(124, 77, 255, 0.5);
    }
    .kpi-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #7c4dff;
        margin: 0;
    }
    .kpi-card .label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.5;
        margin: 0.3rem 0 0;
        color: #ccc;
    }

    /* ── Status Badges ─────────────────── */
    .badge-barato {
        background: rgba(0, 230, 118, 0.15);
        color: #00e676;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-justo {
        background: rgba(255, 171, 0, 0.15);
        color: #ffab00;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-caro {
        background: rgba(255, 23, 68, 0.15);
        color: #ff1744;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
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
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚀 Antigravity")
    st.caption("Screener de Fluxo de Caixa Livre")
    st.markdown("---")

    # Watchlist Selection
    st.subheader("📋 Watchlist")
    watchlist_option = st.radio(
        "Escolha a lista de ativos:",
        ["🇧🇷 B3 (Ibovespa)", "🇺🇸 NYSE/NASDAQ", "🌎 Completa (BR + US)", "✏️ Personalizada"],
        index=2,
    )

    if watchlist_option == "🇧🇷 B3 (Ibovespa)":
        selected_tickers = WATCHLIST_BR
    elif watchlist_option == "🇺🇸 NYSE/NASDAQ":
        selected_tickers = WATCHLIST_US
    elif watchlist_option == "🌎 Completa (BR + US)":
        selected_tickers = WATCHLIST_FULL
    else:
        custom_input = st.text_area(
            "Tickers (vírgula):",
            value=", ".join(WATCHLIST_FULL),
            height=120,
        )
        selected_tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]

    st.markdown("---")

    # Conservative Mode
    st.subheader("⚙️ Ajustes")
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
    view_filter = st.radio(
        "Exibir na tela:",
        ["Todos", "🟢 Apenas Baratos", "🔴 Apenas Caros", "🟡 Apenas Justos"],
        index=0,
    )

    st.markdown("---")
    run_btn = st.button("🚀 Atualizar Dados", use_container_width=True, type="primary")

# ─────────────────────────────────────────
# Cached Data Fetching
# ─────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def fetch_data(tickers_tuple, conservative_mode):
    """Fetch and cache screener data."""
    return run_screener(list(tickers_tuple), conservative=conservative_mode)


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
# Load Data (auto on first visit, or on button click)
# ─────────────────────────────────────────
tickers_key = tuple(sorted(selected_tickers))

# Auto-load on page visit (cached), or force refresh on button
if run_btn:
    st.cache_data.clear()

with st.spinner(f"⏳ Analisando {len(selected_tickers)} ativos via Yahoo Finance… (dados serão cacheados por 1h)"):
    df = fetch_data(tickers_key, conservative)

if df.empty:
    st.error("❌ Não foi possível obter dados. Verifique os tickers e tente novamente.")
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
# KPI Cards
# ─────────────────────────────────────────
n_total = len(df)
n_cheap = df['Status'].str.contains('Barato').sum()
n_fair = df['Status'].str.contains('Justo').sum()
n_expensive = df['Status'].str.contains('Caro').sum()
best = df.iloc[0]  # Already sorted by yield desc

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <p class="value">{n_total}</p>
        <p class="label">Ativos Analisados</p>
    </div>
    <div class="kpi-card">
        <p class="value" style="color: #00e676">{n_cheap}</p>
        <p class="label">🟢 Baratos</p>
    </div>
    <div class="kpi-card">
        <p class="value" style="color: #ffab00">{n_fair}</p>
        <p class="label">🟡 Justos</p>
    </div>
    <div class="kpi-card">
        <p class="value" style="color: #ff1744">{n_expensive}</p>
        <p class="label">🔴 Caros</p>
    </div>
    <div class="kpi-card">
        <p class="value" style="font-size:1.4rem">{best['Ticker']}</p>
        <p class="label">Maior Yield ({best['FCF Yield']:.1%})</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Main Content Tabs
# ─────────────────────────────────────────
tab_table, tab_chart, tab_detail = st.tabs(["📋 Ranking", "📊 Gráfico de Bolhas", "🔍 Breakdown"])

# ── Tab 1: Table ─────────────────────
with tab_table:
    st.markdown(f'<div class="section-title">Ranking por FCF Yield — {view_filter}</div>', unsafe_allow_html=True)

    # Sector sub-filter
    available_sectors = sorted(filtered['Setor'].unique())
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

    display = table_df[[
        'Ticker', 'Preço', 'FCF Yield', 'Status',
        'Rev Growth 5Y', 'Setor', 'Market Cap', 'FCF',
        'Ajuste Expansão',
    ]].copy()

    # Format
    def fmt_pct(v):
        return f"{v:.2%}" if pd.notna(v) else "–"

    def fmt_brl(v):
        if pd.isna(v) or v == 0:
            return "–"
        return f"{v/1e9:,.2f} B"

    display['FCF Yield'] = table_df['FCF Yield'].map(fmt_pct)
    display['Rev Growth 5Y'] = table_df['Rev Growth 5Y'].map(fmt_pct)
    display['Market Cap'] = table_df['Market Cap'].map(fmt_brl)
    display['FCF'] = table_df['FCF'].map(fmt_brl)
    display['Preço'] = table_df['Preço'].map(lambda v: f"{v:,.2f}" if v else "–")
    display['Ajuste Expansão'] = display['Ajuste Expansão'].map(
        lambda v: "⚠️ Sim" if v else "–"
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=min(600, 35 * len(display) + 38),
        column_config={
            "Ticker": st.column_config.TextColumn("Ativo", width="small"),
            "Preço": st.column_config.TextColumn("Preço", width="small"),
            "FCF Yield": st.column_config.TextColumn("FCF Yield", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Rev Growth 5Y": st.column_config.TextColumn("Cresc. Receita 5A", width="small"),
            "Setor": st.column_config.TextColumn("Setor", width="medium"),
            "Market Cap": st.column_config.TextColumn("Market Cap", width="small"),
            "FCF": st.column_config.TextColumn("FCF", width="small"),
            "Ajuste Expansão": st.column_config.TextColumn("Ajuste Capex", width="small"),
        },
    )

    st.caption(f"Exibindo {len(display)} de {n_total} ativos · Dados cacheados por 1h")

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
        font=dict(family="Inter", size=13, color="#ccc"),
        legend_title_text="",
        height=550,
        margin=dict(l=50, r=30, t=30, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "💡 **Dica:** Procure ativos no **quadrante superior-direito** — alto Yield **e** alta receita crescendo. "
        "São as verdadeiras 'Joias de Crescimento'."
    )

# ── Tab 3: Detailed Breakdown ───────
with tab_detail:
    st.markdown('<div class="section-title">Breakdown dos Componentes do FCF</div>', unsafe_allow_html=True)

    detail = filtered[[
        'Ticker', 'FCO', 'Adjusted FCO', 'Capex', 'Capex (Raw)',
        'Depreciação', 'Juros', 'Impostos', 'Arrendamentos', 'FCF',
    ]].copy()

    for col in detail.columns:
        if col == 'Ticker':
            continue
        detail[col] = detail[col].map(lambda v: f"{v/1e6:,.0f} M" if pd.notna(v) and v != 0 else "–")

    st.dataframe(detail, use_container_width=True, hide_index=True)

    st.caption("Valores em milhões (M) na moeda local do ativo.")

# ─────────────────────────────────────────
# Footer
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; opacity:0.4; font-size:0.8rem; padding: 1rem 0">
    <b>Screener FCF Yield "Antigravity"</b> · Dados via Yahoo Finance · 
    <a href="https://github.com/julianimmj" target="_blank" style="color:#7c4dff">github.com/julianimmj</a><br>
    Metodologia: (FCO − Capex − Juros − Impostos − Leases) ÷ Market Cap
</div>
""", unsafe_allow_html=True)
