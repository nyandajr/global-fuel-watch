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
| 🇨🇦 Canada | Petrol | [Statistics Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000101) — national monthly average |
| 🇧🇷 Brazil | Petrol, Diesel | [ANP open data](https://www.gov.br/anp) — rolling 4-week, per-station |
| 🇲🇽 Mexico | Petrol, Diesel | Government public price-reporting service — per-station |
| 🇮🇹 Italy | Petrol, Diesel, LPG | [MIMIT Osservatorio Prezzi Carburanti](https://www.mimit.gov.it) — ~93k stations, daily |
| 🇳🇴 Norway | Petrol, Diesel | [Statistics Norway (SSB)](https://www.ssb.no/en/statbank/table/09654) — national monthly average |
| 🇯🇵 Japan | Petrol, Diesel | [METI/ANRE weekly survey](https://www.enecho.meti.go.jp) — has real but occasionally flaky bot-protection, may skip a cycle |

**Confirmed no public source exists** (8 countries) — subsidized or
administratively-fixed prices published only as press releases/PDFs, no
machine-readable feed found after real investigation: Saudi Arabia, UAE,
Kuwait, Iran, India, China, Indonesia, Philippines.

**Real source exists, needs a free API key neither of us can register
unsupervised** (2 countries): Germany ([Tankerkönig](https://creativecommons.tankerkoenig.de/)), South Korea ([Opinet](https://www.opinet.co.kr/user/custapi/openApiNew.do)) — both instant/auto-approved signups, just need a human to do them.

**Real source exists, currently unreachable from this network** (1
country): Netherlands (CBS StatLine) — confirmed blocked/timing out on
repeated attempts, not a dead endpoint necessarily, worth retrying from
a different network.

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