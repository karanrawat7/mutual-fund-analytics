"""
Deliverables generator:
  1. fund_scorecard.csv
  2. alpha_beta.csv
  3. benchmark_comparison_chart.png
  4. Performance_Analytics.ipynb (built via build_notebook pattern)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for PNG export
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sqlite3, json, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")
REPORTS   = os.path.join(BASE_DIR, "reports")
NOTEBOOKS = os.path.join(BASE_DIR, "notebooks")
DB_PATH   = os.path.join(BASE_DIR, "database", "bluestock_mf.db")

os.makedirs(REPORTS,   exist_ok=True)
os.makedirs(NOTEBOOKS, exist_ok=True)

# ─────────────────────────────────────────
# Load base data
# ─────────────────────────────────────────
df_metrics = pd.read_csv(os.path.join(PROCESSED, "fund_metrics.csv"))
conn = sqlite3.connect(DB_PATH)
df_nav        = pd.read_sql("SELECT * FROM fact_nav_synthetic",  conn)
df_benchmarks = pd.read_sql("SELECT * FROM fact_benchmarks",     conn)
df_schemes    = pd.read_sql("SELECT * FROM dim_fund_synthetic",  conn)
conn.close()

df_nav["date"]        = pd.to_datetime(df_nav["date"])
df_benchmarks["date"] = pd.to_datetime(df_benchmarks["date"])

# ─────────────────────────────────────────
# 1.  fund_scorecard.csv
# ─────────────────────────────────────────
scorecard_cols = [
    "scheme_code", "scheme_name", "category", "expense_ratio",
    "cagr_1y", "cagr_3y", "cagr_5y",
    "sharpe_ratio", "sortino_ratio",
    "max_drawdown", "drawdown_start", "drawdown_end",
    "scorecard"
]
df_scorecard = (
    df_metrics[scorecard_cols]
    .sort_values("scorecard", ascending=False)
    .reset_index(drop=True)
)
df_scorecard.index += 1
df_scorecard.index.name = "rank"
scorecard_path = os.path.join(REPORTS, "fund_scorecard.csv")
df_scorecard.to_csv(scorecard_path)
print(f"[OK] fund_scorecard.csv  ->  {scorecard_path}")

# ─────────────────────────────────────────
# 2.  alpha_beta.csv
# ─────────────────────────────────────────
alpha_beta_cols = [
    "scheme_code", "scheme_name", "category",
    "alpha", "beta",
    "sharpe_ratio", "sortino_ratio",
    "tracking_error_nifty50", "tracking_error_nifty100",
    "scorecard"
]
df_alpha_beta = (
    df_metrics[alpha_beta_cols]
    .sort_values("alpha", ascending=False)
    .reset_index(drop=True)
)
df_alpha_beta.index += 1
df_alpha_beta.index.name = "alpha_rank"
ab_path = os.path.join(REPORTS, "alpha_beta.csv")
df_alpha_beta.to_csv(ab_path)
print(f"[OK] alpha_beta.csv      ->  {ab_path}")

# ─────────────────────────────────────────
# 3.  benchmark_comparison_chart.png
#     Top-5 by scorecard vs Nifty 50 & Nifty 100 (3-year window)
# ─────────────────────────────────────────
START_3Y = pd.Timestamp("2023-06-30")
END_3Y   = pd.Timestamp("2026-06-30")

top5 = df_metrics.sort_values("scorecard", ascending=False).head(5)
top5_codes = top5["scheme_code"].tolist()

# Filter NAV to 3-year window
df_nav_3y = df_nav[(df_nav["date"] >= START_3Y) & (df_nav["date"] <= END_3Y)]
df_bench_3y = df_benchmarks[(df_benchmarks["date"] >= START_3Y) & (df_benchmarks["date"] <= END_3Y)].copy()

# Compute cumulative returns (rebased to 0 at start)
df_bench_3y = df_bench_3y.sort_values("date").copy()
bench_start_50  = df_bench_3y["nifty_50"].iloc[0]
bench_start_100 = df_bench_3y["nifty_100"].iloc[0]
df_bench_3y["nifty50_cum"]  = (df_bench_3y["nifty_50"]  / bench_start_50  - 1) * 100
df_bench_3y["nifty100_cum"] = (df_bench_3y["nifty_100"] / bench_start_100 - 1) * 100

# --- Build figure ---
COLORS = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FF9800"]
fig, (ax_main, ax_te) = plt.subplots(
    2, 1, figsize=(16, 11),
    gridspec_kw={"height_ratios": [3, 1]},
    facecolor="#0D1117"
)
fig.suptitle(
    "Top 5 Funds vs Nifty 50 & Nifty 100  |  3-Year Cumulative Return (Jun 2023 – Jun 2026)",
    fontsize=14, fontweight="bold", color="white", y=0.98
)

for ax in (ax_main, ax_te):
    ax.set_facecolor("#161B22")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363D")

# Plot fund lines
for i, code in enumerate(top5_codes):
    name = top5.loc[top5["scheme_code"] == code, "scheme_name"].values[0]
    score = top5.loc[top5["scheme_code"] == code, "scorecard"].values[0]
    df_f = df_nav_3y[df_nav_3y["amfi_code"] == code].sort_values("date")
    if df_f.empty:
        continue
    cum = (df_f["nav"] / df_f["nav"].iloc[0] - 1) * 100
    ax_main.plot(df_f["date"], cum, color=COLORS[i], linewidth=2,
                 label=f"{name[:32]}…  (Score {score:.0f})")

# Plot benchmarks
ax_main.plot(df_bench_3y["date"], df_bench_3y["nifty50_cum"],
             color="white",  linewidth=1.8, linestyle="--", label="Nifty 50 Index")
ax_main.plot(df_bench_3y["date"], df_bench_3y["nifty100_cum"],
             color="#78909C", linewidth=1.8, linestyle=":",  label="Nifty 100 Index")

ax_main.set_ylabel("Cumulative Return (%)", color="white", fontsize=11)
ax_main.yaxis.label.set_color("white")
ax_main.legend(loc="upper left", fontsize=8, framealpha=0.3,
               facecolor="#21262D", labelcolor="white")
ax_main.grid(axis="y", color="#30363D", linestyle="--", alpha=0.6)
ax_main.tick_params(axis="x", labelbottom=False)

# --- Tracking error bar chart (bottom panel) ---
fund_names_short = []
te50_vals, te100_vals = [], []
for code in top5_codes:
    row = top5[top5["scheme_code"] == code].iloc[0]
    fund_names_short.append(row["scheme_name"].split(" ")[0])
    te50_vals.append(row["tracking_error_nifty50"])
    te100_vals.append(row["tracking_error_nifty100"])

x = np.arange(len(top5_codes))
w = 0.35
ax_te.bar(x - w/2, te50_vals,  width=w, color="#42A5F5", label="vs Nifty 50")
ax_te.bar(x + w/2, te100_vals, width=w, color="#EF5350", label="vs Nifty 100")

ax_te.set_xticks(x)
ax_te.set_xticklabels(fund_names_short, color="white", fontsize=9)
ax_te.set_ylabel("Tracking Error (%)", color="white", fontsize=10)
ax_te.set_title("Annualised Tracking Error (3-Year)", color="white", fontsize=10)
ax_te.legend(facecolor="#21262D", labelcolor="white", fontsize=9, framealpha=0.4)
ax_te.grid(axis="y", color="#30363D", linestyle="--", alpha=0.5)

plt.tight_layout(rect=[0, 0, 1, 0.97])
chart_path = os.path.join(REPORTS, "benchmark_comparison_chart.png")
plt.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
plt.close()
print(f"[OK] benchmark_comparison_chart.png  ->  {chart_path}")

# ─────────────────────────────────────────
# 4.  Performance_Analytics.ipynb
# ─────────────────────────────────────────
def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in src.splitlines()]}

def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [l + "\n" for l in src.splitlines()]}

cells = []

cells.append(md("""# Performance Analytics Notebook
### Mutual Fund Quantitative Analysis — 40 Schemes (2021 – 2026)

