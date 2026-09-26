"""Norway national average fuel prices, from Statistics Norway's (SSB)
own open PxWebApi -- table 09654, "Prices on engine fuel (NOK per
litres), by petroleum products and month".

Source verified live 2026-09-26: real JSON-stat2 data, "updated":
"2026-09-21", most recent month 2026M08 -- current for a monthly series.
Monthly, not daily/per-station -- this is a national statistical
average, not the highest-frequency signal available for Norway, but it
is the real one SSB itself publishes. Only petrol (Motor gasoline,
leadfree 95 octane) and diesel are in this table -- no LPG/heating_oil.
"""

from base_scraper import fetch, make_row

API_URL = (
    "https://data.ssb.no/api/pxwebapi/v2/tables/09654/data"
    "?lang=en&valueCodes%5BPetroleumProd%5D=*&valueCodes%5BContentsCode%5D=*"
    "&valueCodes%5BTid%5D=top(2)&outputFormat=json-stat2"
)
SOURCE = "https://www.ssb.no/en/statbank/table/09654"

PRODUCT_LABELS = {"031": "petrol", "035": "diesel"}


def scrape():
    data = fetch(API_URL).json()

    product_index = data["dimension"]["PetroleumProd"]["category"]["index"]
    time_index = data["dimension"]["Tid"]["category"]["index"]
    time_labels = data["dimension"]["Tid"]["category"]["label"]
    n_times = len(time_index)

    # JSON-stat2 value array is row-major over dimensions in `id` order
    # (PetroleumProd, ContentsCode, Tid); ContentsCode has size 1 here.
    latest_time_pos = n_times - 1
    latest_month = None
    rows = []
    for code, fuel in PRODUCT_LABELS.items():
        if code not in product_index:
            continue
        product_pos = product_index[code]
        flat_index = product_pos * n_times + latest_time_pos
        price = data["value"][flat_index]
        month_code = [k for k, v in time_index.items() if v == latest_time_pos][0]
        latest_month = time_labels.get(month_code, month_code)
        date = month_code.replace("M", "-") + "-01"
        rows.append(make_row("NO", fuel, round(price, 3), "NOK", "NOK/litre", date, SOURCE))

    if not rows:
        raise ValueError("Norway fuel price API returned no usable rows")
    return rows


if __name__ == "__main__":
    for row in scrape():
        print(row)
