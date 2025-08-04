# Investing Oracle

A Python-based stock analysis tool that calculates intrinsic value estimates for companies using historical earnings data and Phil Town's Rule #1 investing principles.

## Features

- Scrapes the **Nasdaq-100** companies from Wikipedia.
- Retrieves historical **EPS data** (e.g., from MacroTrends).
- Calculates:
  - **EPS CAGR**
  - **Future EPS**
  - **Estimated future stock price**
  - **Sticker price** (discounted intrinsic value)
  - **Margin of safety price**
- Fetches current stock price using `yfinance`.
- Filters companies that are trading below their margin of safety.
- Outputs results to CSV files for further analysis.

## Output Files

- `nasdaq_intrinsic_values.csv`: Full dataset with calculated values.
- `undervalued_companies.csv`: Companies trading below margin of safety.

## Requirements

pip install the following:

pandas

requests

beautifulsoup4

yfinance

tabulate

## Methodology
The approach is based on Phil Town’s "Rule #1" investing strategy, which focuses on buying great companies at attractive prices based on conservative growth estimates.

## Various
Be a bit patient when using get_nasdaq_companies_and_eps.py as it will take
50 minutes to complete. The reason is that there is a nasty 15 wait there
between the calls to get the EPS because without it, the site blocks access.

Disclaimer
This tool is for educational and informational purposes only and should not be considered financial advice. Always do your own research and consult a financial advisor before making investment decisions.

Contact
Created by George Gkekis.
Feel free to contribute, fork, or open an issue!
