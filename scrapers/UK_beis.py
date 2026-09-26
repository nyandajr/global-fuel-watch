"""UK weekly road fuel prices, from the government's own published dataset.

Source verified live 2026-08-25: a real CSV, updated weekly (this file's
own most recent row was dated the same day it was checked), going back to
2018. Only covers petrol and diesel -- config.py lists heating_oil and lpg
as expected UK fuels too, but this source doesn't publish those, so this
scraper only returns the two it actually has data for rather than
fabricating the rest.
"""

import csv
import io
from datetime import datetime

from base_scraper import fetch, make_row

CSV_URL = "https://assets.publishing.service.gov.uk/media/6a8c63a808705e34a95daa78/CSV__2018_-__.csv"
SOURCE = "https://www.gov.uk/government/statistical-data-sets/oil-and-petroleum-products-weekly-statistics"

# CSV columns: Date, ULSP pump price (pence/litre), ULSD pump price
# (pence/litre), plus duty/VAT columns this scraper doesn't need.
PETROL_COL = "ULSP (Ultra low sulphur unleaded petrol) Pump price in pence/litre"
DIESEL_COL = "ULSD (Ultra low sulphur diesel) Pump price in pence/litre"


def scrape():
    resp = fetch(CSV_URL)
    # The file is UTF-8 with a BOM; utf-8-sig strips it cleanly.
    reader = csv.DictReader(io.StringIO(resp.content.decode("utf-8-sig")))
    rows = list(reader)
    if not rows:
        raise ValueError("UK fuel price CSV returned no rows")

    latest = rows[-1]
    date = datetime.strptime(latest["Date"], "%d/%m/%Y").date().isoformat()

    return [
        make_row("UK", "petrol", float(latest[PETROL_COL]) / 100, "GBP", "GBP/litre", date, SOURCE),
        make_row("UK", "diesel", float(latest[DIESEL_COL]) / 100, "GBP", "GBP/litre", date, SOURCE),
    ]


if __name__ == "__main__":
    for row in scrape():
        print(row)
