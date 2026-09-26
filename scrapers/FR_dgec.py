"""France station-level fuel prices, from the government's own open-data
feed (prix-carburants.gouv.fr / donnees.roulez-eco.fr).

Source verified live 2026-09-26: a real zip containing one XML file with
every French filling station's current prices per fuel grade, last
modified today. National average computed here from all reporting
stations for the two most common grades -- Gazole (diesel) and E10
(unleaded 95, the standard petrol grade, sold at nearly every station,
unlike SP98/E85 which config.py doesn't even list as expected French
fuels). LPG isn't in this feed at all, so only petrol/diesel are
returned rather than fabricating the rest.
"""

import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from statistics import mean

from base_scraper import fetch, make_row

ZIP_URL = "https://donnees.roulez-eco.fr/opendata/instantane"
SOURCE = "https://www.prix-carburants.gouv.fr"

FUEL_IDS = {"1": "diesel", "5": "petrol"}  # Gazole, E10


def scrape():
    resp = fetch(ZIP_URL)
    z = zipfile.ZipFile(io.BytesIO(resp.content))
    xml_bytes = z.read(z.namelist()[0])
    root = ET.fromstring(xml_bytes)

    prices_by_fuel = {"diesel": [], "petrol": []}
    latest_date_by_fuel = {"diesel": None, "petrol": None}

    for prix in root.iter("prix"):
        fuel = FUEL_IDS.get(prix.get("id"))
        if fuel is None:
            continue
        try:
            value = float(prix.get("valeur"))
        except (TypeError, ValueError):
            continue
        if value <= 0:
            continue
        prices_by_fuel[fuel].append(value)
        maj = prix.get("maj", "")
        if maj and (latest_date_by_fuel[fuel] is None or maj > latest_date_by_fuel[fuel]):
            latest_date_by_fuel[fuel] = maj

    rows = []
    for fuel, prices in prices_by_fuel.items():
        if not prices:
            continue
        date = (latest_date_by_fuel[fuel] or datetime.now().isoformat())[:10]
        rows.append(make_row("FR", fuel, round(mean(prices), 3), "EUR", "EUR/litre", date, SOURCE))
    if not rows:
        raise ValueError("France fuel price feed returned no usable rows")
    return rows


if __name__ == "__main__":
    for row in scrape():
        print(row)
