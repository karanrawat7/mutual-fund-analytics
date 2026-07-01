import pandas as pd
import glob
import os


def load_and_explore_datasets(data_dir="data/raw"):
    """
    Load all CSV files from the given directory and perform basic exploration.
    """
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return {}

    datasets = {}

    for file in csv_files:
        filename = os.path.basename(file)

        print("\n" + "=" * 70)
        print(f"Loading Dataset: {filename}")
        print("=" * 70)

        try:
            df = pd.read_csv(file)

            # Store dataframe
            datasets[filename] = df

            # Shape
            print("\nShape:")
            print(df.shape)

            # Data Types
            print("\nData Types:")
            print(df.dtypes)

            # First 5 Rows
            print("\nFirst 5 Rows:")
            print(df.head())

            # -----------------------------
            # Data Quality / Anomaly Checks
            # -----------------------------

            print("\nData Quality Checks")

            # Missing Values
            print("\nMissing Values:")
            print(df.isnull().sum())

            # Duplicate Rows
            print("\nDuplicate Rows:")
            print(df.duplicated().sum())

            # Numeric Summary
            print("\nSummary Statistics:")
            print(df.describe(include="all"))

            print("-" * 70)

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    return datasets


def explore_fund_master(fund_master_df):
    """
    Explore fund_master dataset.
    """

    print("\n" + "=" * 70)
    print("FUND MASTER EXPLORATION")
    print("=" * 70)

    print("\nAMFI Scheme Code Structure")
    print("---------------------------")
    print("- Every mutual fund scheme has a unique AMFI Scheme Code.")
    print("- It is used to identify a scheme across datasets.")
    print("- This code links fund_master with nav_history.")
    print("- One scheme should have one unique AMFI code.")

    if "fund_house" in fund_master_df.columns:
        print("\nUnique Fund Houses:")
        print(fund_master_df["fund_house"].unique())

    if "category" in fund_master_df.columns:
        print("\nUnique Categories:")
        print(fund_master_df["category"].unique())

    if "sub_category" in fund_master_df.columns:
        print("\nUnique Sub Categories:")
        print(fund_master_df["sub_category"].unique())

    if "risk_grade" in fund_master_df.columns:
        print("\nUnique Risk Grades:")
        print(fund_master_df["risk_grade"].unique())


def validate_amfi_codes(fund_master_df, nav_history_df):
    """
    Validate that every AMFI code in fund_master exists in nav_history.
    """

    print("\n" + "=" * 70)
    print("AMFI CODE VALIDATION")
    print("=" * 70)

    if (
        "amfi_code" not in fund_master_df.columns
        or "amfi_code" not in nav_history_df.columns
    ):
        print("amfi_code column not found.")
        return

    master_codes = set(fund_master_df["amfi_code"].unique())
    history_codes = set(nav_history_df["amfi_code"].unique())

    missing_codes = master_codes - history_codes

    print(f"Total AMFI Codes in fund_master : {len(master_codes)}")
    print(f"Total AMFI Codes in nav_history : {len(history_codes)}")

    if len(missing_codes) == 0:

        print("\nData Quality Summary")
        print("--------------------")
        print("[OK] All AMFI codes in fund_master are present in nav_history.")
        print("No missing scheme codes found.")

    else:

        print("\nData Quality Summary")
        print("--------------------")
        print(f"[ERROR] Missing AMFI Codes : {len(missing_codes)}")

        print("\nMissing Codes:")
        for code in sorted(missing_codes):
            print(code)


def main():

    datasets = load_and_explore_datasets()

    # Find fund_master.csv
    fund_master_key = next(
        (file for file in datasets if "fund_master" in file.lower()),
        None,
    )

    # Find nav_history.csv
    nav_history_key = next(
        (file for file in datasets if "nav_history" in file.lower()),
        None,
    )

    if fund_master_key:

        explore_fund_master(datasets[fund_master_key])

        if nav_history_key:
            validate_amfi_codes(
                datasets[fund_master_key],
                datasets[nav_history_key],
            )
        else:
            print("\nnav_history.csv not found.")

    else:
        print("\nfund_master.csv not found.")


if __name__ == "__main__":
    main()