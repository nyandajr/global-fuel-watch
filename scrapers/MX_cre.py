"""Mexico station-level fuel prices, from the government's own public
price-reporting service (successor to CRE's original portal, now under
CNE -- Comisión Nacional de Energía).

Source verified live 2026-09-26: real per-station XML feed of current
prices (regular/premium/diesel), officially linked from the government's
own consumer price-comparison page. National average computed here for
"regular" (petrol) and diesel; "premium" isn't in this repo's fuel-type
list so it's not returned. LPG isn't in this feed either.
"""

import xml.etree.ElementTree as ET
from statistics import mean

from base_scraper import fetch, make_row

PRICES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/prices"
SOURCE = "https://publicacionexterna.azurewebsites.net/publicaciones/prices"

FUEL_TAGS = {"regular": "petrol", "diesel": "diesel"}


def scrape():
    resp = fetch(PRICES_URL)
    root = ET.fromstring(resp.content)

    prices_by_fuel = {"petrol": [], "diesel": []}
    for place in root.findall("place"):
        for gas_price in place.findall("gas_price"):
            fuel = FUEL_TAGS.get(gas_price.get("type"))
            if fuel is None:
                continue
            try:
                value = float(gas_price.text)
            except (TypeError, ValueError):
                continue
            if value > 0:
                prices_by_fuel[fuel].append(value)

    from datetime import date
    today = date.today().isoformat()
    rows = []
    for fuel, prices in prices_by_fuel.items():
        if not prices:
            continue
        rows.append(make_row("MX", fuel, round(mean(prices), 3), "MXN", "MXN/litre", today, SOURCE))
    if not rows:
        raise ValueError("Mexico fuel price feed returned no usable rows")
    return rows


if __name__ == "__main__":
    for row in scrape():
        print(row)
