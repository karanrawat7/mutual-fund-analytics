import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

db_path = os.path.join(BASE_DIR, "database", "bluestock_mf.db")

conn = sqlite3.connect(db_path)

query = """
SELECT * FROM dim_fund;
"""

result = conn.execute(query)

for row in result:
    print(row)

conn.close()