from fastapi import HTTPException

def load_and_return_ticker_data(ticker_data, ticker_name):
  ticker_name = ticker_name.upper()
  for ticker_object in ticker_data:
    if ticker_object['ticker'] == ticker_name:
      return ticker_object

  raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker_name}")

