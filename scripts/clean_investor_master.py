import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

# Load investor_master and states
investor_df = pd.read_csv(os.path.join(RAW_DIR, "investor_master.csv"))
states_df = pd.read_csv(os.path.join(RAW_DIR, "states.csv"))

# Map of state names to state codes for cleaning
# States in csv: UP, Delhi, Maharashtra, Karnataka
# States in states.csv: UP (Uttar Pradesh), DL (Delhi), MH (Maharashtra), KA (Karnataka)
state_name_to_code = dict(zip(states_df["state_name"].str.lower(), states_df["state_code"]))
# Also map code to code to preserve UP
state_code_to_code = dict(zip(states_df["state_code"].str.lower(), states_df["state_code"]))
mapping = {**state_name_to_code, **state_code_to_code}

def clean_state(state):
    if pd.isna(state):
        return state
    state_str = str(state).strip().lower()
    return mapping.get(state_str, state)

investor_df["state"] = investor_df["state"].apply(clean_state)

# Save cleaned file
investor_df.to_csv(os.path.join(PROCESSED_DIR, "investor_master_clean.csv"), index=False)
print("investor_master cleaned successfully!")
