from sqlalchemy import create_engine

engine = create_engine("sqlite:///test.db")

with engine.connect() as conn:
    print("Database Connected Successfully!")