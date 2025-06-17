import requests

def get_stock_quote(symbol: str, api_key: str) -> dict:
    """
    Fetches the latest stock quote for a given symbol from Alpha Vantage.
    """
    # The API URL for the GLOBAL_QUOTE function
    url = (
        f'https://www.alphavantage.co/query'
        f'?function=GLOBAL_QUOTE'
        f'&symbol={symbol}'
        f'&apikey={api_key}'
    )
    
    try:
        response = requests.get(url)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 
        data = response.json()
        
        # The key 'Global Quote' contains the data we want
        if 'Global Quote' in data and data['Global Quote']:
            return data['Global Quote']
        else:
            # Handle cases where the API returns an empty or error message
            print(f"Error fetching data for {symbol}: {data.get('Note', 'Unexpected API response.')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# --- Main part of the script to test the function ---
if __name__ == "__main__":
    # IMPORTANT: Replace with your actual API key and desired stock symbol
    YOUR_API_KEY = "B5SV6A0G84E2R9K5"  # Replace with your key
    STOCK_SYMBOL = "AAPL"          # Example: Apple Inc.

    print(f"Fetching latest quote for {STOCK_SYMBOL}...")
    quote = get_stock_quote(STOCK_SYMBOL, YOUR_API_KEY)
    
    if quote:
        print("\n--- Stock Quote ---")
        # The API returns keys like "01. symbol", "05. price", etc.
        print(f"Symbol: {quote.get('01. symbol')}")
        print(f"Price: ${float(quote.get('05. price')):.2f}")
        print(f"Change: {quote.get('09. change')}")
        print(f"Change Percent: {quote.get('10. change percent')}")
        print(f"Volume: {quote.get('06. volume')}")
        print("-------------------\n")