**Coverage:** Daily Returns · CAGR (1y/3y/5yr) · Sharpe Ratio · Sortino Ratio · Alpha & Beta (OLS) · Maximum Drawdown · Fund Scorecard · Benchmark Comparison · Tracking Error

**Risk-Free Rate:** 6.5% (RBI Repo Rate Proxy)  
**Benchmark:** Nifty 50 & Nifty 100  
**Universe:** 40 synthetic AMFI schemes across Equity / Debt / Hybrid
"""))

# ── Imports & DB load ──────────────────────────────────────────────────────────
cells.append(md("## 1. Setup & Data Loading"))
cells.append(code("""\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import sqlite3, os

sns.set_theme(style="darkgrid")
plt.rcParams["figure.figsize"] = (14, 6)
plt.rcParams["font.size"] = 11

DB_PATH = os.path.join("..", "database", "bluestock_mf.db")
conn = sqlite3.connect(DB_PATH)

df_metrics    = pd.read_csv(os.path.join("..", "data", "processed", "fund_metrics.csv"))
df_nav        = pd.read_sql("SELECT * FROM fact_nav_synthetic",  conn)
df_benchmarks = pd.read_sql("SELECT * FROM fact_benchmarks",     conn)
df_schemes    = pd.read_sql("SELECT * FROM dim_fund_synthetic",  conn)
conn.close()

