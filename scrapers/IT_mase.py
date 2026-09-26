"""Italy station-level fuel prices, from MIMIT's (Ministero delle Imprese
e del Made in Italy) Osservatorio Prezzi Carburanti open-data feed.

Source verified live 2026-09-26: a real ~93k-row `|`-delimited CSV of
every station's current price per fuel/brand variant, dated the day of
extraction. National average computed here from the base (non-branded)
grades only -- "Benzina" (petrol), "Gasolio" (diesel) and "GPL" (lpg) --
since branded premium variants (V-Power, HVO, etc.) would skew a
national average away from what most stations actually charge. "Metano"
(natural gas/CNG) is in the feed too, but it's priced per kg there, not
per litre like the others, so it's left out rather than mislabeling its
unit.
"""

import csv
import io
from statistics import mean

from base_scraper import fetch, make_row

CSV_URL = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
SOURCE = "https://www.mimit.gov.it/it/open-data/elenco-open-data/carburanti-prezzi-praticati-e-anagrafica-degli-impianti"

FUEL_NAMES = {"Benzina": "petrol", "Gasolio": "diesel", "GPL": "lpg"}


def scrape():
    resp = fetch(CSV_URL)
    text = resp.content.decode("utf-8", errors="replace")
    lines = text.splitlines()

    extraction_date = lines[0].replace("Estrazione del ", "").strip() if lines else None
    reader = csv.DictReader(io.StringIO("\n".join(lines[1:])), delimiter="|")

    prices_by_fuel = {v: [] for v in FUEL_NAMES.values()}
    for row in reader:
        fuel = FUEL_NAMES.get(row.get("descCarburante"))
        if fuel is None:
            continue
        try:
            value = float(row["prezzo"])
        except (KeyError, ValueError):
            continue
        if value > 0:
            prices_by_fuel[fuel].append(value)

    rows = []
    for fuel, prices in prices_by_fuel.items():
        if not prices:
            continue
        rows.append(make_row("IT", fuel, round(mean(prices), 3), "EUR", "EUR/litre", extraction_date, SOURCE))
    if not rows:
        raise ValueError("Italy fuel price feed returned no usable rows")
    return rows


if __name__ == "__main__":
    for row in scrape():
        print(row)
