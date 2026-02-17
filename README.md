# 🚀 Screener FCF Yield "Antigravity"

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/julianimmj/screener-fcf-yield/main/app.py)

Aplicação Streamlit para **Value Investing** baseado em **Fluxo de Caixa Livre Real**.

> Diferente de sites como StatusInvest ou Fundamentus, este screener permite o **Ajuste de Capex** — revelando empresas que são máquinas de gerar caixa escondidas por trás de investimentos pesados.

---

## 📐 Metodologia

```
FCF = FCO − Capex − Juros − Impostos − Arrendamentos
Yield = FCF ÷ Market Cap
```

| Passo | Variável | Fonte |
|-------|----------|-------|
| 1 | **FCO** | Cash Flow Statement |
| 2 | **Adjusted FCO** | FCO − Δ Working Capital *(modo conservador)* |
| 3 | **Capex** | Cash Flow Statement |
| 4 | **Ajuste Expansão** | Se Capex > 1.5× Depreciação → usa Depreciação |
| 5 | **Juros / Impostos** | Income Statement (DRE) |
| 6 | **Arrendamentos** | Balance Sheet (Lease Liabilities) |

### Benchmarks

| Tipo | Yield Target |
|------|-------------|
| Empresas Gerais | ≥ 10 % → **Barato** |
| Commodities | ≥ 15 % → **Barato** |

---

## 🎯 Funcionalidades

- **40 ativos pré-carregados** (B3 + NYSE) — dados aparecem automaticamente
- **Filtro por status**: Baratos / Caros / Justos / Todos
- **Modo Conservador** com ajustes de Working Capital e Capex de Manutenção
- **Gráfico de bolhas** — FCF Yield vs Crescimento de Receita 5 anos
- **Cache de 1 hora** — carregamento rápido na nuvem
- **Tema dark profissional**

---

## 🛠️ Deploy no Streamlit Cloud

1. Faça fork ou clone deste repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte à sua conta GitHub
4. Selecione este repositório, branch `main`, e arquivo `app.py`
5. Clique em **Deploy** 🚀

### Execução Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📂 Estrutura

```
├── app.py                    # Interface Streamlit (Dashboard)
├── engine.py                 # Motor de cálculo FCF Yield
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação
├── .gitignore                # Ignorar cache/temp
└── .streamlit/
    └── config.toml           # Tema visual (Dark Mode)
```

---

**Autor:** [julianimmj](https://github.com/julianimmj) · Motor: Antigravity
