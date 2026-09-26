"""Canada national average gasoline price, from Statistics Canada's own
open Web Data Service -- table 18-10-0001-01, monthly average retail
prices for selected petroleum products.

Source verified live 2026-09-26: real CSV data (via StatCan's
getFullTableDownloadCSV API, which returns a zip URL), national ("GEO"=
"Canada") rows run through 2026-08 -- current for a monthly series. Only
"Regular unleaded gasoline at self service filling stations" has a
national-level aggregate in this table; diesel/heating oil are only
broken out per-city in this specific dataset, so only petrol is returned
here rather than guessing at a different table.
"""

import csv
import io
import zipfile

from base_scraper import fetch, make_row

TABLE_LOOKUP_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/18100001/en"
SOURCE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000101"

FUEL_TYPE_LABEL = "Regular unleaded gasoline at self service filling stations"


def scrape():
    lookup = fetch(TABLE_LOOKUP_URL).json()
    zip_url = lookup["object"]

    zip_bytes = fetch(zip_url).content
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    csv_name = next(n for n in z.namelist() if n.lower().endswith(".csv") and "metadata" not in n.lower())
    text = z.read(csv_name).decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    latest = None
    for row in reader:
        if row.get("GEO") != "Canada" or row.get("Type of fuel") != FUEL_TYPE_LABEL:
            continue
        if latest is None or row["REF_DATE"] > latest["REF_DATE"]:
            latest = row

    if latest is None:
        raise ValueError("Canada fuel price table returned no national gasoline rows")

    price_cents_per_litre = float(latest["VALUE"])
    return [
        make_row("CA", "petrol", round(price_cents_per_litre / 100, 3), "CAD", "CAD/litre", latest["REF_DATE"] + "-01", SOURCE),
    ]


if __name__ == "__main__":
    for row in scrape():
        print(row)
