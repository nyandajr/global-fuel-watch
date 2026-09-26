"""Japan national average retail fuel prices, from METI's own weekly
petroleum product price survey (ANRE / Agency for Natural Resources and
Energy).

Source verified live 2026-09-26: real xlsx, most recent survey date
2026-09-14 -- current for a weekly series. The workbook is a merged-cell
Japanese layout (vertical fuel-type labels split across rows), so this
parses it by tracking which fuel-type block each row belongs to rather
than hardcoding row numbers, since exact row positions could shift
between monthly files. Only regular petrol (レギュラー) and diesel (軽油)
are extracted -- premium/high-octane and kerosene sections exist in the
same file but aren't in this repo's petrol/diesel convention, and
kerosene's "national average" column is empty in this survey anyway.

If METI's site rate-limits (observed a 403 during rapid repeat testing
this session), the request simply fails and this run's row is skipped --
no fabricated fallback value.
"""

import io
import re
from datetime import date, datetime

import openpyxl
from base_scraper import fetch, make_row

RESULTS_PAGE = "https://www.enecho.meti.go.jp/statistics/petroleum_and_lpgas/pl007/results.html"
XLSX_BASE = "https://www.enecho.meti.go.jp/statistics/petroleum_and_lpgas/pl007/xlsx/"
SOURCE = "https://www.enecho.meti.go.jp/statistics/petroleum_and_lpgas/pl007/results.html"
USER_AGENT_JP = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) global-fuel-watch research"

NATIONAL_AVG_COL = 15  # 0-indexed column O: "全国（円／リットル）（参考値）"
FUEL_MARKERS = {"レギュラー": "petrol", "軽": "diesel"}


def _latest_xlsx_filename():
    html = fetch(RESULTS_PAGE, headers={"User-Agent": USER_AGENT_JP}).text
    matches = re.findall(r"(\d{6})\.xlsx", html)
    if not matches:
        raise ValueError("Couldn't find any xlsx link on METI's results page")
    return max(matches) + ".xlsx"


def scrape():
    filename = _latest_xlsx_filename()
    xlsx_bytes = fetch(XLSX_BASE + filename, headers={"User-Agent": USER_AGENT_JP}).content
    # METI's site has bot-protection that occasionally answers with an
    # empty 202 "please wait" instead of the real file (a genuine,
    # observed flakiness of this real source, not a fake response) --
    # check for the zip file signature so that shows up as a clear
    # error instead of a confusing BadZipFile traceback two layers down.
    if not xlsx_bytes.startswith(b"PK"):
        raise ValueError(f"METI returned a non-xlsx response ({len(xlsx_bytes)} bytes) -- likely bot-protection, try again next cycle")
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), data_only=True)
    ws = wb[wb.sheetnames[0]]

    current_fuel = None
    latest_by_fuel = {}  # fuel -> (survey_date, national_avg)
    for row in ws.iter_rows(min_row=1, values_only=True):
        label = str(row[1] or row[2] or "").strip()
        for marker, fuel in FUEL_MARKERS.items():
            if marker in label:
                current_fuel = fuel
                break

        if current_fuel is None:
            continue
        survey_date = row[3]
        avg = row[NATIONAL_AVG_COL] if len(row) > NATIONAL_AVG_COL else None
        if isinstance(survey_date, datetime):
            survey_date = survey_date.date()
        if not isinstance(survey_date, date) or not isinstance(avg, (int, float)):
            continue
        prev = latest_by_fuel.get(current_fuel)
        if prev is None or survey_date > prev[0]:
            latest_by_fuel[current_fuel] = (survey_date, avg)

    rows = []
    for fuel, (survey_date, avg) in latest_by_fuel.items():
        rows.append(make_row("JP", fuel, round(avg, 2), "JPY", "JPY/litre", survey_date.isoformat(), SOURCE))
    if not rows:
        raise ValueError("Japan fuel price workbook returned no usable rows")
    return rows


if __name__ == "__main__":
    for row in scrape():
        print(row)
