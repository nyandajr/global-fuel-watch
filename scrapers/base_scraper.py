"""Shared utilities for the per-country fuel-price scrapers.

Each scraper module implements one function, `scrape()`, returning a list
of row dicts matching PUMP_PRICE_FIELDS. Writing to disk and the common
HTTP-fetch pattern live here so individual scrapers stay small and only
contain the source-specific parsing logic.
"""

import csv
import os
import sys
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DATA_PUMP_DIR

# Every row written to data/pump_prices/<COUNTRY_CODE>.csv follows this
# schema, matching the timestamp/date/unit convention already used in
# data/live/crude.csv.
PUMP_PRICE_FIELDS = ["timestamp", "country", "fuel_type", "price", "currency", "unit", "date", "source"]

REQUEST_TIMEOUT = 20
USER_AGENT = "global-fuel-watch/1.0 (+https://github.com/nyandajr/global-fuel-watch)"


def fetch(url, **kwargs):
    """GET a URL with a sane timeout and identifying User-Agent, raising on
    HTTP errors so a broken source fails loudly instead of silently writing
    nothing (per health_check.py's fail-loud convention in this repo).
    """
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers, **kwargs)
    resp.raise_for_status()
    return resp


def make_row(country_code, fuel_type, price, currency, unit, date, source):
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "country": country_code,
        "fuel_type": fuel_type,
        "price": price,
        "currency": currency,
        "unit": unit,
        "date": date,
        "source": source,
    }


def write_rows(country_code, rows):
    """Appends rows to data/pump_prices/<COUNTRY_CODE>.csv, writing the
    header only if the file doesn't exist yet.
    """
    if not rows:
        return 0

    os.makedirs(DATA_PUMP_DIR, exist_ok=True)
    path = os.path.join(DATA_PUMP_DIR, f"{country_code}.csv")
    is_new = not os.path.exists(path)

    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PUMP_PRICE_FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)

    return len(rows)
