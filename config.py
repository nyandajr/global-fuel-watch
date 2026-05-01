FUEL_TYPES = [
    "petrol",
    "diesel",
    "kerosene",
    "lpg",
    "natural_gas",
    "heating_oil",
]

COUNTRIES = {
    "US": {"name": "United States", "region": "Americas", "currency": "USD", "fx_pair": "USD/USD", "fuels": ["petrol", "diesel", "kerosene", "lpg", "natural_gas", "heating_oil"], "source": "https://www.eia.gov/petroleum/gasdiesel/", "frequency": "weekly"},
    "CA": {"name": "Canada", "region": "Americas", "currency": "CAD", "fx_pair": "USD/CAD", "fuels": ["petrol", "diesel", "lpg", "natural_gas", "heating_oil"], "source": "https://natural-resources.canada.ca/energy/fuel-prices/4593", "frequency": "weekly"},
    "BR": {"name": "Brazil", "region": "Americas", "currency": "BRL", "fx_pair": "USD/BRL", "fuels": ["petrol", "diesel", "lpg", "natural_gas"], "source": "https://www.gov.br/anp", "frequency": "weekly"},
    "MX": {"name": "Mexico", "region": "Americas", "currency": "MXN", "fx_pair": "USD/MXN", "fuels": ["petrol", "diesel", "lpg"], "source": "https://www.cre.gob.mx", "frequency": "weekly"},
    "UK": {"name": "United Kingdom", "region": "Europe", "currency": "GBP", "fx_pair": "USD/GBP", "fuels": ["petrol", "diesel", "heating_oil", "lpg"], "source": "https://www.gov.uk/government/statistical-data-sets/oil-and-petroleum-products-weekly-statistics", "frequency": "weekly"},
    "DE": {"name": "Germany", "region": "Europe", "currency": "EUR", "fx_pair": "USD/EUR", "fuels": ["petrol", "diesel", "heating_oil", "natural_gas"], "source": "https://www.destatis.de", "frequency": "weekly"},
    "FR": {"name": "France", "region": "Europe", "currency": "EUR", "fx_pair": "USD/EUR", "fuels": ["petrol", "diesel", "heating_oil", "lpg"], "source": "https://www.prix-carburants.gouv.fr", "frequency": "weekly"},
    "IT": {"name": "Italy", "region": "Europe", "currency": "EUR", "fx_pair": "USD/EUR", "fuels": ["petrol", "diesel", "lpg", "natural_gas"], "source": "https://dgsaie.mise.gov.it", "frequency": "weekly"},
    "NL": {"name": "Netherlands", "region": "Europe", "currency": "EUR", "fx_pair": "USD/EUR", "fuels": ["petrol", "diesel", "lpg", "natural_gas"], "source": "https://www.cbs.nl", "frequency": "weekly"},
    "NO": {"name": "Norway", "region": "Europe", "currency": "NOK", "fx_pair": "USD/NOK", "fuels": ["petrol", "diesel", "heating_oil"], "source": "https://www.norskpetroleum.no", "frequency": "weekly"},
    "SA": {"name": "Saudi Arabia", "region": "Middle East", "currency": "SAR", "fx_pair": "USD/SAR", "fuels": ["petrol", "diesel", "lpg"], "source": "https://www.aramco.com", "frequency": "monthly"},
    "UAE": {"name": "United Arab Emirates", "region": "Middle East", "currency": "AED", "fx_pair": "USD/AED", "fuels": ["petrol", "diesel"], "source": "https://www.moccae.gov.ae", "frequency": "monthly"},
    "KW": {"name": "Kuwait", "region": "Middle East", "currency": "KWD", "fx_pair": "USD/KWD", "fuels": ["petrol", "diesel", "lpg"], "source": "https://www.mew.gov.kw", "frequency": "monthly"},
    "IR": {"name": "Iran", "region": "Middle East", "currency": "IRR", "fx_pair": "USD/IRR", "fuels": ["petrol", "diesel", "lpg", "natural_gas"], "source": "https://www.opec.org", "frequency": "monthly"},
    "IN": {"name": "India", "region": "Asia", "currency": "INR", "fx_pair": "USD/INR", "fuels": ["petrol", "diesel", "lpg", "kerosene"], "source": "https://ppac.gov.in", "frequency": "daily"},
    "CN": {"name": "China", "region": "Asia", "currency": "CNY", "fx_pair": "USD/CNY", "fuels": ["petrol", "diesel", "lpg", "natural_gas"], "source": "https://www.ndrc.gov.cn", "frequency": "monthly"},
    "JP": {"name": "Japan", "region": "Asia", "currency": "JPY", "fx_pair": "USD/JPY", "fuels": ["petrol", "diesel", "kerosene", "lpg"], "source": "https://www.enecho.meti.go.jp", "frequency": "weekly"},
    "KR": {"name": "South Korea", "region": "Asia", "currency": "KRW", "fx_pair": "USD/KRW", "fuels": ["petrol", "diesel", "lpg", "kerosene"], "source": "https://www.knoc.co.kr", "frequency": "weekly"},
    "ID": {"name": "Indonesia", "region": "Asia", "currency": "IDR", "fx_pair": "USD/IDR", "fuels": ["petrol", "diesel", "lpg", "kerosene"], "source": "https://www.pertamina.com", "frequency": "monthly"},
    "PH": {"name": "Philippines", "region": "Asia", "currency": "PHP", "fx_pair": "USD/PHP", "fuels": ["petrol", "diesel", "lpg", "kerosene"], "source": "https://www.doe.gov.ph", "frequency": "weekly"},
}

FX_PAIRS = list(set(
    c["fx_pair"] for c in COUNTRIES.values()
    if c["fx_pair"] != "USD/USD"
))

LIVE_SOURCES = {
    "brent":       "https://www.alphavantage.co/query?function=BRENT&interval=daily",
    "wti":         "https://www.alphavantage.co/query?function=WTI&interval=daily",
    "natural_gas": "https://www.alphavantage.co/query?function=NATURAL_GAS&interval=daily",
}

DATA_LIVE_DIR        = "data/live"
DATA_PUMP_DIR        = "data/pump_prices"
DATA_PREDICTIONS_DIR = "data/predictions"
LOGS_DIR             = "logs"
GLOBAL_LATEST_FILE   = "data/global_latest.json"

FETCH_INTERVAL_MINUTES = 10
SCRAPE_HOUR_UTC        = 6