df_nav["date"]        = pd.to_datetime(df_nav["date"])
df_benchmarks["date"] = pd.to_datetime(df_benchmarks["date"])
print(f"Loaded {len(df_schemes)} schemes | {len(df_nav):,} NAV rows | {len(df_metrics)} fund metric rows")
"""))

# ── Daily Returns validation ────────────────────────────────────────────────────
cells.append(md("""\
## 2. Daily Returns — Distribution Validation
`daily_return = NAV_t / NAV_{t-1} - 1`

We compute returns for every fund-day, then overlay a normal distribution to confirm the return series behaves reasonably (slight negative skew expected for equity funds).
"""))
cells.append(code("""\
# Compute daily returns for all 40 schemes
df_nav_sorted = df_nav.sort_values(["amfi_code", "date"])
df_nav_sorted["daily_return"] = df_nav_sorted.groupby("amfi_code")["nav"].pct_change()
df_returns = df_nav_sorted.dropna(subset=["daily_return"])

# Summary
print("Daily Return Summary (all funds pooled):")
print(df_returns["daily_return"].describe().apply(lambda x: f"{x:.6f}"))

# Distribution plot (sample 50k rows for speed)
sample = df_returns["daily_return"].sample(min(50_000, len(df_returns)), random_state=42)
fig, ax = plt.subplots(figsize=(13, 5))
ax.hist(sample * 100, bins=200, density=True, color="#1565C0", alpha=0.75, label="Observed daily returns")

# Overlay Normal
mu, sigma = sample.mean() * 100, sample.std() * 100
x = np.linspace(mu - 4*sigma, mu + 4*sigma, 400)
from scipy.stats import norm
ax.plot(x, norm.pdf(x, mu, sigma), "r--", lw=2, label=f"Normal(μ={mu:.3f}%, σ={sigma:.3f}%)")
ax.axvline(0, color="white", lw=0.8, linestyle=":")
ax.set_xlabel("Daily Return (%)"); ax.set_ylabel("Density")
ax.set_title("Daily Return Distribution — All 40 Schemes Pooled")
ax.legend()
plt.tight_layout(); plt.show()
"""))

# ── CAGR Comparison Table ──────────────────────────────────────────────────────
cells.append(md("""\
## 3. CAGR Comparison Table
`CAGR = (NAV_end / NAV_start) ^ (1 / n) − 1`

We calculate 1-year, 3-year, and 5-year CAGR and display a ranked table, sorted by 3-year CAGR.
"""))
cells.append(code("""\
cagr_cols = ["scheme_name", "category", "cagr_1y", "cagr_3y", "cagr_5y", "expense_ratio"]
df_cagr = df_metrics[cagr_cols].sort_values("cagr_3y", ascending=False).reset_index(drop=True)
df_cagr.index += 1
df_cagr.index.name = "rank"

# Style the table
def color_val(v):
    if isinstance(v, float):
        color = "green" if v > 0 else "red"
        return f"color: {color}"
    return ""

styled = (df_cagr.style
          .background_gradient(subset=["cagr_1y","cagr_3y","cagr_5y"], cmap="RdYlGn")
          .format({"cagr_1y": "{:.2f}%", "cagr_3y": "{:.2f}%", "cagr_5y": "{:.2f}%",
                   "expense_ratio": "{:.2f}%"}))
