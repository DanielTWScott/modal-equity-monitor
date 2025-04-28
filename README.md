# Modal Equity Monitor

Small serverless app built whilst experimenting on [Modal](https://modal.com/) to monitor large cap US and UK equity prices.

- Pulls last five years of closing price data for top stocks in S&P100, FTSE100, and S&P500
- Calculates returns over last 5 years, average daily returns, and 200-day moving averages
- Automatically saves daily reports to cloud storage (Modal Volumes)
- Scheduled to run every 24 hours without manual intervention.
