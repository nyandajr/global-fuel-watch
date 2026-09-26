"""VM-side replacement for the GitHub Actions workflow -- run from the VM's
own crontab, not GitHub Actions (same migration already proven on
hormuz-strait-monitor, ea-financial-tracker, and dsn-anomaly-tracker).
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_PATHS = ["data/live/", "data/global_latest.json", "logs/"]
PUMP_DATA_PATHS = ["data/pump_prices/"]

load_dotenv(REPO_DIR / ".env")  # populates ALPHA_VANTAGE_KEY for fetch_live.py's subprocess


def run(*args, check=True):
    return subprocess.run(list(args), cwd=str(REPO_DIR), check=check)


def _last_batch(csv_path):
    """Rows sharing the file's most recent timestamp -- each fetch cycle
    writes one row per commodity/pair, all stamped with the same time."""
    try:
        with open(REPO_DIR / csv_path, newline="") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        return []
    if not rows:
        return []
    latest_ts = rows[-1]["timestamp"]
    return [r for r in rows if r["timestamp"] == latest_ts]


def build_commit_message(is_crude):
    if is_crude:
        batch = _last_batch("data/live/crude.csv")
        by_commodity = {r["commodity"]: r["price_usd"] for r in batch}
        parts = []
        for key, label in [("brent", "Brent"), ("wti", "WTI"), ("natural_gas", "NatGas")]:
            if key in by_commodity:
                parts.append(f"{label} ${float(by_commodity[key]):.2f}")
        return "live: crude update — " + (" | ".join(parts) if parts else "no data")

    batch = _last_batch("data/live/fx_rates.csv")
    by_pair = {r["pair"]: r["rate"] for r in batch}
    parts = [f"{len(batch)} pairs"]
    for pair in ["USD/EUR", "USD/GBP", "USD/CNY"]:
        if pair in by_pair:
            parts.append(f"{pair} {float(by_pair[pair]):,.4f}")
    return "live: fx update — " + " | ".join(parts)


def build_pump_commit_message():
    pump_dir = REPO_DIR / "data" / "pump_prices"
    latest_by_country = {}
    for csv_path in sorted(pump_dir.glob("*.csv")):
        country = csv_path.stem
        with open(csv_path, newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        last_ts = rows[-1]["timestamp"]
        latest_by_country[country] = [r for r in rows if r["timestamp"] == last_ts]

    if not latest_by_country:
        return "data: pump price update — no data"

    sample = []
    for country, rows in list(latest_by_country.items())[:3]:
        petrol = next((r for r in rows if r["fuel_type"] == "petrol"), None)
        if petrol:
            sample.append(f"{country} {petrol['currency']} {float(petrol['price']):.3f}/{petrol['unit'].split('/')[-1]}")
    return f"data: pump price update — {len(latest_by_country)} countries | " + " | ".join(sample)


def sync_with_remote():
    # --hard, not --soft, and BEFORE fetch_live.py runs -- reset --soft only
    # moves HEAD, leaving stale index entries for files this script doesn't
    # explicitly `git add`, which then get silently recommitted on the next
    # force-push. Learned this the hard way on hormuz-strait-monitor.
    run("git", "fetch", "origin", "main")
    run("git", "reset", "--hard", "origin/main")


def git_commit_and_push(paths, message):
    # freddynyanda@proton.me is Fred's real, verified GitHub email --
    # standardizing on it here too (the original workflow used
    # nyandajr@users.noreply.github.com, uncertain whether that noreply
    # variant is actually verified for this account).
    run("git", "config", "user.name", "nyandajr")
    run("git", "config", "user.email", "freddynyanda@proton.me")
    run("git", "add", *paths, check=False)

    diff = run("git", "diff", "--cached", "--quiet", check=False)
    if diff.returncode == 0:
        print("[run_and_push] no changes to commit")
        return

    run("git", "commit", "-m", message)
    run("git", "push", "--force", "origin", "HEAD:main")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fx", action="store_true")
    parser.add_argument("--crude", action="store_true")
    parser.add_argument("--pump", action="store_true")
    args = parser.parse_args()

    sync_with_remote()

    if args.pump:
        run(sys.executable, "run_all_scrapers.py", check=False)
        git_commit_and_push(PUMP_DATA_PATHS, build_pump_commit_message())
        print("[run_and_push] done")
        return

    fetch_args = [sys.executable, "fetch_live.py"]
    if args.fx:
        fetch_args.append("--fx")
    if args.crude:
        fetch_args.append("--crude")
    run(*fetch_args)

    health = run(sys.executable, "health_check.py", check=False)
    if health.returncode != 0:
        print("[run_and_push] health check failed, not committing")
        sys.exit(1)

    git_commit_and_push(DATA_PATHS, build_commit_message(args.crude))
    print("[run_and_push] done")


if __name__ == "__main__":
    main()