styled
"""))

# ── Sharpe Ratio ────────────────────────────────────────────────────────────────
cells.append(md("""\
## 4. Sharpe Ratio Ranking
`Sharpe = (Rp − Rf) / σ(Rp) × √252`  |  Rf = 6.5% p.a.

Higher Sharpe means better risk-adjusted performance. We plot the top 20 and bottom 5 for context.
"""))
cells.append(code("""\
df_sharpe = df_metrics[["scheme_name","category","sharpe_ratio","sortino_ratio"]].sort_values("sharpe_ratio", ascending=False).reset_index(drop=True)
df_sharpe.index += 1

# Bar chart — Top 20 by Sharpe
top20 = df_sharpe.head(20)
colors = ["#1976D2" if c == "Equity" else "#388E3C" if c == "Hybrid" else "#F57C00"
          for c in top20["category"]]

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.barh(range(len(top20)), top20["sharpe_ratio"], color=colors)
ax.set_yticks(range(len(top20)))
ax.set_yticklabels([n[:45] for n in top20["scheme_name"]], fontsize=9)
ax.axvline(0, color="red", lw=0.8, linestyle="--")
ax.set_xlabel("Sharpe Ratio")
ax.set_title("Top 20 Funds by Sharpe Ratio (annualised, Rf=6.5%)")
patches = [mpatches.Patch(color="#1976D2", label="Equity"),
           mpatches.Patch(color="#388E3C", label="Hybrid"),
           mpatches.Patch(color="#F57C00", label="Debt")]
ax.legend(handles=patches, loc="lower right")
ax.invert_yaxis()
plt.tight_layout(); plt.show()

print("\\nFull Sharpe/Sortino Table:")
df_sharpe.head(40)
"""))

# ── Sortino ────────────────────────────────────────────────────────────────────
cells.append(md("""\
## 5. Sortino Ratio
`Sortino = (Rp − Rf) / σ_downside × √252`

The Sortino ratio penalises only downside volatility. Funds with a high Sortino but moderate Sharpe have well-controlled drawdown behaviour.
"""))
cells.append(code("""\
df_sortino = df_metrics[["scheme_name","category","sharpe_ratio","sortino_ratio"]].sort_values("sortino_ratio", ascending=False).reset_index(drop=True)
df_sortino.index += 1

# Scatter: Sharpe vs Sortino coloured by category
color_map = {"Equity": "#1976D2", "Hybrid": "#388E3C", "Debt": "#F57C00"}
colors_sc = [color_map[c] for c in df_sortino["category"]]

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df_sortino["sharpe_ratio"], df_sortino["sortino_ratio"], c=colors_sc, s=80, alpha=0.85)
ax.axline((0, 0), slope=1, color="grey", lw=1, linestyle="--", label="Sortino = Sharpe line")
ax.set_xlabel("Sharpe Ratio"); ax.set_ylabel("Sortino Ratio")
ax.set_title("Sharpe vs Sortino Ratio — All 40 Funds")
patches = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
ax.legend(handles=patches)
plt.tight_layout(); plt.show()

df_sortino.head(10)
"""))

# ── Alpha & Beta OLS ──────────────────────────────────────────────────────────
cells.append(md("""\
## 6. Alpha & Beta — OLS Regression on Nifty 100
`Fund_return = α + β × Nifty100_return + ε`  
`Alpha (annualised) = intercept × 252`

- **Beta > 1** → More volatile than the index (amplified market moves)  
- **Positive Alpha** → Consistent excess return above the benchmark
"""))
cells.append(code("""\
df_ab = df_metrics[["scheme_name","category","alpha","beta","tracking_error_nifty100","scorecard"]].copy()
df_ab = df_ab.sort_values("alpha", ascending=False).reset_index(drop=True)
df_ab.index += 1; df_ab.index.name = "alpha_rank"

# Scatter: Alpha vs Beta, sized by |TE|, coloured by category
color_map = {"Equity": "#1976D2", "Hybrid": "#388E3C", "Debt": "#F57C00"}
colors_sc = [color_map[c] for c in df_ab["category"]]
sizes = (df_ab["tracking_error_nifty100"].abs() * 10).clip(lower=30, upper=300)

