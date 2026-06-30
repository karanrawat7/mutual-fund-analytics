# Data Dictionary

## Project: Bluestock Mutual Fund Analysis

This document describes all datasets, columns, data types, business definitions, and source files used in the project.

---

# 1. dim_fund

| Column | Data Type | Business Definition | Source |
|---------|-----------|---------------------|--------|
| amfi_code | INTEGER | Unique AMFI scheme identifier | fund_master.csv |
| fund_name | TEXT | Name of the mutual fund scheme | fund_master.csv |
| category | TEXT | Fund category (Equity, Debt, Hybrid, etc.) | fund_master.csv |
| fund_house | TEXT | Asset Management Company (AMC) | fund_master.csv |

---

# 2. fact_nav

| Column | Data Type | Business Definition | Source |
|---------|-----------|---------------------|--------|
| amfi_code | INTEGER | Mutual fund scheme identifier | nav_history.csv |
| date | DATE | NAV date | nav_history.csv |
| nav | REAL | Net Asset Value of the scheme | nav_history.csv |

---

# 3. fact_transactions

| Column | Data Type | Business Definition | Source |
|---------|-----------|---------------------|--------|
| transaction_id | INTEGER | Unique transaction ID | investor_transactions.csv |
| investor_id | INTEGER | Unique investor ID | investor_transactions.csv |
| amfi_code | INTEGER | Fund identifier | investor_transactions.csv |
| transaction_type | TEXT | SIP, Lumpsum, or Redemption | investor_transactions.csv |
| amount | REAL | Transaction amount | investor_transactions.csv |
| date | DATE | Transaction date | investor_transactions.csv |
| kyc_status | TEXT | KYC verification status | investor_transactions.csv |

---

# 4. fact_performance

| Column | Data Type | Business Definition | Source |
|---------|-----------|---------------------|--------|
| amfi_code | INTEGER | Mutual fund identifier | scheme_performance.csv |
| one_year_return | REAL | 1-year return (%) | scheme_performance.csv |
| three_year_return | REAL | 3-year return (%) | scheme_performance.csv |
| five_year_return | REAL | 5-year return (%) | scheme_performance.csv |
| expense_ratio | REAL | Expense ratio (%) | scheme_performance.csv |

---

# 5. fact_aum

| Column | Data Type | Business Definition | Source |
|---------|-----------|---------------------|--------|
| amfi_code | INTEGER | Mutual fund identifier | aum_history.csv |
| date | DATE | AUM reporting date | aum_history.csv |
| aum | REAL | Assets Under Management | aum_history.csv |

---

# 6. dim_date

| Column | Data Type | Business Definition |
|---------|-----------|---------------------|
| date_id | INTEGER | Surrogate key for date |
| full_date | DATE | Calendar date |
| day | INTEGER | Day of month |
| month | INTEGER | Month number |
| month_name | TEXT | Month name |
| quarter | INTEGER | Quarter of the year |
| year | INTEGER | Calendar year |