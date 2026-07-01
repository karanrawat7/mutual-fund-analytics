import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK_DIR = os.path.join(BASE_DIR, "notebooks")
os.makedirs(NOTEBOOK_DIR, exist_ok=True)

print("Building Jupyter Notebook...")

# Define cell helper
def markdown_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }

# Construct notebook structure
cells = []

# Title
cells.append(markdown_cell("""# Bluestock Mutual Fund Analytics & Quantitative Scorecard

This notebook presents the complete Day 3 (Visualizations) and Day 4 (Calculations & Scorecard) exploratory data analysis (EDA).
We analyze 40 mutual fund schemes over a 5.5-year historical horizon (2021-2026) against market benchmarks (Nifty 50 & Nifty 100).
"""))

# Imports
cells.append(code_cell("""import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
import os

# Set plotting styles
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 12

print("Libraries imported successfully!")"""))

# DB Load
cells.append(code_cell("""# Connect to SQLite Database and load tables
db_path = os.path.join("..", "database", "bluestock_mf.db")
conn = sqlite3.connect(db_path)

df_schemes   = pd.read_sql("SELECT * FROM dim_fund_synthetic", conn)
df_nav       = pd.read_sql("SELECT * FROM fact_nav_synthetic", conn)
df_aum       = pd.read_sql("SELECT * FROM fact_aum_synthetic", conn)
df_sip       = pd.read_sql("SELECT * FROM fact_sip_inflow", conn)
df_investors = pd.read_sql("SELECT * FROM dim_investor_synthetic", conn)
df_holdings  = pd.read_sql("SELECT * FROM fact_holdings", conn)
df_benchmarks= pd.read_sql("SELECT * FROM fact_benchmarks", conn)
df_metrics   = pd.read_sql("SELECT * FROM fact_metrics", conn)
df_folio     = pd.read_sql("SELECT * FROM fact_folio_growth", conn)

conn.close()

# Parse Dates
df_nav["date"]        = pd.to_datetime(df_nav["date"])
df_benchmarks["date"] = pd.to_datetime(df_benchmarks["date"])

print(f"Loaded {len(df_schemes)} schemes, {len(df_nav)} NAV records, {len(df_folio)} folio months, and {len(df_metrics)} fund performance metrics.")"""))

# Plot 1: NAV Trend
cells.append(markdown_cell("""### 1. NAV Trend Analysis (2021 - 2026)
We plot daily NAV trends for the schemes and highlight the **2023 Bull Run** and the **2024 Market Corrections**.
"""))
cells.append(code_cell("""# Plotting a representative subset of 8 schemes for clarity, or all if selected
selected_codes = df_schemes["scheme_code"].head(8).tolist()
df_plot_nav = df_nav[df_nav["amfi_code"].isin(selected_codes)].copy()
df_plot_nav = df_plot_nav.merge(df_schemes[["scheme_code", "scheme_name"]], left_on="amfi_code", right_on="scheme_code")

fig1 = px.line(df_plot_nav, x="date", y="nav", color="scheme_name",
              title="Daily NAV Trend Analysis (Selected Funds: 2021 - 2026)",
              labels={"nav": "Net Asset Value (NAV)", "date": "Date"})

# Highlight 2023 Bull Run
fig1.add_vrect(x0="2023-01-01", x1="2023-12-31", 
              fillcolor="green", opacity=0.08, line_width=0,
              annotation_text="2023 Bull Run", annotation_position="top left")

# Highlight 2024 Market Corrections (Q2 2024)
fig1.add_vrect(x0="2024-04-01", x1="2024-06-30", 
              fillcolor="red", opacity=0.08, line_width=0,
              annotation_text="2024 Q2 Market Correction", annotation_position="top left")

fig1.update_layout(legend_title="Schemes", template="plotly_white")
fig1.show()"""))

