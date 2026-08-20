import yfinance as yf
from datetime import datetime, timedelta

def get_forward_returns(ticker: str, filing_date: str, days: int = 90):
    """
    Get stock return N days after filing date
    filing_date: "2024-11-01"
    days: number of days to calculate return over
    """
    stock = yf.Ticker(ticker)
    
    # Convert filing_date to datetime and add days
    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d")
    end_dt = filing_dt + timedelta(days=days)
    
    # Download price data
    hist = stock.history(start=filing_date, end=end_dt.strftime("%Y-%m-%d"))
    
    if len(hist) < 2:
        return None  # Not enough data
    
    price_at_filing = hist['Close'].iloc[0]
    price_after_days = hist['Close'].iloc[-1]
    
    forward_return = (price_after_days - price_at_filing) / price_at_filing
    
    return forward_return