import requests, os


def fetch_filing_document(cik: str, accessionNumber: str, primaryDocument: str) -> str:
  accessionNumberNoDashes = ''.join(accessionNumber.split('-'))
  url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accessionNumberNoDashes}/{primaryDocument}'
  resp = requests.get(url, headers = {'User-Agent': os.environ['SEC_EDGAR_USER_AGENT']})
  resp.raise_for_status()
  
  return resp.text