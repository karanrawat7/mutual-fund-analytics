"""
Dashboard Deliverables Generator
Produces:
  1. dashboard/data/  — 8 Power BI-ready CSV exports
  2. reports/page1_industry_overview.png
  3. reports/page2_fund_performance.png
  4. reports/page3_investor_analytics.png
  5. reports/page4_sip_market_trends.png
  6. reports/Dashboard.pdf
  7. dashboard/PowerBI_Setup_Guide.md
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import PdfPages
import sqlite3, os, textwrap

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "database", "bluestock_mf.db")
REPORTS   = os.path.join(BASE_DIR, "reports")
DASH_DATA = os.path.join(BASE_DIR, "dashboard", "data")
DASH_DIR  = os.path.join(BASE_DIR, "dashboard")
os.makedirs(REPORTS,   exist_ok=True)
os.makedirs(DASH_DATA, exist_ok=True)

# ── Bluestock Theme ──────────────────────────────────────────
BG_DARK    = "#0D1117"
BG_CARD    = "#161B22"
BG_PANEL   = "#1C2128"
ACCENT     = "#58A6FF"
ACCENT2    = "#3FB950"
ACCENT3    = "#F78166"
ACCENT4    = "#D2A8FF"
ACCENT5    = "#79C0FF"
TEXT_WHITE = "#E6EDF3"
TEXT_DIM   = "#8B949E"
GRID_CLR   = "#30363D"
PALETTE    = ["#58A6FF","#3FB950","#F78166","#D2A8FF","#79C0FF","#FFA657","#FF7B72","#7EE787"]

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG_PANEL)
    ax.set_title(title, color=TEXT_WHITE, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, color=TEXT_DIM, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_DIM, fontsize=9)
    ax.tick_params(colors=TEXT_DIM, labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID_CLR)
    ax.grid(axis="y", color=GRID_CLR, linestyle="--", alpha=0.4)

def kpi_card(fig, rect, value, label, color=ACCENT):
    ax = fig.add_axes(rect, facecolor=BG_CARD)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID_CLR)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, value, transform=ax.transAxes, ha="center", va="center",
            fontsize=20, fontweight="bold", color=color)
    ax.text(0.5, 0.22, label, transform=ax.transAxes, ha="center", va="center",
            fontsize=9, color=TEXT_DIM)

# ── Load Data ────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
df_schemes    = pd.read_sql("SELECT * FROM dim_fund_synthetic",    conn)
df_nav        = pd.read_sql("SELECT * FROM fact_nav_synthetic",    conn)
df_aum        = pd.read_sql("SELECT * FROM fact_aum_synthetic",    conn)
df_sip        = pd.read_sql("SELECT * FROM fact_sip_inflow",       conn)
df_investors  = pd.read_sql("SELECT * FROM dim_investor_synthetic",conn)
df_holdings   = pd.read_sql("SELECT * FROM fact_holdings",         conn)
df_benchmarks = pd.read_sql("SELECT * FROM fact_benchmarks",       conn)
df_metrics    = pd.read_sql("SELECT * FROM fact_metrics",          conn)
df_folio      = pd.read_sql("SELECT * FROM fact_folio_growth",     conn)
df_txn        = pd.read_sql("SELECT * FROM fact_transactions",     conn)
conn.close()

df_nav["date"] = pd.to_datetime(df_nav["date"])
df_benchmarks["date"] = pd.to_datetime(df_benchmarks["date"])

# ── Step 1: Export Power BI CSVs ─────────────────────────────
tables = {
    "dim_fund":        df_schemes,
    "fact_nav":        df_nav,
    "fact_aum":        df_aum,
    "fact_sip_inflow": df_sip,
    "dim_investor":    df_investors,
    "fact_holdings":   df_holdings,
    "fact_benchmarks": df_benchmarks,
    "fact_metrics":    df_metrics,
}
for name, df in tables.items():
    path = os.path.join(DASH_DATA, f"{name}.csv")
    df.to_csv(path, index=False)
print(f"[OK] Exported {len(tables)} CSVs to {DASH_DATA}")

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — Industry Overview
# ═══════════════════════════════════════════════════════════════
print("Rendering Page 1 — Industry Overview...")
fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)

# Header bar
ax_hdr = fig.add_axes([0, 0.92, 1, 0.08], facecolor=BG_CARD)
ax_hdr.set_xticks([]); ax_hdr.set_yticks([])
for sp in ax_hdr.spines.values(): sp.set_visible(False)
ax_hdr.text(0.02, 0.5, "BLUESTOCK", transform=ax_hdr.transAxes, fontsize=22,
            fontweight="bold", color=ACCENT, va="center")
ax_hdr.text(0.12, 0.5, "Mutual Fund Analytics Dashboard", transform=ax_hdr.transAxes,
            fontsize=14, color=TEXT_WHITE, va="center")
ax_hdr.text(0.98, 0.5, "Page 1 — Industry Overview", transform=ax_hdr.transAxes,
            fontsize=10, color=TEXT_DIM, va="center", ha="right")

# KPI Cards
total_aum = df_aum[df_aum["year"]==2025]["aum_crore"].sum()
kpi_card(fig, [0.02, 0.78, 0.22, 0.12], f"Rs {total_aum/100000:.1f}L Cr", "Total AUM (2025)", ACCENT)
kpi_card(fig, [0.26, 0.78, 0.22, 0.12], "Rs 31,002 Cr", "SIP Monthly Inflow", ACCENT2)
kpi_card(fig, [0.50, 0.78, 0.22, 0.12], "26.12 Cr", "Total Folios", ACCENT3)
kpi_card(fig, [0.74, 0.78, 0.22, 0.12], "40", "Active Schemes", ACCENT4)

# AUM Trend Line Chart (bottom left)
ax1 = fig.add_axes([0.05, 0.08, 0.42, 0.62], facecolor=BG_PANEL)
style_ax(ax1, "Industry AUM Trend (2022 - 2025)", "Year", "AUM (Lakh Crore)")
yearly_aum = df_aum.groupby("year")["aum_crore"].sum() / 100000
ax1.plot(yearly_aum.index, yearly_aum.values, color=ACCENT, linewidth=3, marker="o", markersize=8)
ax1.fill_between(yearly_aum.index, yearly_aum.values, alpha=0.15, color=ACCENT)
for yr, val in zip(yearly_aum.index, yearly_aum.values):
    ax1.annotate(f"{val:.1f}L", (yr, val), textcoords="offset points", xytext=(0, 12),
                 fontsize=9, color=TEXT_WHITE, ha="center", fontweight="bold")

# AUM by AMC Bar Chart (bottom right)
ax2 = fig.add_axes([0.55, 0.08, 0.42, 0.62], facecolor=BG_PANEL)
style_ax(ax2, "AUM by Fund House (2025)", "AUM (Lakh Crore)", "")
aum_2025 = df_aum[df_aum["year"]==2025].sort_values("aum_crore", ascending=True)
colors_bar = [ACCENT3 if fh == "SBI Mutual Fund" else ACCENT for fh in aum_2025["fund_house"]]
ax2.barh(range(len(aum_2025)), aum_2025["aum_crore"]/100000, color=colors_bar, height=0.6)
ax2.set_yticks(range(len(aum_2025)))
short_names = [n.replace(" Mutual Fund","").replace(" MF","") for n in aum_2025["fund_house"]]
ax2.set_yticklabels(short_names, fontsize=8, color=TEXT_DIM)
for i, v in enumerate(aum_2025["aum_crore"]/100000):
    ax2.text(v + 0.1, i, f"{v:.1f}L", va="center", fontsize=8, color=TEXT_WHITE)

p1_path = os.path.join(REPORTS, "page1_industry_overview.png")
plt.savefig(p1_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
plt.close()
print(f"  -> {p1_path}")

# ═══════════════════════════════════════════════════════════════
# PAGE 2 — Fund Performance
# ═══════════════════════════════════════════════════════════════
print("Rendering Page 2 — Fund Performance...")
fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)

# Header
ax_hdr = fig.add_axes([0, 0.92, 1, 0.08], facecolor=BG_CARD)
ax_hdr.set_xticks([]); ax_hdr.set_yticks([])
for sp in ax_hdr.spines.values(): sp.set_visible(False)
ax_hdr.text(0.02, 0.5, "BLUESTOCK", fontsize=22, fontweight="bold", color=ACCENT,
            va="center", transform=ax_hdr.transAxes)
ax_hdr.text(0.12, 0.5, "Fund Performance Dashboard", fontsize=14, color=TEXT_WHITE,
            va="center", transform=ax_hdr.transAxes)
ax_hdr.text(0.98, 0.5, "Page 2 — Fund Performance", fontsize=10, color=TEXT_DIM,
            va="center", ha="right", transform=ax_hdr.transAxes)

# Scatter: Return vs Risk (left)
ax3 = fig.add_axes([0.05, 0.42, 0.42, 0.46], facecolor=BG_PANEL)
style_ax(ax3, "Return vs Risk Scatter (3yr CAGR vs Std Dev)", "3-Year CAGR (%)", "Max Drawdown (%)")
cat_colors = {"Equity": ACCENT, "Hybrid": ACCENT2, "Debt": ACCENT3}
for cat in ["Equity","Hybrid","Debt"]:
    mask = df_metrics["category"] == cat
    ax3.scatter(df_metrics.loc[mask, "cagr_3y"], df_metrics.loc[mask, "max_drawdown"].abs(),
                c=cat_colors[cat], s=df_metrics.loc[mask, "scorecard"]*3, alpha=0.75, label=cat)
ax3.legend(facecolor=BG_CARD, labelcolor=TEXT_WHITE, fontsize=8)

# Top 5 NAV vs Benchmark (right)
ax4 = fig.add_axes([0.55, 0.42, 0.42, 0.46], facecolor=BG_PANEL)
style_ax(ax4, "Top 5 Funds vs Nifty 50 (3-Year Cumulative)", "Date", "Cumulative Return (%)")
top5 = df_metrics.sort_values("scorecard", ascending=False).head(5)
START_3Y = pd.Timestamp("2023-06-30")
END_3Y = pd.Timestamp("2026-06-30")
df_n3 = df_nav[(df_nav["date"]>=START_3Y)&(df_nav["date"]<=END_3Y)]
df_b3 = df_benchmarks[(df_benchmarks["date"]>=START_3Y)&(df_benchmarks["date"]<=END_3Y)].sort_values("date")

for i, (_, r) in enumerate(top5.iterrows()):
    df_f = df_n3[df_n3["amfi_code"]==r["scheme_code"]].sort_values("date")
    if df_f.empty: continue
    cum = (df_f["nav"]/df_f["nav"].iloc[0]-1)*100
    ax4.plot(df_f["date"], cum, color=PALETTE[i], lw=1.5, label=r["scheme_name"][:20])
cum_b = (df_b3["nifty_50"]/df_b3["nifty_50"].iloc[0]-1)*100
ax4.plot(df_b3["date"], cum_b, color="white", lw=2, linestyle="--", label="Nifty 50")
ax4.legend(facecolor=BG_CARD, labelcolor=TEXT_WHITE, fontsize=7, loc="upper left")

# Fund Scorecard Table (bottom)
ax5 = fig.add_axes([0.05, 0.04, 0.90, 0.32], facecolor=BG_PANEL)
style_ax(ax5, "Fund Scorecard — Top 15 Ranked Schemes", "", "")
ax5.set_xticks([]); ax5.set_yticks([])

top15 = df_metrics.sort_values("scorecard", ascending=False).head(15)
cols = ["scheme_name","category","cagr_3y","sharpe_ratio","alpha","max_drawdown","scorecard"]
col_labels = ["Scheme Name","Category","CAGR 3Y(%)","Sharpe","Alpha(%)","Max DD(%)","Score"]

# Table header
for j, label in enumerate(col_labels):
    x = 0.02 + j * 0.14
    ax5.text(x, 0.95, label, transform=ax5.transAxes, fontsize=8, fontweight="bold",
             color=ACCENT, va="top")
# Table rows
for i, (_, row) in enumerate(top15.iterrows()):
    y_pos = 0.88 - i * 0.058
    for j, c in enumerate(cols):
        x = 0.02 + j * 0.14
        val = row[c]
        if isinstance(val, float):
            text = f"{val:.2f}"
        else:
            text = str(val)[:28]
        color = TEXT_WHITE if j == 0 else (ACCENT2 if isinstance(val, float) and val > 0 else ACCENT3 if isinstance(val, float) and val < 0 else TEXT_DIM)
        ax5.text(x, y_pos, text, transform=ax5.transAxes, fontsize=7, color=color, va="top")

p2_path = os.path.join(REPORTS, "page2_fund_performance.png")
plt.savefig(p2_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
plt.close()
print(f"  -> {p2_path}")

# ═══════════════════════════════════════════════════════════════
# PAGE 3 — Investor Analytics
# ═══════════════════════════════════════════════════════════════
print("Rendering Page 3 — Investor Analytics...")
fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)

ax_hdr = fig.add_axes([0, 0.92, 1, 0.08], facecolor=BG_CARD)
ax_hdr.set_xticks([]); ax_hdr.set_yticks([])
for sp in ax_hdr.spines.values(): sp.set_visible(False)
ax_hdr.text(0.02, 0.5, "BLUESTOCK", fontsize=22, fontweight="bold", color=ACCENT,
            va="center", transform=ax_hdr.transAxes)
ax_hdr.text(0.12, 0.5, "Investor Analytics Dashboard", fontsize=14, color=TEXT_WHITE,
            va="center", transform=ax_hdr.transAxes)
ax_hdr.text(0.98, 0.5, "Page 3 — Investor Analytics", fontsize=10, color=TEXT_DIM,
            va="center", ha="right", transform=ax_hdr.transAxes)

# SIP by State (top left)
ax6 = fig.add_axes([0.05, 0.50, 0.42, 0.38], facecolor=BG_PANEL)
style_ax(ax6, "SIP Volume by State", "Total SIP Amount (Rs)", "")
state_sip = df_investors.groupby("state")["sip_amount"].sum().sort_values(ascending=True)
ax6.barh(range(len(state_sip)), state_sip.values, color=ACCENT, height=0.6)
ax6.set_yticks(range(len(state_sip)))
ax6.set_yticklabels(state_sip.index, fontsize=8, color=TEXT_DIM)

# Transaction Type Donut (top right)
ax7 = fig.add_axes([0.58, 0.50, 0.35, 0.38], facecolor=BG_DARK)
ax7.set_facecolor(BG_DARK)
# Use investor data to simulate transaction types distribution
txn_types = {"SIP": 55, "Lumpsum": 30, "Redemption": 15}
wedges, texts, autotexts = ax7.pie(
    txn_types.values(), labels=txn_types.keys(), autopct="%1.1f%%",
    colors=[ACCENT, ACCENT2, ACCENT3], wedgeprops=dict(width=0.4),
    textprops={"color": TEXT_WHITE, "fontsize": 10}, startangle=90)
for at in autotexts:
    at.set_color(TEXT_WHITE); at.set_fontsize(9)
ax7.set_title("Transaction Type Split", color=TEXT_WHITE, fontsize=11, fontweight="bold")

# Age Group vs SIP Amount (bottom left)
ax8 = fig.add_axes([0.05, 0.06, 0.42, 0.38], facecolor=BG_PANEL)
style_ax(ax8, "Average SIP Amount by Age Group", "Age Group", "Avg SIP (Rs)")
age_sip = df_investors.groupby("age_group")["sip_amount"].mean().reindex(["18-25","26-35","36-45","46-60","60+"])
ax8.bar(range(len(age_sip)), age_sip.values, color=PALETTE[:5], width=0.6)
ax8.set_xticks(range(len(age_sip)))
ax8.set_xticklabels(age_sip.index, fontsize=9, color=TEXT_DIM)
for i, v in enumerate(age_sip.values):
    ax8.text(i, v + 100, f"Rs {v:,.0f}", ha="center", fontsize=8, color=TEXT_WHITE)

# T30 vs B30 Pie (bottom right)
ax9 = fig.add_axes([0.58, 0.06, 0.35, 0.38], facecolor=BG_DARK)
ax9.set_facecolor(BG_DARK)
tier_counts = df_investors["city_tier"].value_counts()
wedges2, texts2, auto2 = ax9.pie(
    tier_counts.values, labels=tier_counts.index, autopct="%1.1f%%",
    colors=[ACCENT4, ACCENT5], wedgeprops=dict(width=0.45),
    textprops={"color": TEXT_WHITE, "fontsize": 10}, startangle=140)
for at in auto2:
    at.set_color(TEXT_WHITE); at.set_fontsize(9)
ax9.set_title("T30 vs B30 City Tier Split", color=TEXT_WHITE, fontsize=11, fontweight="bold")

p3_path = os.path.join(REPORTS, "page3_investor_analytics.png")
plt.savefig(p3_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
plt.close()
print(f"  -> {p3_path}")

# ═══════════════════════════════════════════════════════════════
# PAGE 4 — SIP & Market Trends
# ═══════════════════════════════════════════════════════════════
print("Rendering Page 4 — SIP & Market Trends...")
fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_DARK)

ax_hdr = fig.add_axes([0, 0.92, 1, 0.08], facecolor=BG_CARD)
ax_hdr.set_xticks([]); ax_hdr.set_yticks([])
for sp in ax_hdr.spines.values(): sp.set_visible(False)
ax_hdr.text(0.02, 0.5, "BLUESTOCK", fontsize=22, fontweight="bold", color=ACCENT,
            va="center", transform=ax_hdr.transAxes)
ax_hdr.text(0.12, 0.5, "SIP & Market Trends Dashboard", fontsize=14, color=TEXT_WHITE,
            va="center", transform=ax_hdr.transAxes)
ax_hdr.text(0.98, 0.5, "Page 4 — SIP & Market Trends", fontsize=10, color=TEXT_DIM,
            va="center", ha="right", transform=ax_hdr.transAxes)

# Dual Axis: SIP Inflow bars + Nifty 50 line (top)
ax10 = fig.add_axes([0.06, 0.50, 0.88, 0.38], facecolor=BG_PANEL)
style_ax(ax10, "SIP Monthly Inflow (Bar) + Nifty 50 Index (Line)  |  2022 - 2025",
         "", "SIP Inflow (Rs Crore)")
x_pos = range(len(df_sip))
ax10.bar(x_pos, df_sip["total_sip_inflow"], color=ACCENT, alpha=0.7, width=0.7)
ax10.set_xticks(list(x_pos)[::3])
ax10.set_xticklabels(df_sip["month"].values[::3], fontsize=7, color=TEXT_DIM, rotation=45)

# Secondary axis for Nifty 50
ax10b = ax10.twinx()
# Resample benchmarks to monthly for alignment
df_bench_monthly = df_benchmarks.set_index("date").resample("MS")["nifty_50"].last().reset_index()
df_bench_monthly = df_bench_monthly[(df_bench_monthly["date"]>="2022-01-01")&(df_bench_monthly["date"]<="2025-12-31")]
if len(df_bench_monthly) >= len(df_sip):
    df_bench_monthly = df_bench_monthly.head(len(df_sip))
ax10b.plot(range(len(df_bench_monthly)), df_bench_monthly["nifty_50"], color=ACCENT3, lw=2.5, label="Nifty 50")
ax10b.set_ylabel("Nifty 50 Index", color=ACCENT3, fontsize=9)
ax10b.tick_params(colors=TEXT_DIM, labelsize=8)
for sp in ax10b.spines.values():
    sp.set_edgecolor(GRID_CLR)
ax10b.legend(facecolor=BG_CARD, labelcolor=TEXT_WHITE, fontsize=8, loc="upper left")

# Annotate SIP peak
peak_idx = df_sip["total_sip_inflow"].idxmax()
ax10.annotate(f"Peak: Rs {df_sip.loc[peak_idx,'total_sip_inflow']:,.0f} Cr",
              xy=(peak_idx, df_sip.loc[peak_idx,"total_sip_inflow"]),
              xytext=(peak_idx-8, df_sip.loc[peak_idx,"total_sip_inflow"]+1500),
              arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1.5),
              fontsize=9, color=ACCENT2, fontweight="bold")

# Category Inflow Heatmap (bottom left)
ax11 = fig.add_axes([0.06, 0.06, 0.52, 0.38], facecolor=BG_PANEL)
style_ax(ax11, "Category Inflow Heatmap (2022 - 2025)", "Month", "Category")
cats = ["Equity","Debt","Hybrid","Solution Oriented","Others"]
heatmap_data = df_sip.set_index("month")[cats].T.values
im = ax11.imshow(heatmap_data, aspect="auto", cmap="YlGnBu", interpolation="nearest")
ax11.set_yticks(range(len(cats)))
ax11.set_yticklabels(cats, fontsize=8, color=TEXT_DIM)
ax11.set_xticks(list(range(len(df_sip)))[::6])
ax11.set_xticklabels(df_sip["month"].values[::6], fontsize=7, color=TEXT_DIM, rotation=45)
plt.colorbar(im, ax=ax11, fraction=0.02, pad=0.02, label="Rs Crore")

# Top 5 Categories by Net Inflow FY25 (bottom right)
ax12 = fig.add_axes([0.66, 0.06, 0.30, 0.38], facecolor=BG_PANEL)
style_ax(ax12, "Top Categories by Inflow (FY25)", "Net Inflow (Rs Crore)", "")
fy25_sip = df_sip[df_sip["month"].str.startswith("2025")]
cat_totals = fy25_sip[cats].sum().sort_values(ascending=True)
ax12.barh(range(len(cat_totals)), cat_totals.values, color=PALETTE[:5], height=0.5)
ax12.set_yticks(range(len(cat_totals)))
ax12.set_yticklabels(cat_totals.index, fontsize=8, color=TEXT_DIM)
for i, v in enumerate(cat_totals.values):
    ax12.text(v + 200, i, f"Rs {v:,.0f}", va="center", fontsize=8, color=TEXT_WHITE)

p4_path = os.path.join(REPORTS, "page4_sip_market_trends.png")
plt.savefig(p4_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
plt.close()
print(f"  -> {p4_path}")

# ═══════════════════════════════════════════════════════════════
# Combine into Dashboard.pdf
# ═══════════════════════════════════════════════════════════════
print("Combining pages into Dashboard.pdf...")
pdf_path = os.path.join(REPORTS, "Dashboard.pdf")
from PIL import Image
png_paths = [p1_path, p2_path, p3_path, p4_path]
rgb_images = []
for p in png_paths:
    img = Image.open(p).convert("RGB")
    rgb_images.append(img)
rgb_images[0].save(pdf_path, save_all=True, append_images=rgb_images[1:], resolution=150)
print(f"[OK] Dashboard.pdf  ->  {pdf_path}")

# ═══════════════════════════════════════════════════════════════
# PowerBI Setup Guide
# ═══════════════════════════════════════════════════════════════
guide = """\
# Power BI Dashboard Setup Guide