fig, ax = plt.subplots(figsize=(11, 7))
sc = ax.scatter(df_ab["beta"], df_ab["alpha"], c=colors_sc, s=sizes, alpha=0.85)
ax.axhline(0, color="grey", lw=0.9, linestyle="--")
ax.axvline(1, color="grey", lw=0.9, linestyle=":")
ax.set_xlabel("Beta (vs Nifty 100)"); ax.set_ylabel("Alpha (% annualised)")
ax.set_title("Alpha vs Beta — 40 Mutual Fund Schemes\\n(bubble size ∝ Tracking Error vs Nifty 100)")
patches = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
ax.legend(handles=patches, loc="upper left")
# Annotate top-5 alpha generators
for _, row in df_ab.head(5).iterrows():
    ax.annotate(row["scheme_name"].split()[0], (row["beta"], row["alpha"]),
                fontsize=7, ha="left", va="bottom",
                color="white" if row["alpha"] > 0 else "red")
plt.tight_layout(); plt.show()

print("\\nAlpha & Beta Table (top 10 by Alpha):")
df_ab.head(10)
"""))

# ── Max Drawdown ───────────────────────────────────────────────────────────────
cells.append(md("""\
## 7. Maximum Drawdown
`Max Drawdown = min(NAV_t / running_max(NAV) − 1)`

The largest peak-to-trough decline. We also report the worst-drawdown date range for each fund.
"""))
cells.append(code("""\
df_dd = df_metrics[["scheme_name","category","max_drawdown","drawdown_start","drawdown_end"]].copy()
df_dd = df_dd.sort_values("max_drawdown").reset_index(drop=True)   # most negative first
df_dd.index += 1; df_dd.index.name = "dd_rank"

# Horizontal bar — worst 15
worst15 = df_dd.head(15)
fig, ax = plt.subplots(figsize=(13, 6))
colors_dd = ["#C62828" if c == "Equity" else "#558B2F" if c == "Hybrid" else "#E65100"
             for c in worst15["category"]]
ax.barh(range(len(worst15)), worst15["max_drawdown"], color=colors_dd)
ax.set_yticks(range(len(worst15)))
ax.set_yticklabels([n[:45] for n in worst15["scheme_name"]], fontsize=9)
ax.set_xlabel("Maximum Drawdown (%)")
ax.set_title("15 Worst Maximum Drawdowns Across 40 Funds")
ax.invert_yaxis()
ax.axvline(-20, color="yellow", lw=0.9, linestyle="--", label="−20% threshold")
ax.legend()
plt.tight_layout(); plt.show()

df_dd.head(15)
"""))

# ── Composite Scorecard ────────────────────────────────────────────────────────
cells.append(md("""\
## 8. Fund Scorecard (0 – 100)
Composite weighted rank score:

| Weight | Metric |
|--------|--------|
| 30% | 3-Year CAGR rank |
| 25% | Sharpe Ratio rank |
| 20% | Alpha rank |
| 15% | Expense Ratio rank (inverse — lower is better) |
| 10% | Max Drawdown rank (inverse — less negative is better) |
"""))
cells.append(code("""\
df_scorecard = df_metrics[["scheme_code","scheme_name","category","expense_ratio",
                            "cagr_1y","cagr_3y","cagr_5y","sharpe_ratio","sortino_ratio",
                            "alpha","max_drawdown","scorecard"]].copy()
df_scorecard = df_scorecard.sort_values("scorecard", ascending=False).reset_index(drop=True)
df_scorecard.index += 1; df_scorecard.index.name = "rank"

# Lollipop chart
fig, ax = plt.subplots(figsize=(14, 9))
colors_lp = ["#1565C0" if c == "Equity" else "#2E7D32" if c == "Hybrid" else "#E65100"
             for c in df_scorecard["category"]]
ax.hlines(df_scorecard.index, 0, df_scorecard["scorecard"], color=colors_lp, linewidth=1.2, alpha=0.7)
ax.scatter(df_scorecard["scorecard"], df_scorecard.index, c=colors_lp, s=50, zorder=5)
ax.set_yticks(df_scorecard.index)
ax.set_yticklabels([n[:48] for n in df_scorecard["scheme_name"]], fontsize=8)
ax.set_xlabel("Composite Scorecard (0 – 100)")
ax.set_title("Fund Scorecard Ranking — All 40 Schemes")
ax.invert_yaxis()
ax.axvline(50, color="grey", lw=0.8, linestyle="--", label="Score = 50")
patches = [mpatches.Patch(color="#1565C0", label="Equity"),
           mpatches.Patch(color="#2E7D32", label="Hybrid"),
           mpatches.Patch(color="#E65100", label="Debt")]
