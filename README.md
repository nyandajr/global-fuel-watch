# 🌍 global-fuel-watch

> Real-time crude oil and FX tracking, plus real per-country retail
> petrol/diesel prices where a genuine government or statistical-agency
> source exists — not fabricated for the countries that don't have one.

![Last Update](https://img.shields.io/github/last-commit/nyandajr/global-fuel-watch?label=last%20update&color=green)
![License](https://img.shields.io/github/license/nyandajr/global-fuel-watch)

**A note on this README's history:** it used to claim full petrol/diesel/
LPG coverage across 20 countries. That was never true — 19 of the 21
per-country scraper files were completely empty placeholders; only crude
oil and FX were ever real. Rather than quietly deleting the claim, it's
being fixed the honest way: implementing the scrapers for real, one
verified source at a time, and listing exactly what's actually live
below.

---

## 🔴 Live Data

| Commodity | Latest Price | Unit |
|---|---|---|
| Brent Crude | $113.89 | USD/barrel |
| WTI Crude | $99.89 | USD/barrel |
| Natural Gas | $2.72 | USD/MMBtu |

> Updated every 10 minutes via GitHub Actions. See [data/live/crude.csv](data/live/crude.csv)

---

## 🌐 Retail Pump Price Coverage

**Live now** — each backed by a real, verified government or
statistical-agency source (see the matching `scrapers/<CODE>_*.py` for
exactly which one and when it was verified):

| Country | Fuels | Source |
|---|---|---|
| 🇬🇧 UK | Petrol, Diesel | [gov.uk weekly road fuel prices](https://www.gov.uk/government/statistical-data-sets/oil-and-petroleum-products-weekly-statistics) |
| 🇺🇸 US | Petrol, Diesel | [EIA weekly retail prices](https://www.eia.gov/petroleum/gasdiesel/) |
| 🇫🇷 France | Petrol, Diesel | [prix-carburants.gouv.fr](https://www.prix-carburants.gouv.fr) — real-time, every filling station in France |

**Not yet implemented** (17 countries): Canada, Brazil, Mexico, Germany,
Italy, Netherlands, Norway, Saudi Arabia, UAE, Kuwait, Iran, India,
China, Japan, South Korea, Indonesia, Philippines. `config.py` lists a
candidate source for each, but those are unverified starting points, not
confirmed working endpoints — being worked through one verified source
at a time rather than assumed.

---

## ⛽ Fuel Types

Petrol and diesel are the two fuels covered everywhere data exists.
Kerosene, LPG, natural gas and heating oil are tracked only where a
country's real source actually publishes them (see each scraper's own
docstring) — never backfilled with a guess.

---

## 🏗️ Architecture

Self-hosted VM cron (not GitHub Actions — sub-hourly schedule triggers
proved unreliable across this whole portfolio), same pattern as every
other tracker in this account:

- `fetch_live.py` — crude oil (Brent/WTI/natural gas) and FX rates
- `run_all_scrapers.py` — every implemented per-country pump-price
  scraper in `scrapers/`, one failure doesn't stop the others
- `vm_automation/run_and_push.py` — `--crude` / `--fx` / `--pump`,
  each syncs, runs, and force-pushes real data with a content-aware
  commit message