"""Brazil station-level fuel prices, from ANP's (Agência Nacional do
Petróleo) own open-data feed -- a rolling last-4-weeks CSV of every
surveyed station's collected price.

Source verified live 2026-09-26: real per-station CSV data, most recent
collection date 31/08/2026. National average computed here for the most
recent collection date present, from GASOLINA (regular petrol) and
DIESEL (regular diesel, not the S10 low-sulfur variant, to keep one
petrol/diesel figure per the rest of this repo's convention). LPG isn't
in this feed, so only petrol/diesel are returned.
"""

import csv
import io
from statistics import mean

from base_scraper import fetch, make_row

GASOLINE_CSV_URL = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv"
DIESEL_CSV_URL = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/qus/ultimas-4-semanas-diesel-gnv.csv"
SOURCE = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos"


def _brl(value_str):
    return float(value_str.strip().replace(",", "."))


def _latest_average(csv_url, product_name):
    resp = fetch(csv_url)
    text = resp.content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = [r for r in reader if r.get("Produto") == product_name]
    if not rows:
        raise ValueError(f"No '{product_name}' rows in {csv_url}")

    # Keep only the most recent collection date present, so the figure
    # reflects "current" price rather than averaging over 4 weeks of
    # movement.
    dates = [r["Data da Coleta"] for r in rows if r.get("Data da Coleta")]
    latest_date = max(dates, key=lambda d: d[6:] + d[3:5] + d[0:2])  # DD/MM/YYYY -> sortable
    latest_rows = [r for r in rows if r["Data da Coleta"] == latest_date]

    prices = [_brl(r["Valor de Venda"]) for r in latest_rows if r.get("Valor de Venda")]
    return round(mean(prices), 3), latest_date


def scrape():
    petrol_price, petrol_date = _latest_average(GASOLINE_CSV_URL, "GASOLINA")
    diesel_price, diesel_date = _latest_average(DIESEL_CSV_URL, "DIESEL")

    def iso(d):  # DD/MM/YYYY -> YYYY-MM-DD
        dd, mm, yyyy = d.split("/")
        return f"{yyyy}-{mm}-{dd}"

    return [
        make_row("BR", "petrol", petrol_price, "BRL", "BRL/litre", iso(petrol_date), SOURCE),
        make_row("BR", "diesel", diesel_price, "BRL", "BRL/litre", iso(diesel_date), SOURCE),
    ]


if __name__ == "__main__":
    for row in scrape():
        print(row)
