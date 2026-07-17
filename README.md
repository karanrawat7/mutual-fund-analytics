# Bluestock Mutual Fund Analytics Capstone

Comprehensive analytics, ETL, and reporting pipeline for Mutual Fund data — now extended with a full **Equity Analytics & Financial Ratio Engine** for 92 Indian listed companies.

---

## Project Structure

```
.
├── data/
│   ├── raw/                    # Raw CSVs, daily NAV, companies.xlsx (92 companies × 15 yrs)
│   └── processed/              # Cleaned datasets and computed metrics
├── database/
│   └── bluestock_mf.db         # SQLite: mutual fund + equity analytics tables
├── src/
│   ├── analytics/
│   │   ├── ratios.py           # Profitability, leverage & efficiency ratio functions
│   │   ├── cagr.py             # CAGR engine with 6 edge-case handlers
│   │   ├── cashflow_kpis.py    # FCF, CFO quality, CapEx intensity, capital allocation
│   │   ├── populate_ratios.py  # Orchestrator: populates financial_ratios table
│   │   └── edge_case_audit.py  # ROCE/ROE cross-checks → ratio_edge_cases.log
│   └── data/
│       ├── generate_equity_data.py   # Synthetic financial data generator
│       └── schema.py                 # DDL: companies, company_financials, financial_ratios
├── tests/
│   └── kpi/
│       ├── test_ratios.py      # 8 profitability ratio unit tests
│       ├── test_leverage.py    # 4 leverage & efficiency unit tests
│       ├── test_cagr.py        # 6 CAGR edge-case unit tests
│       └── test_cashflow.py    # 2 cash flow KPI unit tests
├── output/
│   ├── capital_allocation.csv  # 8-pattern capital allocation labels (1,380 rows)
│   └── ratio_edge_cases.log    # Documented anomalies with categories
├── scripts/                    # ETL pipeline, report generators, dashboard builders
├── notebooks/                  # Jupyter EDA and quantitative analysis
├── reports/                    # PDF, PPTX, HTML reports, and dashboard PNGs
├── dashboard/                  # Power BI CSVs and setup guide
└── sql/                        # Database schema definitions
```

---

## Sprint 2 — Financial Ratio Engine ✅

> **Epic 02 | Days 08–14 | 42 Story Points**

### What Was Built

| Component | Detail |
|---|---|
| Companies | 92 listed Indian companies across 12 sectors |
| Years | FY2010 – FY2024 (15 years per company) |
| `financial_ratios` rows | **1,380** (92 × 15) |
| KPI columns | **47** per company-year |
| Unit tests | **20 / 20 passing** |

### KPIs Computed

**Profitability** — Net Profit Margin, Operating Profit Margin, ROE, ROCE, ROA

**Leverage / Efficiency** — Debt-to-Equity, Interest Coverage (with ICR label), High-leverage Flag, Net Debt, Asset Turnover

**Cash Flow** — Free Cash Flow, FCF Conversion Rate, CapEx Intensity, CFO Quality Score, 8-Pattern Capital Allocation Classifier

**CAGR (3yr / 5yr / 10yr)** — Revenue, PAT, EPS — with 6 edge-case flags (`DECLINE_TO_LOSS`, `TURNAROUND`, `BOTH_NEGATIVE`, `ZERO_BASE`, `INSUFFICIENT`)

**Composite** — Weighted composite quality score (ROE + CAGR + D/E + ICR + CFO quality + FCF conversion)

### Running the Ratio Engine

```bash
# Step 1 — generate companies.xlsx (if not present)
python -m src.data.generate_equity_data

# Step 2 — create tables and load raw data
python -m src.data.schema

# Step 3 — compute all KPIs and populate financial_ratios
python -m src.analytics.populate_ratios

# Step 4 — cross-check ratios and generate audit log
python -m src.analytics.edge_case_audit

# Step 5 — run all 20 unit tests
python -m pytest tests/kpi/ -v
```

### Exit Criteria — All Met ✅

| Criterion | Result |
|---|---|
| `SELECT COUNT(*) FROM financial_ratios` ≥ 1,100 | **1,380** ✅ |
| Zero null-only columns | **0** ✅ |
| 20 unit tests pass with 0 failures | **20/20** ✅ |
| ROE spot-check difference < 0.1% (TCS, HDFC Bank, Reliance) | **< 0.0001%** ✅ |
| Revenue CAGR 5yr spot-check difference < 0.1% | **< 0.0001%** ✅ |
| `ratio_edge_cases.log` exists with documented explanations | **114 anomalies** ✅ |
| Screener (ROE > 15% & D/E < 1) count 15–50 | **31 companies** ✅ |

---

## Sprint 1 — Mutual Fund Analytics

### Setup & Installation

```bash
pip install -r requirements.txt
python scripts/etl_pipeline.py
```

### Key Deliverables & Commands

- **Streamlit Web Dashboard:**
  ```bash
  streamlit run scripts/streamlit_app.py
  ```

- **Generate Final Report (PDF) & Presentation (PPTX):**
  ```bash
  python scripts/generate_reports.py
  ```

- **Fund Recommender CLI:**
  ```bash
  python scripts/recommender.py --risk High
  ```

- **Markowitz Efficient Frontier:**
  ```bash
  python scripts/efficient_frontier.py
  ```

- **Monte Carlo 5-Year NAV Projection:**
  ```bash
  python scripts/monte_carlo.py
  ```

- **HTML Email Report Generator:**
  ```bash
  python scripts/email_report.py
  ```

- **Live NAV Fetcher (Auto-scheduling):**
  See docs inside `scripts/live_nav_fetch.py` for setting up Windows Task Scheduler or Linux Cron to auto-fetch daily NAV data.
