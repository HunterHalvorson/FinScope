import requests
import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from helper_functions import load_and_return_ticker_data
from services.edgar import fetch_filing_document
from services.text_extraction import extract_sections_from_filing


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*']
)

load_dotenv()

print(f"API Key loaded: {os.environ.get('SEC_API_KEY')}")

with open('./data/tickers.json') as f:
    TICKERS = json.load(f)


@app.get('/filings/{ticker}')
def get_filings(ticker: str):

    ticker_data = load_and_return_ticker_data(TICKERS, ticker)

    cik = str(ticker_data['cik_str'])
    padded_cik = cik.zfill(10)

    response = requests.get(
        f'https://data.sec.gov/submissions/CIK{padded_cik}.json',
        headers={
            'User-Agent': os.environ['SEC_EDGAR_USER_AGENT']
        }
    )

    response.raise_for_status()

    data = response.json()
    recent = data['filings']['recent']

    filings = []

    for form, filing_date, accession_no, primary_doc in zip(
        recent['form'],
        recent['filingDate'],
        recent['accessionNumber'],
        recent['primaryDocument']
    ):

        if form in ("10-K", "10-Q"):
            filings.append({
                'form': form,
                'filingDate': filing_date,
                'accessionNumber': accession_no,
                'primaryDocument': primary_doc
            })

    return filings


@app.get('/filings/{ticker}/{accession}/text')
def get_filing_text(
    ticker: str,
    accession: str,
    primary_document: str
):

    ticker_data = load_and_return_ticker_data(TICKERS, ticker)

    cik = str(ticker_data['cik_str'])

    try:

        raw_html = fetch_filing_document(
            cik,
            accession,
            primary_document
        )

        sections = extract_sections_from_filing(raw_html)

        return {
            "raw_html": sections
        }

    except Exception as e:

        print(f"Error fetching filing: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )