"""
engine.py — Motor de Cálculo do Screener FCF Yield "Antigravity"

Metodologia:
  FCF = FCO (ou Adjusted_FCO) - Capex - Juros - Impostos - Arrendamentos
  Yield = (FCF / Market_Cap) * 100

Ajustes opcionais (Modo Conservador):
  - Adjusted_FCO = FCO - Variação do Capital de Giro
  - Se Capex > Depreciação * 1.5 → Capex = Depreciação (Ajuste de Expansão)
"""

import yfinance as yf
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _safe(df: pd.DataFrame, key: str) -> float:
    """Return the most recent non-NaN value from a yfinance statement row."""
    if key in df.index:
        row = df.loc[key]
        for val in row:
            if pd.notna(val) and val != 0:
                return float(val)
    return 0.0


def _safe_series(df: pd.DataFrame, key: str) -> pd.Series:
    """Return full row Series from a yfinance statement DataFrame (NaN kept)."""
    if key in df.index:
        return df.loc[key].astype(float)
    return pd.Series(dtype=float)


def _first_found(df: pd.DataFrame, *keys) -> float:
    """Try multiple keys in order, return the first non-zero value."""
    for k in keys:
        v = _safe(df, k)
        if v != 0:
            return v
    return 0.0


# ─────────────────────────────────────────────
# Revenue Growth (5 Years)
# ─────────────────────────────────────────────

def _revenue_growth_5y(ticker: yf.Ticker) -> float:
    """
    Calculate annualized revenue growth over the last ~4-5 available periods.
    Returns a decimal (e.g. 0.12 = 12%).
    """
    try:
        inc = ticker.income_stmt
        rev = _safe_series(inc, 'Total Revenue')
        if rev.empty:
            rev = _safe_series(inc, 'Revenue')

        # Drop NaN values — keeps only real data points
        rev = rev.dropna()
        rev = rev[rev > 0]

        if len(rev) < 2:
            return 0.0

        # yfinance columns are dates, most recent first
        latest = rev.iloc[0]
        oldest = rev.iloc[-1]  # last available (typically 4 periods back)
        n_years = len(rev) - 1

        if oldest <= 0 or latest <= 0 or n_years == 0:
            return 0.0

        cagr = (latest / oldest) ** (1 / n_years) - 1
        return cagr
    except Exception:
        return 0.0


# ─────────────────────────────────────────────
# Core Calculation
# ─────────────────────────────────────────────

