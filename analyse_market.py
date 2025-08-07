import argparse
import pandas as pd
from datetime import datetime
from get_nasdaq_companies_and_eps import get_eps_for_companies
from calculate_intrinsic_value import calculate_value

def main():
    parser = argparse.ArgumentParser(description="Run investing analysis pipeline")
    parser.add_argument('--backtest', action='store_true', help="Enable backtest mode")
    parser.add_argument('--final_year', type=int, default=datetime.now().year, help="Start date for backtest")
    parser.add_argument('--years_back', type=int, default=10, help="How many years back to simulate")

    args = parser.parse_args()
    # Validate start date
    if args.backtest and not args.final_year:
        parser.error("--final_year is required when --backtest is set")


    eps_results = get_eps_for_companies(args.final_year, args.years_back)
    calculate_value(eps_results, args.backtest, args.final_year, args.years_back)

if __name__ == "__main__":
    main()