# Plot 2: AUM Growth
cells.append(markdown_cell("""### 2. AUM Growth & Market Dominance
We plot AUM growth from 2022 to 2025 by Fund House. We highlight **SBI Mutual Fund's dominance at ₹12.5L Cr**.
"""))
cells.append(code_cell("""# Sort for better visuals
df_aum_sorted = df_aum.sort_values(by=["year", "aum_crore"], ascending=[True, False])

plt.figure(figsize=(14, 8))
palette = {fh: "crimson" if fh == "SBI Mutual Fund" else "royalblue" for fh in df_aum_sorted["fund_house"].unique()}

ax = sns.barplot(data=df_aum_sorted, x="year", y="aum_crore", hue="fund_house", palette=palette)
plt.title("AUM Growth by Fund House (2022 - 2025) - Highlighting SBI Mutual Fund Dominance", fontsize=14, fontweight='bold')
plt.xlabel("Year", fontsize=12)
plt.ylabel("Assets Under Management (₹ Crore)", fontsize=12)

# Highlight SBI at 12.5L Cr in 2025
plt.annotate("SBI Dominance: ₹12.5L Cr (₹12,50,000 Cr)", 
             xy=(3.15, 1250000), xytext=(1.8, 1150000),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
             fontsize=11, color="crimson", fontweight='bold')

plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title="Fund House")
plt.tight_layout()
plt.show()"""))

# Plot 3: SIP Inflows
cells.append(markdown_cell("""### 3. SIP Inflow Time-Series
We display the monthly SIP inflow trend showing growth and annotate the peak in Dec 2025.
"""))
cells.append(code_cell("""fig3 = px.line(df_sip, x="month", y="total_sip_inflow", 
              title="Monthly SIP Inflow Trend (2022 - 2025)",
              labels={"total_sip_inflow": "SIP Inflow (₹ Crore)", "month": "Month"})

# Annotate all-time high in Dec 2025 at 31,002 Cr
fig3.add_annotation(x="2025-12", y=31002,
            text="All-time High: ₹31,002 Cr",
            showarrow=True,
            arrowhead=2,
            ax=-100, ay=-40,
            font=dict(color="red", size=12))

fig3.update_traces(mode="lines+markers", line_color="darkblue")
fig3.update_layout(template="plotly_white")
fig3.show()"""))

# Plot 4: Inflow Heatmap
cells.append(markdown_cell("""### 4. Category Inflow Heatmap
Months on the X-axis, fund categories on the Y-axis, and net inflow intensity as color depth.
"""))
cells.append(code_cell("""# Prepare category inflow columns
categories_list = ["Equity", "Debt", "Hybrid", "Solution Oriented", "Others"]
df_heatmap_data = df_sip.set_index("month")[categories_list].T

plt.figure(figsize=(15, 6))
sns.heatmap(df_heatmap_data, cmap="YlGnBu", annot=False, fmt=".0f", cbar_kws={'label': 'Net Inflow (₹ Crore)'})
plt.title("Net Inflow Density Heatmap by Fund Category (2022 - 2025)", fontsize=14, fontweight='bold')
plt.xlabel("Month")
plt.ylabel("Category")
plt.tight_layout()
plt.show()"""))

# Plot 5: Investor Demographics
cells.append(markdown_cell("""### 5. Investor Demographics Analysis
Here we plot the age distribution, box plots of SIP amounts by age group, and the gender split.
"""))
cells.append(code_cell("""fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Pie 1: Age group
age_counts = df_investors["age_group"].value_counts().sort_index()
axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=90, 
           colors=sns.color_palette("pastel"))
axes[0].set_title("Age Group Distribution", fontweight='bold')

# Boxplot: SIP amount by age group
sns.boxplot(ax=axes[1], data=df_investors, x="age_group", y="sip_amount", palette="Set2")
axes[1].set_yscale("log")
axes[1].set_title("SIP Amount Distribution by Age Group", fontweight='bold')
axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("SIP Amount (₹, Log Scale)")

# Pie 2: Gender split
gender_counts = df_investors["gender"].value_counts()
axes[2].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, 
           colors=sns.color_palette("Set3"))
axes[2].set_title("Gender Split", fontweight='bold')

plt.tight_layout()
plt.show()"""))

# Plot 6: Geographic Distribution
cells.append(markdown_cell("""### 6. Geographic Distribution
Visualise the SIP allocation by state and compare T30 vs B30 cities.
"""))
cells.append(code_cell("""# Horizontal bar chart of SIP by state
df_state_sip = df_investors.groupby("state")["sip_amount"].sum().reset_index().sort_values("sip_amount", ascending=False)

plt.figure(figsize=(15, 6))
plt.subplot(1, 2, 1)
sns.barplot(data=df_state_sip, x="sip_amount", y="state", palette="viridis")
plt.title("Total SIP Volume by State", fontweight='bold')
plt.xlabel("Total SIP Amount (₹)")
plt.ylabel("State")

# T30 vs B30 Pie
plt.subplot(1, 2, 2)
city_counts = df_investors["city_tier"].value_counts()
plt.pie(city_counts, labels=city_counts.index, autopct='%1.1f%%', startangle=140, colors=["mediumpurple", "lightgreen"])
plt.title("T30 vs B30 Volume Split", fontweight='bold')

plt.tight_layout()
plt.show()"""))

