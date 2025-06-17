## Review & Common Mistakes Checklist

### 1. Error Handling & Robustness
- **Network/Data Issues:** If yfinance fails to fetch data (e.g., due to network or ticker issues), the script handles it gracefully by skipping the ticker and moving on.
- **User Input:** The script defaults to "week" if the user enters an invalid period selection.  
  → You might want to add further input validation.
- **Sector Filter:** If the user enters a sector that doesn’t exist, the script notifies them and exits.
- **Empty DataFrame:** If no data is available, the script prints a message and exits.

### 2. Code Quality
- **PEP8 Compliance:** The code is readable and well-structured. For full compliance, ensure function and variable names use snake_case and lines are <80 characters where possible.
- **Comments & Docstrings:** The code includes helpful comments and docstrings—good for maintainability.

### 3. Enhancements (Optional)
- **Batch Data Fetching:** yfinance can fetch multiple tickers at once, improving speed. For a small number of tickers, this isn’t critical, but if you expand the universe, consider batching.
- **Requirements File:** Include a `requirements.txt`:
  ```
  yfinance
  pandas
  plotly
  ```
- **README Sample Output:** Add sample command line output in your README to help users know what to expect.

### 4. Known Limitations
- **yfinance API Quotas:** For large lists or repeated queries, be aware of API rate limits.
- **Market Hours:** Running the script outside of market hours may show incomplete or stale data.

---

## HOWTO: Using StockView

### Prerequisites
- Python 3.7 or newer
- Internet connection

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GizzZmo/StockView.git
   cd StockView
   ```

2. **(Recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   _Or install manually:_
   ```bash
   pip install yfinance pandas plotly
   ```

### Usage

1. **Run the script:**
   ```bash
   python stockview.py
   ```

2. **Follow the prompts:**
   - Select a time period (Day, Week, Month, Year)
   - Optionally, filter by sector (press Enter to skip)
   - View the top winners and losers in the terminal
   - An interactive chart will pop up in your browser or default viewer

3. **Example Output:**
   ```
   Select Period:
   1: Day
   2: Week
   3: Month
   4: Year
   Enter option [1-4]: 2

   Fetching data for the last Week...

   Available sectors: Communication Services, Consumer Discretionary, Consumer Staples, Energy, Financials, Healthcare, Industrials, Materials, Real Estate, Technology, Utilities
   Filter by sector (leave blank for all):
   Top Winners:
     Ticker               Sector    Return
      NVDA           Technology     8.120
      AMZN Consumer Discretionary     7.050
      ...
   Top Losers:
     Ticker           Sector    Return
      XOM             Energy    -2.350
      ...
   ```

### Troubleshooting

- If you see "No data found," check your internet connection or try a different period/ticker.
- For "No data for sector," verify your spelling or pick from the listed available sectors.

---

**Ready for release!**  
If you want to further polish for end-users, consider batch fetching, richer error messages, or even a Streamlit web interface in the future.  
Let me know if you want any of those enhancements or have further questions!
