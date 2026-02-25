"""
update_data.py — Daily data fetcher for Screener FCF Yield "Antigravity"

Runs via GitHub Actions every day at 06:00 UTC.
Fetches all tickers, calculates FCF Yield (normal + conservative),
and saves the results to data/screener_normal.csv and data/screener_conservative.csv.

The Streamlit app reads from these CSVs — zero API calls at runtime.
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import calculate_fcf, classify_status, _calculate_with_retry

# ─────────────────────────────────────────────
# All 200 Tickers
# ─────────────────────────────────────────────
TICKERS_BR = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA",
    "ABEV3.SA", "WEGE3.SA", "RENT3.SA", "SUZB3.SA",
    "GGBR4.SA", "CSNA3.SA", "CMIG4.SA", "AXIA3.SA", "RADL3.SA",
    "VIVT3.SA", "MGLU3.SA", "LREN3.SA", "CSAN3.SA", "BPAC11.SA",
    "B3SA3.SA", "HAPV3.SA", "RDOR3.SA", "RAIL3.SA", "SBSP3.SA",
    "ENEV3.SA", "TOTS3.SA", "PRIO3.SA", "RRRP3.SA", "VBBR3.SA",
    "KLBN11.SA", "UGPA3.SA", "MOTV3.SA", "EQTL3.SA", "CPFE3.SA",
    "CPLE6.SA", "TAEE11.SA", "ENBR3.SA", "CYRE3.SA", "MRVE3.SA",
    "SANB11.SA", "BRSR6.SA", "ABCB4.SA", "BMGB4.SA", "ITSA4.SA",
    "BBSE3.SA", "SULA11.SA", "PSSA3.SA", "IRBR3.SA", "CXSE3.SA",
    "AUAU3.SA", "AMER3.SA", "SOMA3.SA", "GRND3.SA", "ALPA4.SA",
    "ASAI3.SA", "MDIA3.SA", "NATU3.SA", "HYPE3.SA",
    "GOAU4.SA", "USIM5.SA", "BRKM5.SA", "UNIP6.SA", "FESA4.SA",
    "AURE3.SA", "CSMG3.SA", "SAPR11.SA", "TRPL4.SA", "TIMS3.SA",
    "EZTC3.SA", "DIRR3.SA", "EVEN3.SA", "TEND3.SA", "JHSF3.SA",
    "MULT3.SA", "IGTI11.SA", "ALSO3.SA", "SMAL11.SA",
    "LWSA3.SA", "CASH3.SA", "BMOB3.SA", "POSI3.SA", "INTB3.SA",
    "FLRY3.SA", "DASA3.SA", "MATD3.SA", "QUAL3.SA", "ODPV3.SA",
    "AZUL4.SA", "EMBJ3.SA", "HBSA3.SA",
    "MOVI3.SA", "VAMO3.SA", "SIMH3.SA", "SMTO3.SA", "SLCE3.SA",
    # Adicionados
    "BRFS3.SA", "MRFG3.SA", "BEEF3.SA", "VIIA3.SA",
    "COGN3.SA", "YDUQ3.SA", "ECOR3.SA", "EGIE3.SA", "PETR3.SA",
]

TICKERS_US = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "NVDA", "TSLA", "AVGO", "ORCL", "CRM",
    "ADBE", "AMD", "INTC", "QCOM", "TXN",
    "IBM", "NOW", "INTU", "AMAT", "MU",
    "JPM", "BAC", "WFC", "GS", "MS",
    "C", "BLK", "SCHW", "AXP", "USB",
    "V", "MA", "PYPL", "SQ", "FIS",
    "UNH", "JNJ", "PFE", "ABBV", "MRK",
    "LLY", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "ISRG", "MDT", "CI",
    "PG", "KO", "PEP", "COST", "WMT",
    "MCD", "NKE", "SBUX", "TGT", "LOW",
    "HD", "DIS", "NFLX", "CMCSA", "BKNG",
    "XOM", "CVX", "COP", "SLB", "EOG",
    "PSX", "VLO", "MPC", "LIN", "APD",
    "FCX", "NEM", "DOW", "DD", "PPG",
    "CAT", "DE", "HON", "UPS", "RTX",
    "LMT", "BA", "GE", "MMM", "EMR",
    "FDX", "WM", "CSX", "NSC", "UNP",
    "AMT", "PLD", "CCI", "EQIX", "PSA",
    "NEE", "DUK", "SO", "D", "AEP",
]

ALL_TICKERS = TICKERS_BR + TICKERS_US


def fetch_all(tickers: list[str], conservative: bool) -> pd.DataFrame:
    """Fetch data for all tickers with delays to avoid rate limiting."""
    results = []
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i}/{total}] {ticker}...", end=" ", flush=True)
        row = _calculate_with_retry(ticker, conservative, max_retries=3)
        if row is not None:
            results.append(row)
            print("✓")
        else:
            print("✗ (skipped)")

        # Rate limiting — 1.5s between each ticker
        if i < total:
            time.sleep(1.5)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df['Status'] = df.apply(classify_status, axis=1)
    df.sort_values('FCF Yield', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def main():
    """Main entry point for the daily data update."""
    os.makedirs("data", exist_ok=True)

    now = datetime.now(timezone.utc)
    print(f"=== Screener FCF Yield — Data Update ===")
    print(f"    Date: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"    Tickers: {len(ALL_TICKERS)}")
    print()

    # ── Normal Mode ──────────────────────
    print("── Fetching Normal Mode ──")
    df_normal = fetch_all(ALL_TICKERS, conservative=False)
    if not df_normal.empty:
        df_normal.to_csv("data/screener_normal.csv", index=False)
        print(f"\n✓ Saved data/screener_normal.csv ({len(df_normal)} tickers)")
    else:
        print("\n✗ No data fetched for normal mode")

    print()

    # ── Conservative Mode ────────────────
    print("── Fetching Conservative Mode ──")
    df_conservative = fetch_all(ALL_TICKERS, conservative=True)
    if not df_conservative.empty:
        df_conservative.to_csv("data/screener_conservative.csv", index=False)
        print(f"\n✓ Saved data/screener_conservative.csv ({len(df_conservative)} tickers)")
    else:
        print("\n✗ No data fetched for conservative mode")

    # ── Metadata ─────────────────────────
    meta = {
        "last_updated": now.isoformat(),
        "tickers_total": len(ALL_TICKERS),
        "tickers_normal_ok": len(df_normal) if not df_normal.empty else 0,
        "tickers_conservative_ok": len(df_conservative) if not df_conservative.empty else 0,
    }
    pd.Series(meta).to_json("data/metadata.json")
    print(f"\n✓ Metadata saved to data/metadata.json")
    print(f"\n=== Done! ===")


if __name__ == "__main__":
    main()
