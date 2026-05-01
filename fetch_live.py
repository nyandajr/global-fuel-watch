# fetch_live.py
# Runs every 10 minutes via GitHub Actions
# Fetches: Brent crude, WTI crude, Natural Gas prices + all FX rates

import requests
import pandas as pd
import os
import json
import time
from datetime import datetime, timezone
from config import FX_PAIRS, DATA_LIVE_DIR, LOGS_DIR

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
AV_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "demo")

def fetch_with_retry(url, retries=3, delay=5):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  Attempt {i+1} failed: {e}")
            time.sleep(delay)
    return None

def append_to_csv(filepath, row: dict):
    df = pd.DataFrame([row])
    header = not os.path.exists(filepath)
    df.to_csv(filepath, mode="a", header=header, index=False)

def log_uptime(status, records):
    append_to_csv(f"{LOGS_DIR}/uptime.csv", {
        "timestamp": TIMESTAMP,
        "job": "fetch_live",
        "status": status,
        "records_fetched": records,
    })

def fetch_commodity(function_name, label):
    print(f"Fetching {label}...")
    url = (f"https://www.alphavantage.co/query"
           f"?function={function_name}&interval=daily&apikey={AV_KEY}")
    data = fetch_with_retry(url)
    if not data or "data" not in data:
        print(f"  [{label}] No data returned.")
        return 0
    latest = data["data"][0]
    append_to_csv(f"{DATA_LIVE_DIR}/crude.csv", {
        "timestamp": TIMESTAMP,
        "commodity": label,
        "price_usd": latest["value"],
        "date": latest["date"],
        "unit": "USD/barrel" if label != "natural_gas" else "USD/MMBtu",
    })
    print(f"  [{label}] {latest['value']} on {latest['date']}")
    return 1

def fetch_fx():
    print("Fetching FX rates...")
    url = "https://open.er-api.com/v6/latest/USD"
    data = fetch_with_retry(url)
    if not data or "rates" not in data:
        print("  [FX] No data returned.")
        return 0
    records = 0
    for pair in FX_PAIRS:
        _, to_cur = pair.split("/")
        rate = data["rates"].get(to_cur)
        if rate:
            append_to_csv(f"{DATA_LIVE_DIR}/fx_rates.csv", {
                "timestamp": TIMESTAMP,
                "pair": pair,
                "rate": rate,
                "base": "USD",
            })
            records += 1
    print(f"  [FX] {records} pairs fetched.")
    return records

def update_global_latest(fx_count):
    with open("data/global_latest.json", "w") as f:
        json.dump({
            "last_updated_utc": TIMESTAMP,
            "commodities_fetched": 3,
            "fx_pairs_fetched": fx_count,
        }, f, indent=2)
    print("  global_latest.json updated.")

def main():
    print(f"\n{'='*50}")
    print(f"global-fuel-watch | fetch_live.py")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"{'='*50}\n")

    total  = fetch_commodity("BRENT", "brent")
    total += fetch_commodity("WTI", "wti")
    total += fetch_commodity("NATURAL_GAS", "natural_gas")
    fx_count = fetch_fx()
    total += fx_count

    update_global_latest(fx_count)
    status = "success" if total > 0 else "failed"
    log_uptime(status, total)

    print(f"\n{'='*50}")
    print(f"Done. Total records: {total} | Status: {status}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()