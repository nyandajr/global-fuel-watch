"""US weekly retail gasoline and diesel prices, from EIA's own published
workbooks.

Source verified live 2026-09-26: real .xls files, both showing a most
recent row dated 2026-09-21 -- current, not stale. Only covers petrol and
diesel -- config.py lists kerosene/lpg/natural_gas/heating_oil as
expected US fuels too, but this specific EIA series doesn't publish
those, so this scraper only returns what it actually has real data for.
"""

from datetime import datetime, timedelta

import xlrd
from base_scraper import fetch, make_row

GASOLINE_URL = "https://www.eia.gov/petroleum/gasdiesel/xls/pswrgvwall.xls"
DIESEL_URL = "https://www.eia.gov/petroleum/gasdiesel/xls/psw18vwall.xls"
SOURCE = "https://www.eia.gov/petroleum/gasdiesel/"


def _excel_date(value):
    return (datetime(1899, 12, 30) + timedelta(days=value)).date().isoformat()


def _latest_national_price(xls_bytes):
    wb = xlrd.open_workbook(file_contents=xls_bytes)
    sheet = wb.sheet_by_name("Data 1")
    last = sheet.nrows - 1
    return _excel_date(sheet.cell_value(last, 0)), sheet.cell_value(last, 1)


def scrape():
    gas_date, gas_price = _latest_national_price(fetch(GASOLINE_URL).content)
    diesel_date, diesel_price = _latest_national_price(fetch(DIESEL_URL).content)

    return [
        make_row("US", "petrol", gas_price, "USD", "USD/gallon", gas_date, SOURCE),
        make_row("US", "diesel", diesel_price, "USD", "USD/gallon", diesel_date, SOURCE),
    ]


if __name__ == "__main__":
    for row in scrape():
        print(row)
