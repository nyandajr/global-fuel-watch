"""Runs every implemented per-country scraper in scrapers/, writing each
one's real rows to data/pump_prices/<COUNTRY_CODE>.csv.

Only countries with a genuinely verified real data source get a scraper
module here -- see each module's own docstring for how its source was
verified. A country with no scraper simply isn't attempted rather than
having a fake one; config.py's COUNTRIES dict lists all 20 as coverage
targets, but SCRAPERS below is the honest subset actually implemented.

One country's scraper failing (dead link, changed format, network
hiccup) doesn't stop the others -- each runs independently and failures
are logged, not raised, so a single broken source can't take down the
whole run.
"""

import importlib
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scrapers"))
from base_scraper import write_rows  # noqa: E402

# Module name -> country code. Add an entry here once a scraper module
# exists and its scrape() has been verified to return real rows.
SCRAPERS = {
    "UK_beis": "UK",
    "US_eia": "US",
    "FR_dgec": "FR",
}


def run_all():
    total_written = 0
    results = {}
    for module_name, country_code in SCRAPERS.items():
        try:
            module = importlib.import_module(module_name)
            rows = module.scrape()
            n = write_rows(country_code, rows)
            results[country_code] = n
            total_written += n
            print(f"[run_all_scrapers] {country_code}: {n} rows")
        except Exception as e:
            results[country_code] = None
            print(f"[run_all_scrapers] {country_code}: FAILED - {e}")
            traceback.print_exc()

    ok = sum(1 for v in results.values() if v)
    print(f"[run_all_scrapers] {ok}/{len(SCRAPERS)} scrapers succeeded, {total_written} rows written")
    return results


if __name__ == "__main__":
    run_all()
