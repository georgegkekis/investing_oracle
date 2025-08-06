import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def filter_undervalued_companies(df):
    """
    Filters companies where the current stock price is less than or equal to 115% of the Margin of Safety (MOS) price.
    """
    current_price_col = next((col for col in df.columns if col.startswith("Price")), None)

    # Filter companies where current price <= 115% of MOS price
    undervalued = df[df[current_price_col] <= 1.15 * df["MOS_Price"]]
    return undervalued

def get_stock_price(ticker, date_str=None):
    """
    Get the stock closing price for a given ticker on a specified date.
    If the date is a weekend, fallback to the previous Friday.

    Parameters:
        ticker (str): The stock ticker symbol.
        date_str (str): The target date in 'YYYY-MM-DD' format. Defaults to today.

    Returns:
        float or None: Closing price on the valid trading day, or None if not found.
    """
    if date_str is None:
        date = datetime.today().date()
    else:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Adjust if the date is a weekend
    if date.weekday() == 5:      # Saturday
        date -= timedelta(days=1)
    elif date.weekday() == 6:    # Sunday
        date -= timedelta(days=2)

    start = date - timedelta(days=2)
    end = date + timedelta(days=1)

    data = yf.download(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), progress=False, auto_adjust=True)

    if not data.empty:
        # Try to find the closest available date on or before the target date
        data = data.sort_index()
        available_dates = data.index.strftime('%Y-%m-%d')
        if date.strftime('%Y-%m-%d') in available_dates:
            close_price = data.loc[data.index == pd.to_datetime(date), 'Close'].iloc[0]
        else:
            close_price = data['Close'].iloc[-1]  # fallback to the most recent available

        print(f"{ticker} closing price on {date}: ${float(close_price.iloc[0]):.2f}")
        return float(close_price.iloc[0]), date
    else:
        print(f"No data found for {ticker} near {date}")
        return None, date

def safe_float(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except:
        return None

def calculate_intrinsic_value(eps_old, eps_new, years=10, pe_ratio=30, discount_rate=0.15):
    try:
        eps_old = safe_float(eps_old)
        eps_new = safe_float(eps_new)

        if eps_old <= 0 or eps_new <= 0:
            return None  # Invalid for CAGR

        cagr = (eps_new / eps_old) ** (1 / years) - 1
        future_eps = eps_new * (1 + cagr) ** years
        future_price = future_eps * pe_ratio
        sticker_price = future_price / ((1 + discount_rate) ** years)
        mos_price = sticker_price * 0.5

        return {
            "EPS_CAGR": round(cagr * 100, 2),
            "Future_EPS": round(future_eps, 2),
            "Future_Price": round(future_price, 2),
            "Sticker_Price": round(sticker_price, 2),
            "MOS_Price": round(mos_price, 2),
        }
    except Exception as e:
        print(f"Exception:{e}")
        return None

def sort_by_mos_difference(df):
    """
    Sort the DataFrame by the percentage difference between Current Price and MOS Price.

    Percentage Difference = ((MOS_Price - Current_price) / Current_price) * 100

    Parameters:
        df (pd.DataFrame): The input DataFrame with at least 'Current_price' and 'MOS_Price' columns.

    Returns:
        pd.DataFrame: A new DataFrame sorted by the percentage difference, descending.
    """
    current_price_col = next((col for col in df.columns if col.startswith("Price")), None)

    df = df.copy()
    df["MOS_Diff_%"] = ((df["MOS_Price"] - df[current_price_col]) / df[current_price_col]) * 100
    df_sorted = df.sort_values(by="MOS_Diff_%", ascending=False)

    return df_sorted

def calculate_value(df, backtesting, final_year, years_back):
    results = []

    for _, row in df.iterrows():
        result = calculate_intrinsic_value(row["EPS_initial"], row["EPS_latest"])
        if result:
            if final_year == datetime.now().year:
                price_date = datetime.today().strftime('%Y-%m-%d')
            else:
                price_date = f"{final_year}-01-07" # Pass a date for compatibility
            price, date = get_stock_price(row["Ticker"], price_date)
            result.update({
                "Company": row["Company"],
                "Ticker": row["Ticker"],
                "EPS_initial": row["EPS_initial"],
                "EPS_latest": row["EPS_latest"],
                f"Price {date}": price
            })
            results.append(result)

    eps_data = pd.DataFrame(results)
    back = "backtest" if backtesting else ""
    intrinsic_values_file = f"nasdaq_intrinsic_values_{back}_from_{final_year}to{final_year-years_back}"
    eps_data["Calculation_date"] = datetime.today().strftime('%d-%m-%Y')
    eps_data.to_csv(f"{intrinsic_values_file}.csv", index=True)

    print(f"Saved intrinsic value results for {len(eps_data)-1} companies to {intrinsic_values_file}")
    undervalued_file=f"undervalued_companies_{back}_from_{final_year}to{final_year-years_back}"
    dframe = pd.read_csv(f'{intrinsic_values_file}.csv')
    undervalued = filter_undervalued_companies(dframe)
    undervalued.to_csv(f"{undervalued_file}.csv", index=True)
    print(f"{len(undervalued)} undervalued companies saved to {undervalued_file}.csv")
    undervalued_sorted = sort_by_mos_difference(undervalued)
    undervalued_sorted = undervalued_sorted.reset_index(drop=True)
    current_price_col = next((col for col in undervalued_sorted.columns if col.startswith("Price")), None)
    undervalued_sorted = undervalued_sorted[[
        "Calculation_date", "Company", "Ticker", current_price_col, "MOS_Price", "MOS_Diff_%", "EPS_initial", "EPS_latest", "EPS_CAGR"
    ]]
    undervalued_sorted.to_csv(f"{undervalued_file}_sorted.csv", index=True)
    undervalued_sorted.to_html(f"{undervalued_file}_sorted.html", index=True)

if __name__ == "__main__":
    calculate_value(pd.read_csv("nasdaq_eps_data.csv"), backtesting=False, final_year= datetime.now().year, years_back=10)