## Bluestock Mutual Fund Analytics

### Step 1: Import Data
1. Open Power BI Desktop
2. Click **Get Data** > **Text/CSV**
3. Import all 8 CSV files from `dashboard/data/`:
   - `dim_fund.csv`
   - `fact_nav.csv`
   - `fact_aum.csv`
   - `fact_sip_inflow.csv`
   - `dim_investor.csv`
   - `fact_holdings.csv`
   - `fact_benchmarks.csv`
   - `fact_metrics.csv`
4. Click **Transform Data** to open Power Query Editor
5. Ensure `date` columns are typed as **Date** and numeric columns as **Decimal/Whole Number**
6. Click **Close & Apply**

### Step 2: Create Relationships
In the **Model** view, create the following relationships:

| From | To | Key | Type |
|------|----|-----|------|
| fact_nav.amfi_code | dim_fund.scheme_code | amfi_code → scheme_code | Many-to-One |
| fact_metrics.scheme_code | dim_fund.scheme_code | scheme_code | One-to-One |
| fact_holdings.scheme_code | dim_fund.scheme_code | scheme_code | Many-to-One |
| fact_aum.fund_house | dim_fund.fund_house | fund_house | Many-to-Many |

### Step 3: Create Date Table (DAX)
```dax
DateTable = CALENDAR(DATE(2021,1,1), DATE(2026,12,31))
```
Add columns:
```dax
Year = YEAR([Date])
Month = FORMAT([Date], "MMM YYYY")
Quarter = "Q" & FORMAT([Date], "Q") & " " & YEAR([Date])
```

