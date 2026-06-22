import pandas as pd
import glob
import os

def load_and_explore_datasets(data_dir="data/raw"):
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {data_dir}. Please place the 10 provided CSV datasets there.")
        return {}
        
    datasets = {}
    for file in csv_files:
        filename = os.path.basename(file)
        print(f"\n--- Loading {filename} ---")
        try:
            df = pd.read_csv(file)
            print(f"Shape: {df.shape}")
            print("Data Types:")
            print(df.dtypes)
            print("Head:")
            print(df.head())
            datasets[filename] = df
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            
    return datasets

def explore_fund_master(fund_master_df):
    print("\n--- Exploring Fund Master ---")
    if 'fund_house' in fund_master_df.columns:
        print("\nUnique Fund Houses:")
        print(fund_master_df['fund_house'].unique())
    if 'category' in fund_master_df.columns:
        print("\nUnique Categories:")
        print(fund_master_df['category'].unique())
    if 'sub_category' in fund_master_df.columns:
        print("\nUnique Sub-categories:")
        print(fund_master_df['sub_category'].unique())
    if 'risk_grade' in fund_master_df.columns:
        print("\nUnique Risk Grades:")
        print(fund_master_df['risk_grade'].unique())

def validate_amfi_codes(fund_master_df, nav_history_df):
    print("\n--- Validating AMFI Codes ---")
    if 'scheme_code' in fund_master_df.columns and 'scheme_code' in nav_history_df.columns:
        master_codes = set(fund_master_df['scheme_code'].unique())
        history_codes = set(nav_history_df['scheme_code'].unique())
        
        missing_in_history = master_codes - history_codes
        
        print(f"Total codes in fund_master: {len(master_codes)}")
        print(f"Total codes in nav_history: {len(history_codes)}")
        print(f"Codes in fund_master but missing in nav_history: {len(missing_in_history)}")
        
        # Short data quality summary
        print("\nData Quality Summary:")
        if len(missing_in_history) == 0:
            print("- All AMFI codes in fund_master have corresponding records in nav_history.")
        else:
            print(f"- Found {len(missing_in_history)} AMFI codes in fund_master without NAV history.")
    else:
        print("Required columns ('scheme_code') not found in the datasets for validation.")

if __name__ == "__main__":
    datasets = load_and_explore_datasets()
    
    # We expect fund_master.csv and nav_history.csv to exist among the loaded datasets
    fund_master_key = next((k for k in datasets.keys() if 'fund_master' in k.lower()), None)
    nav_history_key = next((k for k in datasets.keys() if 'nav_history' in k.lower()), None)
    
    if fund_master_key:
        explore_fund_master(datasets[fund_master_key])
        
        if nav_history_key:
            validate_amfi_codes(datasets[fund_master_key], datasets[nav_history_key])
        else:
            print("\nnav_history.csv not found, skipping validation.")
    else:
        print("\nfund_master.csv not found, skipping specific exploration and validation.")
