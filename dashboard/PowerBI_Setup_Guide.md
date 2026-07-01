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