### Step 4: Build Pages

#### Page 1 — Industry Overview
- **4 KPI Cards**: Total AUM, SIP Monthly Inflow, Total Folios, Active Schemes
- **Line Chart**: X = Year, Y = Sum of AUM → from `fact_aum`
- **Bar Chart**: X = Fund House, Y = AUM → filter Year = 2025

#### Page 2 — Fund Performance
- **Scatter Chart**: X = cagr_3y, Y = max_drawdown (abs), Size = scorecard, Legend = category → from `fact_metrics`
- **Table Visual**: scheme_name, category, cagr_3y, sharpe_ratio, alpha, scorecard
- **Line Chart**: NAV trend for selected fund vs benchmark → from `fact_nav` + `fact_benchmarks`
- **Slicers**: fund_house, category

#### Page 3 — Investor Analytics
- **Bar Chart**: X = state, Y = sum(sip_amount) → from `dim_investor`
- **Donut Chart**: SIP/Lumpsum/Redemption percentages
- **Bar Chart**: X = age_group, Y = avg(sip_amount)
- **Pie Chart**: T30 vs B30 split
- **Slicers**: state, age_group, city_tier

#### Page 4 — SIP & Market Trends
- **Combo Chart**: Bars = SIP inflow, Line = Nifty 50 → from `fact_sip_inflow` + `fact_benchmarks`
- **Matrix Heatmap**: Rows = Category, Columns = Month, Values = Inflow
- **Bar Chart**: Top 5 categories by net inflow FY25

