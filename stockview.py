import yfinance as yf
import pandas as pd
import plotly.express as px

# Expanded tickers and sectors
TICKERS = {
    # Technology
    'AAPL': 'Technology',
    'MSFT': 'Technology',
    'GOOGL': 'Communication Services',
    'META': 'Communication Services',
    'NVDA': 'Technology',
    'ADBE': 'Technology',
    'ORCL': 'Technology',
    'CSCO': 'Technology',
    'IBM': 'Technology',
    'CRM': 'Technology',

    # Consumer Discretionary
    'AMZN': 'Consumer Discretionary',
    'TSLA': 'Consumer Discretionary',
    'HD': 'Consumer Discretionary',
    'MCD': 'Consumer Discretionary',
    'NKE': 'Consumer Discretionary',
    'SBUX': 'Consumer Discretionary',

    # Financials
    'JPM': 'Financials',
    'BAC': 'Financials',
    'WFC': 'Financials',
    'C': 'Financials',
    'GS': 'Financials',
    'MS': 'Financials',
    'AXP': 'Financials',

    # Healthcare
    'JNJ': 'Healthcare',
    'PFE': 'Healthcare',
    'MRK': 'Healthcare',
    'ABBV': 'Healthcare',
    'TMO': 'Healthcare',
    'LLY': 'Healthcare',
    'UNH': 'Healthcare',

    # Industrials
    'UNP': 'Industrials',
    'HON': 'Industrials',
    'UPS': 'Industrials',
    'CAT': 'Industrials',
    'BA': 'Industrials',

    # Energy
    'XOM': 'Energy',
    'CVX': 'Energy',
    'COP': 'Energy',
    'SLB': 'Energy',

    # Utilities
    'NEE': 'Utilities',
    'DUK': 'Utilities',
    'SO': 'Utilities',

    # Consumer Staples
    'PG': 'Consumer Staples',
    'KO': 'Consumer Staples',
    'PEP': 'Consumer Staples',
    'WMT': 'Consumer Staples',
    'COST': 'Consumer Staples',

    # Real Estate
    'PLD': 'Real Estate',
    'AMT': 'Real Estate',
    'CCI': 'Real Estate',

    # Materials
    'LIN': 'Materials',
    'APD': 'Materials',
    'SHW': 'Materials',

    # Telecommunication Services
    'VZ': 'Communication Services',
    'T': 'Communication Services',
    'TMUS': 'Communication Services',
}

def get_returns(ticker, period):
    """Fetch and calculate percent return for a ticker over a given period."""
    data = yf.download(ticker, period=period, interval='1d', progress=False)
    if data.empty:
        return None
    start_price = data['Open'][0]
    end_price = data['Close'][-1]
    pct_return = (end_price - start_price) / start_price * 100
    return pct_return

def get_all_returns(tickers, period):
    """Get returns for all tickers."""
    results = []
    for ticker, sector in tickers.items():
        ret = get_returns(ticker, period)
        if ret is not None:
            results.append({'Ticker': ticker, 'Sector': sector, 'Return': ret})
    return pd.DataFrame(results)

def show_winners_losers(df, top_n=3):
    """Print top winners and losers."""
    winners = df.sort_values('Return', ascending=False).head(top_n)
    losers = df.sort_values('Return').head(top_n)
    print("Top Winners:")
    print(winners.to_string(index=False))
    print("\nTop Losers:")
    print(losers.to_string(index=False))

def filter_by_sector(df, sector):
    """Filter DataFrame by sector."""
    return df[df['Sector'] == sector]

def plot_returns(df, title='Stock Returns'):
    """Plot bar chart of returns by ticker and sector."""
    fig = px.bar(df, x='Ticker', y='Return', color='Sector', title=title)
    fig.show()

def select_period():
    """Ask user for period selection."""
    options = {
        '1': ('1d', "Day"),
        '2': ('7d', "Week"),
        '3': ('1mo', "Month"),
        '4': ('1y', "Year")
    }
    print("Select Period:")
    for k, v in options.items():
        print(f"{k}: {v[1]}")
    choice = input("Enter option [1-4]: ").strip()
    return options.get(choice, ('7d', "Week"))  # Default to week

def main():
    period, period_label = select_period()
    print(f"\nFetching data for the last {period_label}...\n")
    df = get_all_returns(TICKERS, period)
    if df.empty:
        print("No data found. Try with different tickers or period.")
        return
    print("Available sectors:", ', '.join(sorted(df['Sector'].unique())))
    sector = input("Filter by sector (leave blank for all): ").strip()
    if sector:
        df = filter_by_sector(df, sector)
        if df.empty:
            print(f"No data for sector: {sector}")
            return
    show_winners_losers(df)
    plot_returns(df, f"{period_label} Returns{f' - {sector}' if sector else ''}")

if __name__ == "__main__":
    main()
