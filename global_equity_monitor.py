import modal
import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Create Modal app
app = modal.App(
    "global-equity-price-monitor",
    volumes={"/outputs": modal.Volume.from_name("equity-monitor-outputs", create_if_missing=True)}
)

# Define tickers
SP100_TOP10 = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "BRK-B", "UNH", "TSLA", "JNJ"]
FTSE100_TOP10 = ["SHEL.L", "HSBA.L", "AZN.L", "GSK.L", "ULVR.L", "BP.L", "DGE.L", "BATS.L", "RIO.L", "GLEN.L"]
SP5002_TOP10 = ["AVGO", "COST", "WMT", "PG", "XOM", "LLY", "JPM", "V", "HD", "MA"]

ALL_STOCKS = SP100_TOP10 + FTSE100_TOP10 + SP5002_TOP10

@app.function(schedule=modal.Period(hours=24))
def fetch_and_save_prices():
    # Download last 5 years of closing prices
    data = yf.download(ALL_STOCKS, period="5y", interval="1d", group_by="ticker", auto_adjust=True, threads=True)

    report_rows = []
    
    for ticker in ALL_STOCKS:
        if ticker not in data.columns.levels[0]:
            continue
        
        try:
            closing_prices = data[ticker]["Close"]
            returns = closing_prices.pct_change().dropna()

            overall_return = (closing_prices.iloc[-1] / closing_prices.iloc[0] - 1) * 100
            avg_daily_return = returns.mean() * 100
            moving_average_200 = closing_prices[-200:].mean()

            report_rows.append({
                "Ticker": ticker,
                "5Y Overall Return (%)": round(overall_return, 2),
                "Avg Daily Return (%)": round(avg_daily_return, 4),
                "200-Day Moving Average ($)": round(moving_average_200, 2)
            })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # Save report to CSV
    df = pd.DataFrame(report_rows)
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Decide path based on environment
    if modal.is_local():
        output_folder = "outputs"
        os.makedirs(output_folder, exist_ok=True)
        file_path = f"{output_folder}/equity_monitor_report_{today_str}.csv"
    else:
        file_path = f"/outputs/equity_monitor_report_{today_str}.csv"

    df.to_csv(file_path, index=False)
    print(f"✅ Report saved to {file_path}")

# Local test
if __name__ == "__main__":
    fetch_and_save_prices.local()