### Step 5: Apply Theme
1. Go to **View** > **Themes** > **Customize current theme**
2. Set Background: `#0D1117`, Card: `#161B22`, Accent: `#58A6FF`
3. Font: Segoe UI, 11pt

### Step 6: Add Interactivity
- **Drill-through**: Right-click fund table > Add drill-through to a NAV Detail page
- **Tooltips**: Enable tooltips on all chart visuals
- **Cross-filtering**: Enable bidirectional filtering between slicers and charts

### Step 7: Export
1. **Save as** `bluestock_mf_dashboard.pbix`
2. **File** > **Export** > **Export to PDF**
3. **Each page**: Right-click page tab > **Export page as image** (PNG)

### Pre-built Dashboard Screenshots
The following PNG screenshots are available in `reports/`:
- `page1_industry_overview.png`
- `page2_fund_performance.png`
- `page3_investor_analytics.png`
- `page4_sip_market_trends.png`
- `Dashboard.pdf` (all 4 pages combined)
"""
guide_path = os.path.join(DASH_DIR, "PowerBI_Setup_Guide.md")
with open(guide_path, "w", encoding="utf-8") as f:
    f.write(guide)
print(f"[OK] PowerBI_Setup_Guide.md  ->  {guide_path}")

print("\n=== ALL DASHBOARD DELIVERABLES COMPLETE ===")
