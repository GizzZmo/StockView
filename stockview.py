import yfinance as yf
import pandas as pd
import plotly.express as px

# Example tickers and their sectors (expand as needed)
TICKERS = {
    'AAPL': 'Technology',
    'MSFT': 'Technology',
    'GOOGL': 'Communication Services',
    'JPM': 'Financials',
    'TSLA': 'Consumer Discretionary',
    'AMZN': 'Consumer Discretionary',
    'META': 'Communication Services',
    'NVDA': 'Technology'
}

# Helper function to fetch returns
def get_returns(ticker, period):
    data = yf.download(ticker, period=period, interval='1d', progress=False)
    if data.empty:
        return None
    start_price = data['Open'][0]
    end_price = data['Close'][-1]
    pct_return = (end_price - start_price) / start_price * 100
    return pct_return

def get_all_returns(tickers, period):
    results = []
    for ticker, sector in tickers.items():
        ret = get_returns(ticker, period)
        if ret is not None:
            results.append({'Ticker': ticker, 'Sector': sector, 'Return': ret})
    return pd.DataFrame(results)

def show_winners_losers(df, top_n=3):
    winners = df.sort_values('Return', ascending=False).head(top_n)
    losers = df.sort_values('Return').head(top_n)
    print("Top Winners:")
    print(winners.to_string(index=False))
    print("\nTop Losers:")
    print(losers.to_string(index=False))

def filter_by_sector(df, sector):
    return df[df['Sector'] == sector]

def plot_returns(df, title='Stock Returns'):
    fig = px.bar(df, x='Ticker', y='Return', color='Sector', title=title)
    fig.show()

def select_period():
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
    df = get_all_returns(TICKERS, period)
    if df.empty:
        print("No data found. Try with different tickers or period.")
        return
    print("\nAvailable sectors:", ', '.join(sorted(df['Sector'].unique())))
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