def calculate_fcf(ticker_symbol: str, conservative: bool = False) -> dict | None:
    """
    Calculate FCF Yield for a single ticker.

    Args:
        ticker_symbol: e.g. 'AAPL' or 'PETR4.SA'
        conservative: If True, applies Working Capital adjustment
                      and Capex = Depreciation when Capex > 1.5× Depreciation.

    Returns:
        dict with all calculated metrics, or None on failure.
    """
    try:
        tk = yf.Ticker(ticker_symbol)
        info = tk.info

        # ── Statements ──────────────────────────
        cf = tk.cashflow
        inc = tk.income_stmt
        bs = tk.balance_sheet

        if cf.empty or inc.empty:
            return None

        # ── Step 1: FCO ─────────────────────────
        fco = _first_found(cf,
                           'Operating Cash Flow',
                           'Total Cash From Operating Activities',
                           'Cash Flow From Continuing Operating Activities')

        # ── Step 2: Adjusted FCO (Dica 2) ───────
        wc_change = _first_found(cf, 'Change In Working Capital')
        adjusted_fco = fco - wc_change if conservative else fco

        # ── Capex ───────────────────────────────
        capex_raw = _first_found(cf,
                                 'Capital Expenditure',
                                 'Capital Expenditures',
                                 'Purchase Of PPE')
        capex_raw = -abs(capex_raw) if capex_raw > 0 else capex_raw  # ensure negative

        # ── Depreciation ────────────────────────
        depreciation = _first_found(cf,
                                    'Depreciation Amortization Depletion',
                                    'Depreciation And Amortization')
        if depreciation == 0:
            depreciation = _first_found(inc,
                                        'Depreciation And Amortization',
                                        'Depreciation')

        # ── Step 4: Expansion Adjustment (Dica 1) ──
        capex_expansion_triggered = False
        capex = capex_raw
        if conservative and depreciation != 0:
            if abs(capex_raw) > abs(depreciation) * 1.5:
                capex = -abs(depreciation)        # Maintenance Capex only
                capex_expansion_triggered = True

        # ── Interest (Juros) ────────────────────
        interest = abs(_first_found(inc,
                                    'Interest Expense',
                                    'Interest Expense Non Operating'))
        if interest == 0:
            interest = abs(_first_found(cf,
                                        'Interest Paid Supplemental Data',
                                        'Interest Paid Cff'))

        # ── Taxes (Impostos) ────────────────────
        taxes = abs(_first_found(inc,
                                 'Tax Provision',
                                 'Income Tax Expense'))
        if taxes == 0:
            taxes = abs(_first_found(cf,
                                     'Income Tax Paid Supplemental Data',
                                     'Taxes Refund Paid'))

        # ── Leases (Arrendamentos) ──────────────
        leases = 0.0
        if not bs.empty:
            leases = abs(_first_found(bs,
                                      'Capital Lease Obligations',
                                      'Lease Liabilities'))
            if leases == 0:
                leases = abs(_safe(bs, 'Long Term Capital Lease Obligation')) \
                       + abs(_safe(bs, 'Current Capital Lease Obligation'))

        # ── Step 3: FCF ─────────────────────────
        fcf = adjusted_fco + capex - interest - taxes - leases

        # ── Market Cap ──────────────────────────
        market_cap = info.get('marketCap', 0)
        if not market_cap:
            shares = info.get('sharesOutstanding', 0)
            price = info.get('currentPrice', info.get('previousClose', 0))
            market_cap = shares * price if shares and price else 0

        # ── Step 5: Yield ───────────────────────
        fcf_yield = (fcf / market_cap) if market_cap else 0.0

        # ── Revenue Growth 5Y (Dica 3) ──────────
        rev_growth_5y = _revenue_growth_5y(tk)

        # ── Sector ──────────────────────────────
        sector = info.get('sector', 'Desconhecido')
        price = info.get('currentPrice', info.get('previousClose', 0))

        return {
            'Ticker': ticker_symbol,
            'Preço': price,
            'Market Cap': market_cap,
            'FCO': fco,
            'Adjusted FCO': adjusted_fco,
            'Capex': capex,
            'Capex (Raw)': capex_raw,
            'Depreciação': depreciation,
            'Ajuste Expansão': capex_expansion_triggered,
            'Juros': interest,
            'Impostos': taxes,
            'Arrendamentos': leases,
            'FCF': fcf,
            'FCF Yield': fcf_yield,
            'Rev Growth 5Y': rev_growth_5y,
            'Setor': sector,
        }

    except Exception as e:
        print(f"[engine] Erro ao processar {ticker_symbol}: {e}")
        return None


# ─────────────────────────────────────────────
# Classification
# ─────────────────────────────────────────────

COMMODITY_SECTORS = {'Energy', 'Basic Materials', 'Utilities'}

def classify_status(row: pd.Series) -> str:
    """
    Barato / Justo / Caro based on sector benchmarks.
    - Commodities (Energy, Basic Materials): ≥15 % → Barato
    - General:                                ≥10 % → Barato
    """
    y = row['FCF Yield']
    threshold = 0.15 if row['Setor'] in COMMODITY_SECTORS else 0.10

    if y >= threshold:
        return '🟢 Barato'
    elif y >= threshold * 0.7:
        return '🟡 Justo'
    else:
        return '🔴 Caro'


# ─────────────────────────────────────────────
# Batch Runner
# ─────────────────────────────────────────────

def run_screener(tickers: list[str],
                 conservative: bool = False) -> pd.DataFrame:
    """Run the screener for a list of tickers and return a sorted DataFrame."""
    results = []
    for t in tickers:
        row = calculate_fcf(t.strip(), conservative=conservative)
        if row is not None:
            results.append(row)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df['Status'] = df.apply(classify_status, axis=1)
    df.sort_values('FCF Yield', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
