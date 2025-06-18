import os
import io
import base64
import requests
import pandas as pd
import mplfinance as mpf
from flask import Flask, request, render_template_string, redirect, url_for, session

# ==============================================================================
# FLASK APP INITIALIZATION
# ==============================================================================
app = Flask(__name__)
# A secret key is required to use Flask sessions for storing the API key.
app.secret_key = os.urandom(24)

# ==============================================================================
# HTML TEMPLATES
# ==============================================================================
# Using template strings to keep the application in a single file for simplicity.

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockView - Analysis</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-gray-200">
    <div class="container mx-auto px-4 py-8 md:py-12">
        <div class="max-w-xl mx-auto text-center">
            <h1 class="text-4xl md:text-5xl font-bold text-white mb-2">StockView</h1>
            <p class="text-lg text-gray-400 mb-8">Enter a stock ticker and your API key to get a complete analysis.</p>
            
            {% if error %}
                <div class="bg-red-800 border border-red-600 text-red-100 px-4 py-3 rounded-lg relative mb-6 text-left" role="alert">
                    <strong class="font-bold">Error:</strong>
                    <span class="block sm:inline">{{ error }}</span>
                </div>
            {% endif %}

            <form action="{{ url_for('analyze') }}" method="post" class="space-y-4">
                <div>
                    <label for="symbol" class="sr-only">Stock Ticker</label>
                    <input type="text" name="symbol" id="symbol" placeholder="e.g., AAPL, TSLA, MSFT"
                           class="w-full px-5 py-3 text-lg text-gray-200 bg-gray-800 border-2 border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500 transition duration-300">
                </div>
                <div>
                    <label for="api_key" class="sr-only">Alpha Vantage API Key</label>
                    <input type="text" name="api_key" id="api_key" placeholder="Enter your Alpha Vantage API Key" value="{{ session.get('api_key', '') }}"
                           class="w-full px-5 py-3 text-lg text-gray-200 bg-gray-800 border-2 border-gray-700 rounded-lg focus:outline-none focus:border-indigo-500 transition duration-300">
                </div>
                <button type="submit" 
                        class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-8 py-3 text-lg rounded-lg transition duration-300 shadow-lg">
                    Analyze
                </button>
            </form>
            <p class="text-xs text-gray-500 mt-4">Data provided by Alpha Vantage. Not financial advice.</p>
        </div>
    </div>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis for {{ overview.get('Symbol', 'N/A') }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .metric-card { background-color: #1F2937; }
    </style>
</head>
<body class="bg-gray-900 text-gray-200">
    <div class="container mx-auto px-4 py-8">
        
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
            <div>
                <h1 class="text-3xl md:text-4xl font-bold text-white">{{ overview.get('Name', 'Unknown Company') }}</h1>
                <p class="text-xl text-indigo-400">{{ overview.get('Symbol', 'N/A') }} - {{ overview.get('Exchange', 'N/A') }}</p>
                <p class="text-md text-gray-400 max-w-2xl mt-2">{{ overview.get('Description', 'No description available.') }}</p>
            </div>
            <a href="/" class="mt-4 md:mt-0 inline-block bg-gray-700 hover:bg-gray-600 text-white font-bold px-6 py-3 rounded-lg transition duration-300">New Analysis</a>
        </div>

        <!-- Fundamental Analysis Section -->
        <div class="mb-10">
            <h2 class="text-2xl font-semibold text-white border-b-2 border-gray-700 pb-2 mb-4">Fundamental Analysis</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div class="metric-card p-4 rounded-lg shadow-lg">
                    <p class="text-sm text-gray-400">P/E Ratio</p>
                    <p class="text-2xl font-bold text-white">{{ fundamentals.pe_ratio }}</p>
                </div>
                <div class="metric-card p-4 rounded-lg shadow-lg">
                    <p class="text-sm text-gray-400">EPS</p>
                    <p class="text-2xl font-bold text-white">{{ fundamentals.eps }}</p>
                </div>
                <div class="metric-card p-4 rounded-lg shadow-lg">
                    <p class="text-sm text-gray-400">Debt/Equity</p>
                    <p class="text-2xl font-bold text-white">{{ fundamentals.debt_to_equity }}</p>
                </div>
                <div class="metric-card p-4 rounded-lg shadow-lg">
                    <p class="text-sm text-gray-400">Return on Equity (ROE)</p>
                    <p class="text-2xl font-bold text-white">{{ fundamentals.return_on_equity }}</p>
                </div>
            </div>
        </div>

        <!-- Technical Analysis Section -->
        <div>
            <h2 class="text-2xl font-semibold text-white border-b-2 border-gray-700 pb-2 mb-4">Technical Analysis Chart</h2>
            <div class="bg-gray-800 p-2 rounded-lg shadow-lg">
                <img src="data:image/png;base64,{{ chart_image }}" alt="Stock Chart for {{ overview.get('Symbol', 'N/A') }}" class="w-full h-auto rounded">
            </div>
        </div>
        
        <div class="text-center mt-8 text-gray-500 text-xs">
            <p>StockView | Data provided by Alpha Vantage. Not financial advice.</p>
        </div>

    </div>
</body>
</html>
"""


# ==============================================================================
# DATA FETCHING (Corresponds to Section 1 of the Plan)
# ==============================================================================
def get_stock_data(symbol, api_key):
    """Fetches historical and fundamental data. Returns (DataFrame, dict, error_message)."""
    print(f"Fetching data for {symbol}...")
    
    # 1. Fetch Historical Price Data
    price_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}'
    try:
        r_price = requests.get(price_url)
        r_price.raise_for_status()
        price_data = r_price.json()
        
        if "Note" in price_data:
            return None, None, f"API limit reached or other API note: {price_data['Note']}"
        if "Error Message" in price_data:
            return None, None, f"Invalid symbol or API error: {price_data['Error Message']}"
            
        df = pd.DataFrame.from_dict(price_data['Time Series (Daily)'], orient='index')
        df = df.astype(float)
        df.rename(columns={'1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '6. volume': 'Volume'}, inplace=True)
        df.index = pd.to_datetime(df.index)
        df = df.iloc[::-1]
        
    except requests.exceptions.RequestException as e:
        return None, None, f"Network error fetching price data: {e}"
    except (KeyError, TypeError):
        return None, None, f"Could not parse price data for '{symbol}'. It may be an invalid ticker."

    # 2. Fetch Fundamental Data
    overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
    try:
        r_overview = requests.get(overview_url)
        r_overview.raise_for_status()
        overview_data = r_overview.json()
        if "Note" in overview_data:
            return df, {}, f"API limit reached on fundamentals: {overview_data['Note']}"
        if not overview_data or overview_data.get('Symbol') is None:
             return df, {}, "Could not fetch fundamental data (the symbol might be an ETF or Index, which lacks this data)."

    except requests.exceptions.RequestException as e:
        return df, {}, f"Network error fetching overview data: {e}"

    print("Data fetching complete.")
    return df, overview_data, None


# ==============================================================================
# ANALYTICAL ENGINES (Corresponds to Section 2 of the Plan)
# ==============================================================================
def run_fundamental_analysis(overview_data):
    """Performs fundamental analysis and returns a dictionary of metrics."""
    fundamentals = {}
    try:
        fundamentals['eps'] = f"{float(overview_data.get('EPS', '0')):.2f}"
        fundamentals['pe_ratio'] = f"{float(overview_data.get('PERatio', '0')):.2f}"
        fundamentals['debt_to_equity'] = f"{float(overview_data.get('DebtToEquityRatio', '0')):.2f}"
        fundamentals['return_on_equity'] = f"{float(overview_data.get('ReturnOnEquityTTM', '0')):.2%}"
    except (ValueError, TypeError):
        # Fill with N/A if data is missing or not a number
        for key in ['eps', 'pe_ratio', 'debt_to_equity', 'return_on_equity']:
            if key not in fundamentals: fundamentals[key] = "N/A"
            
    return fundamentals

def run_technical_analysis(df):
    """Calculates technical indicators and returns the DataFrame."""
    if df is None: return None
    print("Calculating technical indicators...")
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['StdDev_20'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['StdDev_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['StdDev_20'] * 2)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    print("Indicators calculated.")
    return df

# ==============================================================================
# THE VIEWER (Corresponds to Section 3 of the Plan)
# ==============================================================================
def create_chart(df, symbol, overview_data):
    """Creates a financial chart and returns it as a base64 encoded string."""
    if df is None: return None
    print("Generating chart...")
    df_chart = df.tail(365) # Chart last year of data

    ap = [
        mpf.make_addplot(df_chart[['SMA_50', 'SMA_200']]),
        mpf.make_addplot(df_chart[['Upper_Band', 'Lower_Band']], color='grey', alpha=0.3),
        mpf.make_addplot(df_chart['RSI'], panel=2, color='orange', ylabel='RSI'),
        mpf.make_addplot(df_chart[['MACD', 'Signal_Line']], panel=3, ylabel='MACD'),
    ]

    company_name = overview_data.get('Name', symbol)
    
    # Create custom style for dark theme
    mc = mpf.make_marketcolors(up='#22c55e', down='#ef4444', inherit=True)
    s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc)

    # Save chart to a memory buffer
    buf = io.BytesIO()
    mpf.plot(
        df_chart, type='candle', style=s,
        title=f'\nTechnical Analysis for {company_name} ({symbol})',
        ylabel='Price ($)', volume=True, ylabel_lower='Volume',
        addplot=ap, panel_ratios=(6, 2, 2, 2), figratio=(12, 8),
        savefig=dict(fname=buf, dpi=100, format='png')
    )
    buf.seek(0)
    chart_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    print("Chart generated.")
    return chart_image

# ==============================================================================
# FLASK ROUTES
# ==============================================================================
@app.route('/')
def home():
    """Renders the home page with the search form."""
    error = request.args.get('error')
    return render_template_string(HOME_TEMPLATE, error=error)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles the form submission and displays the analysis results."""
    symbol = request.form.get('symbol', '').strip().upper()
    api_key = request.form.get('api_key', '').strip()

    # Store API key in session to pre-fill it on the next visit
    session['api_key'] = api_key

    if not symbol:
        return redirect(url_for('home', error="Ticker symbol cannot be empty."))
    if not api_key:
        return redirect(url_for('home', error="API Key cannot be empty."))

    # 1. Fetch data
    price_df, overview, error = get_stock_data(symbol, api_key)
    if error:
        return redirect(url_for('home', error=error))

    # 2. Run analysis
    fundamentals = run_fundamental_analysis(overview)
    analyzed_df = run_technical_analysis(price_df)

    # 3. Create the viewer output
    chart = create_chart(analyzed_df, symbol, overview)

    return render_template_string(RESULTS_TEMPLATE, overview=overview, fundamentals=fundamentals, chart_image=chart)

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    print("="*60)
    print("Starting StockView Web Application...")
    print("Server running at http://127.0.0.1:5000")
    print("Press CTRL+C to quit.")
    print("="*60)
    app.run(debug=True)
