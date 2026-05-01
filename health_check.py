# health_check.py
# Validates pipeline output before every commit
# Fails loudly if data is missing or corrupt

import os
import sys
import pandas as pd
import json
from datetime import datetime, timezone, timedelta

CHECKS_PASSED = 0
CHECKS_FAILED = 0

def check(name, condition, message):
    global CHECKS_PASSED, CHECKS_FAILED
    if condition:
        print(f"  ✅ {name}")
        CHECKS_PASSED += 1
    else:
        print(f"  ❌ {name} — {message}")
        CHECKS_FAILED += 1

def run_checks():
    print(f"\n{'='*50}")
    print(f"global-fuel-watch | health_check.py")
    print(f"{'='*50}\n")

    # 1. Check crude.csv exists and has rows
    crude_path = "data/live/crude.csv"
    check("crude.csv exists", os.path.exists(crude_path), "file missing")

    if os.path.exists(crude_path):
        df = pd.read_csv(crude_path)
        check("crude.csv has rows", len(df) > 0, "file is empty")
        check("crude.csv has expected columns",
              all(c in df.columns for c in ["timestamp","commodity","price_usd","date","unit"]),
              "missing columns")
        check("crude prices are positive",
              (pd.to_numeric(df["price_usd"], errors="coerce") > 0).all(),
              "non-positive prices found")
        check("all 3 commodities present",
              set(df["commodity"].unique()) >= {"brent","wti","natural_gas"},
              f"missing commodities: {df['commodity'].unique()}")

    # 2. Check fx_rates.csv exists and has rows
    fx_path = "data/live/fx_rates.csv"
    check("fx_rates.csv exists", os.path.exists(fx_path), "file missing")

    if os.path.exists(fx_path):
        df = pd.read_csv(fx_path)
        check("fx_rates.csv has rows", len(df) > 0, "file is empty")
        check("fx rates are positive",
              (pd.to_numeric(df["rate"], errors="coerce") > 0).all(),
              "non-positive rates found")
        check("at least 10 FX pairs present",
              df["pair"].nunique() >= 10,
              f"only {df['pair'].nunique()} pairs found")

    # 3. Check global_latest.json exists and is recent
    latest_path = "data/global_latest.json"
    check("global_latest.json exists", os.path.exists(latest_path), "file missing")

    if os.path.exists(latest_path):
        with open(latest_path) as f:
            latest = json.load(f)
        check("global_latest.json has last_updated_utc",
              "last_updated_utc" in latest,
              "missing last_updated_utc key")

        if "last_updated_utc" in latest:
            last = datetime.strptime(latest["last_updated_utc"], "%Y-%m-%d %H:%M:%S")
            last = last.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - last
            check("data is fresh (within 30 min)",
                  age < timedelta(minutes=30),
                  f"last update was {int(age.total_seconds()/60)} min ago")

    # 4. Check logs directory exists
    check("logs/ directory exists", os.path.isdir("logs"), "logs/ missing")

    # Summary
    print(f"\n{'='*50}")
    print(f"Checks passed: {CHECKS_PASSED}")
    print(f"Checks failed: {CHECKS_FAILED}")
    print(f"{'='*50}\n")

    if CHECKS_FAILED > 0:
        print("❌ Health check FAILED — aborting commit.")
        sys.exit(1)
    else:
        print("✅ Health check PASSED — safe to commit.")
        sys.exit(0)

if __name__ == "__main__":
    run_checks()