import sqlite3

conn = sqlite3.connect("database/bluestock_mf.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_fund(

amfi_code INTEGER PRIMARY KEY,

fund_name TEXT,

category TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_nav(

id INTEGER PRIMARY KEY AUTOINCREMENT,

amfi_code INTEGER,

date DATE,

nav REAL,

FOREIGN KEY(amfi_code)
REFERENCES dim_fund(amfi_code)

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_transactions(

transaction_id INTEGER PRIMARY KEY,

investor_id INTEGER,

amfi_code INTEGER,

transaction_type TEXT,

amount REAL,

date DATE

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_performance(

amfi_code INTEGER PRIMARY KEY,

one_year_return REAL,

three_year_return REAL,

five_year_return REAL,

expense_ratio REAL

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_aum(

id INTEGER PRIMARY KEY AUTOINCREMENT,

amfi_code INTEGER,

date DATE,

aum REAL

)
""")

conn.commit()

conn.close()

print("Database schema created successfully!")