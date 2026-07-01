CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_name TEXT NOT NULL,
    category TEXT,
    fund_house TEXT
);
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER,
    year INTEGER
);
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    date_id INTEGER,
    nav REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY,
    investor_id INTEGER,
    amfi_code INTEGER,
    date_id INTEGER,
    transaction_type TEXT,
    amount REAL,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    one_year_return REAL,
    three_year_return REAL,
    five_year_return REAL,
    expense_ratio REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);
CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    date_id INTEGER,
    aum REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_metrics (
    scheme_code INTEGER PRIMARY KEY,
    scheme_name TEXT,
    category TEXT,
    expense_ratio REAL,
    cagr_1y REAL,
    cagr_3y REAL,
    cagr_5y REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    alpha REAL,
    beta REAL,
    max_drawdown REAL,
    drawdown_start TEXT,
    drawdown_end TEXT,
    tracking_error_nifty50 REAL,
    tracking_error_nifty100 REAL,
    scorecard REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(amfi_code)
);