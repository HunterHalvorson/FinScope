import requests
import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from helper_functions import load_and_return_ticker_data
from services.edgar import fetch_filing_document
from services.text_extraction import extract_sections_from_filing
from services.embeddings import embed_text, chunk_text
import chromadb


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
            "sections": sections
        }

    except Exception as e:

        print(f"Error fetching filing: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post('/filings/{ticker}/{accession}/injest')
def injestion_pipeline(ticker: str, accession: str, primary_document: str):
    ticker_data = load_and_return_ticker_data(TICKERS, ticker)

    cik = str(ticker_data['cik_str'])

    # Get the Filing metadata
    padded_cik = cik.zfill(10)

    response = requests.get(f'https://data.sec.gov/submissions/CIK{padded_cik}.json',
                             headers={'User-Agent': os.environ['SEC_EDGAR_USER_AGENT']})

    response.raise_for_status()

    data = response.json()
    recent = data['filings']['recent']

    filing_date = None
    filing_form = None

    for form, date, accession_no in zip(
        recent['form'],
        recent['filingDate'],
        recent['accessionNumber']
    ):

        if accession_no == accession:

            filing_date = date
            filing_form = form
            break

    if filing_date is None:
        raise HTTPException(
            status_code=404,
            detail="Filing not found"
        )

    # Download filing
    try:
        raw_html = fetch_filing_document(cik, accession, primary_document)
        sections = extract_sections_from_filing(raw_html)

    except Exception as e:
        print(f"Error fetching filing: {e}")
        raise HTTPException(status_code=500,detail=str(e))

    mda = sections['mda']
    riskFactors = sections['riskFactors']

    mda_chunks = chunk_text(mda)
    riskFactor_chunks = chunk_text(riskFactors)

    mda_embed = embed_text(mda_chunks)
    riskFactor_embed = embed_text(riskFactor_chunks)

    mda_metadata = []

    for index in range(len(mda_chunks)):

        metadata = {
            "ticker": ticker_data["ticker"],
            "cik": ticker_data["cik_str"],
            "company": ticker_data["title"],
            "sector": ticker_data["sector"],
            "filing_date": filing_date,
            "form": filing_form,
            "accession": accession,
            "primary_document": primary_document,
            "section": "mda",
            "chunk_index": index
        }

        mda_metadata.append(metadata)

    risk_factor_metadata = []

    for index in range(len(riskFactor_chunks)):

        metadata = {
            "ticker": ticker_data["ticker"],
            "cik": ticker_data["cik_str"],
            "company": ticker_data["title"],
            "sector": ticker_data["sector"],
            "filing_date": filing_date,
            "form": filing_form,
            "accession": accession,
            "primary_document": primary_document,
            "section": "riskFactors",
            "chunk_index": index
        }

        risk_factor_metadata.append(metadata)

    # The client is basically your connection/interface to Chroma.
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name = 'filings')
    