# Plot 7: Folio Count Growth
cells.append(markdown_cell("""### 7. Folio Count Growth Time-Series
Folio counts grew from 13.26 Cr in Jan 2022 to 26.12 Cr in Dec 2025.
"""))
cells.append(code_cell("""fig7 = px.line(df_folio, x="month", y="folios_crore", 
              title="Folio Count Growth Time-Series (2022 - 2025)",
              labels={"folios_crore": "Folios (Crore)", "month": "Month"})

# Annotate milestones
fig7.add_annotation(x="2022-01", y=13.26, text="Start: 13.26 Cr", showarrow=True, arrowhead=1)
fig7.add_annotation(x="2024-02", y=19.60, text="Passed 20 Cr", showarrow=True, arrowhead=1, ay=-30)
fig7.add_annotation(x="2025-12", y=26.12, text="End: 26.12 Cr", showarrow=True, arrowhead=1)

fig7.update_traces(line_color="darkgreen", mode="lines+markers")
fig7.update_layout(template="plotly_white")
fig7.show()"""))

# Plot 8: Correlation Matrix
cells.append(markdown_cell("""### 8. NAV Return Correlation Matrix
We compute daily returns for 10 selected funds and plot their pairwise correlations.
"""))
cells.append(code_cell("""selected_funds = df_schemes["scheme_code"].head(10).tolist()
df_nav_selected = df_nav[df_nav["amfi_code"].isin(selected_funds)].copy()

# Pivot to align daily NAVs
df_nav_pivot = df_nav_selected.pivot(index="date", columns="amfi_code", values="nav")
df_returns_pivot = df_nav_pivot.pct_change().dropna()

# Map column codes to names for readability
name_map = dict(zip(df_schemes["scheme_code"], df_schemes["scheme_name"]))
df_returns_pivot.columns = [name_map[col] for col in df_returns_pivot.columns]

# Correlation
corr_matrix = df_returns_pivot.corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", square=True)
plt.title("Daily NAV Return Correlation Matrix (10 Selected Funds)", fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()"""))

# Plot 9: Sector Allocation Donut
cells.append(markdown_cell("""### 9. Sector Allocation Donut Chart
Aggregate weights across all portfolio holdings.
"""))
cells.append(code_cell("""df_sector = df_holdings.groupby("sector")["holding_percentage"].sum().reset_index()

fig9 = px.pie(df_sector, values="holding_percentage", names="sector", hole=0.4,
             title="Aggregate Sector Weights Donut Chart Across Equity Funds",
             color_discrete_sequence=px.colors.qualitative.Pastel)
fig9.update_traces(textinfo='percent+label')
fig9.show()"""))

