import requests
import pandas as pd
import os

def fetch_mf_data(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def process_and_save_mf_data(scheme_code, name, output_dir="data/raw"):
    print(f"Fetching NAV for {name} ({scheme_code})...")
    data = fetch_mf_data(scheme_code)
    
    if "data" in data and data["data"]:
        df = pd.DataFrame(data["data"])
        # Add metadata columns
        df['scheme_code'] = data['meta']['scheme_code']
        df['scheme_name'] = data['meta']['scheme_name']
        df['fund_house'] = data['meta']['fund_house']
        df['scheme_type'] = data['meta']['scheme_type']
        df['scheme_category'] = data['meta']['scheme_category']
        
        # Save to CSV
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"nav_{scheme_code}.csv")
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")
        return df
    else:
        print(f"No data found for {name} ({scheme_code})")
        return None

if __name__ == "__main__":
    # 1. Fetch live NAV from mfapi.in: GET https://api.mfapi.in/mf/125497 (HDFC Top 100 Direct). Parse JSON response and save as raw CSV.
    process_and_save_mf_data(125497, "HDFC Top 100 Direct")
    
    # 2. Fetch NAV for 5 key schemes: SBI Bluechip (119551), ICICI Bluechip (120503), Nippon Large Cap (118632), Axis Bluechip (119092), Kotak Bluechip (120841).
    key_schemes = {
        119551: "SBI Bluechip",
        120503: "ICICI Bluechip",
        118632: "Nippon Large Cap",
        119092: "Axis Bluechip",
        120841: "Kotak Bluechip"
    }
    
    for code, name in key_schemes.items():
        process_and_save_mf_data(code, name)
        
    print("NAV fetching complete.")
