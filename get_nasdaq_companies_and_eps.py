import pandas as pd
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

def fetch_eps(symbol, year):
    url = f"https://www.macrotrends.net/stocks/charts/{symbol}/{symbol.lower()}/eps-earnings-per-share-diluted"

# Use multiple agents to avoid getting blocked
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)...",
    ]

    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"[{symbol}] Request failed: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "historical_data_table"})

    if not table:
        print(f"[{symbol}] EPS table not found.")
        return None

    for row in table.find_all("tr"): # Iterate over every HTML row <tr>
        # Find all table cells <td>
        # cols[0] is expected to be the year.
        # cols[1] is expected to be the EPS value.
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols and cols[0] == str(year):
            return cols[1]

    print(f"[{symbol}] EPS for {year} not found.")
    return None

def get_nasdaq_companies():
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    tables = pd.read_html(url)

    nasdaq_table = None
    for table in tables:
        if 'Company' in table.columns and 'Ticker' in table.columns:
            nasdaq_table = table
            break

    if nasdaq_table is not None:
        # Only keep Company and ticker columns
        #nasdaq_table = nasdaq_table[['Company', 'Ticker']]
        print(tabulate(nasdaq_table, headers='keys', tablefmt='fancy_grid', showindex=True))
        print(f"\nTotal number of companies: {len(nasdaq_table)}")
    else:
        print("Could not find the Nasdaq-100 table.")
    return nasdaq_table

# Final_year will be current year for the latest calculation
# It will be a year in the past for backtesting purposes.
final_year = datetime.now().year
target_years = [final_year - 11, final_year - 1]
nasdaq = get_nasdaq_companies()
results = []

for _, row in nasdaq.iterrows():
    ticker = row['Ticker']
    company = row['Company']
    eps_data = {}

    for y in target_years:
        eps = fetch_eps(ticker, y)
        eps_data[y] = eps
        time.sleep(15)  # Avoid blocking
        # TODO: Figure out sweet spot between being fast and not being blocked

    print(f"{ticker}: EPS {target_years[0]} = {eps_data[target_years[0]]}, EPS {target_years[1]} = {eps_data[target_years[1]]}")
    results.append({
        'Company': company,
        'Ticker': ticker,
        'EPS_initial': eps_data[target_years[0]],
        'EPS_latest': eps_data[target_years[1]],
    })

df_results = pd.DataFrame(results)
df_results.to_csv("nasdaq_eps_data.csv", index=False)
print("\nSaved results to nasdaq_eps_data.csv")