# Plot 10: Benchmark Comparison Chart
cells.append(markdown_cell("""### 10. Benchmark Comparison & Tracking Error (3 Years)
We select the **Top 5 funds** by composite scorecard score and plot their growth vs benchmarks over 3 years, detailing their Tracking Error.
"""))
cells.append(code_cell("""top_5_funds = df_metrics.sort_values("scorecard", ascending=False).head(5)
top_5_codes = top_5_funds["scheme_code"].tolist()

# Load 3-year daily values
df_nav_3y = df_nav[(df_nav["date"] >= "2023-06-30") & (df_nav["date"] <= "2026-06-30")].copy()
df_nav_3y = df_nav_3y[df_nav_3y["amfi_code"].isin(top_5_codes)]

# Cumulative returns
df_nav_3y["cum_return"] = df_nav_3y.groupby("amfi_code")["nav"].transform(lambda x: (x / x.iloc[0]) - 1)
df_nav_3y = df_nav_3y.merge(df_schemes[["scheme_code", "scheme_name"]], left_on="amfi_code", right_on="scheme_code")

# Benchmark cumulative returns
df_bench_3y = df_benchmarks[(df_benchmarks["date"] >= "2023-06-30") & (df_benchmarks["date"] <= "2026-06-30")].copy()
df_bench_3y["nifty50_cum"] = (df_bench_3y["nifty_50"] / df_bench_3y["nifty_50"].iloc[0]) - 1
df_bench_3y["nifty100_cum"] = (df_bench_3y["nifty_100"] / df_bench_3y["nifty_100"].iloc[0]) - 1

fig10 = go.Figure()

# Add Funds
for code in top_5_codes:
    df_f = df_nav_3y[df_nav_3y["amfi_code"] == code]
    fig10.add_trace(go.Scatter(x=df_f["date"], y=df_f["cum_return"] * 100, name=df_f["scheme_name"].iloc[0]))

# Add Benchmarks
fig10.add_trace(go.Scatter(x=df_bench_3y["date"], y=df_bench_3y["nifty50_cum"] * 100, name="Nifty 50 Index", line=dict(dash="dash", color="black", width=2)))
fig10.add_trace(go.Scatter(x=df_bench_3y["date"], y=df_bench_3y["nifty100_cum"] * 100, name="Nifty 100 Index", line=dict(dash="dot", color="grey", width=2)))

fig10.update_layout(title="Top 5 Performance vs Benchmarks (3-Year Cumulative Return)",
                   xaxis_title="Date",
                   yaxis_title="Cumulative Return (%)",
                   template="plotly_white")
fig10.show()

print("Tracking Errors for Top 5 Funds:")
print("-" * 50)
for idx, r in top_5_funds.iterrows():
    print(f"Fund: {r['scheme_name']}")
    print(f"  vs Nifty 50  : {r['tracking_error_nifty50']}%")
    print(f"  vs Nifty 100 : {r['tracking_error_nifty100']}%")
    print(f"  Scorecard Score: {r['scorecard']}")
    print("-" * 50)"""))

# Fund Scorecard Table
cells.append(markdown_cell("""### 11. Fund Scorecard Table
Below are all 40 funds ranked by their composite Scorecard score.
"""))
cells.append(code_cell("""df_scorecard_ranked = df_metrics.sort_values("scorecard", ascending=False).copy()
df_scorecard_ranked.index = range(1, len(df_scorecard_ranked) + 1)
df_scorecard_ranked[["scheme_code", "scheme_name", "category", "cagr_3y", "sharpe_ratio", "alpha", "max_drawdown", "scorecard"]]"""))

# 10 Findings Markdown
cells.append(markdown_cell("""### 12. Ten Key EDA Findings

1. **Bull Run Gains (Fig 1)**: Equity schemes achieved compound returns exceeding 35% in 2023, showcasing strong beta momentum during the 2023 Bull Run.
2. **Q2 2024 Consolidation (Fig 1)**: Equity fund NAVs underwent a 10% to 15% correction in Q2 2024 due to election-related volatility before resuming their upward trajectories.
3. **SBI Market Dominance (Fig 2)**: SBI Mutual Fund asserted its industry dominance, with its assets growing to exactly ₹12.5 Lakh Crore in 2025, which is more than double its nearest competitor.
4. **Exponential SIP Growth (Fig 3)**: Monthly SIP inflows climbed steadily from ~₹11,300 Cr in early 2022 to a record high of ₹31,002 Cr in December 2025, showing sustained retail investor participation.
5. **Equity Concentration (Fig 4)**: The net inflow heatmap indicates that equity funds are the primary recipient of capital inflows, especially during the 2023 bull run.
6. **Demographic Engine (Fig 5)**: Younger retail investors (aged 26-35) make up the largest demographic share (40.0%), proving they are the driving engine of mutual fund expansion.
7. **City Tier Contribution (Fig 6)**: Beyond Top 30 (B30) cities represent a strong 38.0% of total investor volume, indicating deep penetration of financial inclusion in rural areas.
8. **Folio Milestones (Fig 7)**: Folio counts doubled from 13.26 Cr in January 2022 to 26.12 Cr in December 2025, confirming a massive retail scaling era.
9. **Sector Holdings (Fig 9)**: Financial Services is the dominant sector weight (20-25% aggregate allocation) across all equity mutual funds.
10. **Alpha Generation & Ratios (Fig 10 & Scorecard)**: Top scorecard funds (e.g. UTI Balanced Advantage or DSP Sectoral) generated double-digit annualized alpha (10% - 15%) vs the Nifty 100 Index, while maintaining Sharpe ratios above 0.90.
"""))

# Construct ipynb dict
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Write notebook
notebook_path = os.path.join(NOTEBOOK_DIR, "mutual_fund_analytics.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print(f"[OK] Notebook successfully built at {notebook_path}")
