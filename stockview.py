import yfinance as yf
import pandas as pd
import plotly.express as px

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

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
    """
    Fetch and calculate percent return for a ticker over a given period.
    Handles empty data and missing columns robustly.
    """
    try:
        data = yf.download(
            ticker,
            period=period,
            interval='1d',
            progress=False,
            auto_adjust=False  # Explicit to avoid FutureWarning
        )
        if data.empty or 'Open' not in data.columns or 'Close' not in data.columns:
            print(f"  [!] No valid data for {ticker} in period '{period}'.")
            return None
        start_price = data['Open'].iloc[0]
        end_price = data['Close'].iloc[-1]
        pct_return = (end_price - start_price) / start_price * 100
        return pct_return
    except Exception as e:
        print(f"  [!] Error fetching data for {ticker}: {e}")
        return None

def get_all_returns(tickers, period):
    """Get returns for all tickers."""
    results = []
    print("\nFetching data for tickers. This may take a moment...\n")
    for i, (ticker, sector) in enumerate(tickers.items(), 1):
        print(f"  [{i}/{len(tickers)}] {ticker}...", end="\r")
        ret = get_returns(ticker, period)
        if ret is not None:
            results.append({'Ticker': ticker, 'Sector': sector, 'Return': ret})
    print(" " * 40, end="\r")  # Clear progress line
    return pd.DataFrame(results)

def show_winners_losers(df, top_n=3):
    """Print top winners and losers."""
    print("\n" + "="*40)
    print("Top Winners and Losers")
    print("="*40)
    if df.empty:
        print("No data to display winners and losers.")
        return
    # Ensure 'Return' is numeric and drop NaNs
    df = df.copy()
    df['Return'] = pd.to_numeric(df['Return'], errors='coerce')
    df = df.dropna(subset=['Return'])
    if df.empty:
        print("No valid return data to display winners and losers.")
        return
    winners = df.sort_values('Return', ascending=False).head(top_n)
    losers = df.sort_values('Return').head(top_n)
    print("\nTop Winners:")
    if TABULATE_AVAILABLE:
        print(tabulate(winners, headers="keys", tablefmt="fancy_grid", showindex=False, floatfmt=".2f"))
    else:
        print(winners.to_string(index=False, float_format="%.2f"))
    print("\nTop Losers:")
    if TABULATE_AVAILABLE:
        print(tabulate(losers, headers="keys", tablefmt="fancy_grid", showindex=False, floatfmt=".2f"))
    else:
        print(losers.to_string(index=False, float_format="%.2f"))

def filter_by_sector(df, sector):
    """Filter DataFrame by sector."""
    return df[df['Sector'].str.lower() == sector.lower()]

def plot_returns(df, title='Stock Returns'):
    """Plot improved bar chart of returns by ticker and sector."""
    if df.empty:
        print("No data to plot.")
        return
    df = df.copy()
    df['Return'] = pd.to_numeric(df['Return'], errors='coerce')
    df = df.dropna(subset=['Return'])
    df = df.sort_values('Return', ascending=False)
    fig = px.bar(
        df,
        x='Ticker',
        y='Return',
        color='Sector',
        title=title,
        text='Return',
        color_discrete_sequence=px.colors.qualitative.Safe  # colorblind-friendly
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(
        xaxis_title='Ticker',
        yaxis_title='Return (%)',
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        yaxis=dict(tickformat=".2f"),
        bargap=0.3,
        legend_title_text='Sector',
        plot_bgcolor='white'
    )
    fig.show()

def select_period():
    """Ask user for period selection."""
    options = {
        '1': ('1d', "Day"),
        '2': ('7d', "Week"),
        '3': ('1mo', "Month"),
        '4': ('1y', "Year")
    }
    print("\nSelect Period:")
    for k, v in options.items():
        print(f"  {k}: {v[1]}")
    while True:
        choice = input("Enter option [1-4]: ").strip()
        if choice in options:
            return options[choice]
        elif choice == "":
            return options['2']  # Default to week
        else:
            print("Invalid input. Please enter a number between 1 and 4.")

def main():
    print("="*50)
    print("        StockView - Stock Return Visualizer")
    print("="*50)
    while True:
        period, period_label = select_period()
        print(f"\nFetching data for the last {period_label}...\n")
        df = get_all_returns(TICKERS, period)
        if df.empty:
            print("No data found. Try with different tickers or period.")
            continue
        print("\nAvailable sectors:")
        sectors = sorted(df['Sector'].unique())
        for i, s in enumerate(sectors, 1):
            print(f"  {i}. {s}")
        print("  0. All sectors")
        sector = input("Filter by sector (enter number or leave blank for all): ").strip()
        if sector and sector.isdigit() and 0 < int(sector) <= len(sectors):
            df = filter_by_sector(df, sectors[int(sector)-1])
            if df.empty:
                print(f"No data for sector: {sectors[int(sector)-1]}")
                continue
            sector_label = f" - {sectors[int(sector)-1]}"
        else:
            sector_label = ""
        show_winners_losers(df)
        plot_returns(df, f"{period_label} Returns{sector_label}")
        again = input("\nWould you like to view another period or sector? (y/n): ").strip().lower()
        if again != "y":
            print("\nThank you for using StockView!")
            break

if __name__ == "__main__":
    main()