ax.legend(handles=patches, loc="lower right")
plt.tight_layout(); plt.show()

df_scorecard
"""))

# ── Benchmark Comparison ──────────────────────────────────────────────────────
cells.append(md("""\
## 9. Benchmark Comparison — Top 5 vs Nifty 50 & Nifty 100 (3-Year)
`Tracking Error = Std(R_fund − R_benchmark) × √252`

A lower tracking error means the fund moves closely with the benchmark.
"""))
cells.append(code("""\
START_3Y = pd.Timestamp("2023-06-30")
END_3Y   = pd.Timestamp("2026-06-30")

top5 = df_metrics.sort_values("scorecard", ascending=False).head(5)
COLORS = ["#2196F3","#FF5722","#4CAF50","#9C27B0","#FF9800"]

df_nav_3y   = df_nav[(df_nav["date"] >= START_3Y) & (df_nav["date"] <= END_3Y)]
df_bench_3y = df_benchmarks[(df_benchmarks["date"] >= START_3Y) & (df_benchmarks["date"] <= END_3Y)].copy().sort_values("date")

# Cumulative returns
bench_s50  = df_bench_3y["nifty_50"].iloc[0]
bench_s100 = df_bench_3y["nifty_100"].iloc[0]
df_bench_3y["nifty50_cum"]  = (df_bench_3y["nifty_50"]  / bench_s50  - 1) * 100
df_bench_3y["nifty100_cum"] = (df_bench_3y["nifty_100"] / bench_s100 - 1) * 100

fig, ax = plt.subplots(figsize=(15, 7))
for i, (_, row) in enumerate(top5.iterrows()):
    code_val = row["scheme_code"]
    df_f = df_nav_3y[df_nav_3y["amfi_code"] == code_val].sort_values("date")
    if df_f.empty: continue
    cum = (df_f["nav"] / df_f["nav"].iloc[0] - 1) * 100
    label = f"{row['scheme_name'][:35]}  [Score={row['scorecard']:.0f}]"
    ax.plot(df_f["date"], cum, color=COLORS[i], lw=2, label=label)

ax.plot(df_bench_3y["date"], df_bench_3y["nifty50_cum"],  "w--", lw=2,   label="Nifty 50")
ax.plot(df_bench_3y["date"], df_bench_3y["nifty100_cum"], "grey", lw=1.8, linestyle=":", label="Nifty 100")

ax.set_xlabel("Date"); ax.set_ylabel("Cumulative Return (%)")
ax.set_title("Top-5 Fund Performance vs Benchmarks  |  3-Year Window (Jun 2023 – Jun 2026)", fontsize=13)
ax.legend(fontsize=8, loc="upper left")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.show()

# Tracking Error table
print("\\nTracking Error Summary:")
te_table = top5[["scheme_name","tracking_error_nifty50","tracking_error_nifty100","scorecard"]].reset_index(drop=True)
te_table.index += 1
te_table.columns = ["Scheme","TE vs Nifty 50 (%)","TE vs Nifty 100 (%)","Scorecard"]
print(te_table.to_string())
"""))

# ── Final Summary ─────────────────────────────────────────────────────────────
cells.append(md("""\
## 10. Deliverables

| File | Location | Description |
|------|----------|-------------|
| `Performance_Analytics.ipynb` | `notebooks/` | This notebook |
| `fund_scorecard.csv` | `reports/` | All 40 funds ranked by composite scorecard |
| `alpha_beta.csv` | `reports/` | Alpha, Beta, Tracking Error for all funds |
| `benchmark_comparison_chart.png` | `reports/` | High-resolution PNG of top-5 vs benchmarks |
"""))

# Assemble and write
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"}
    },
    "nbformat": 4,
    "nbformat_minor": 2
}
nb_path = os.path.join(NOTEBOOKS, "Performance_Analytics.ipynb")
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)
print(f"[OK] Performance_Analytics.ipynb  ->  {nb_path}")
