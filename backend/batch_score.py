import json, requests, os
from dotenv import load_dotenv
from services.edgar import fetch_filing_document
from services.text_extraction import extract_sections_from_filing
from services.sentiment import score_filing_sections
from services.returns import get_forward_returns
from services.results import  save_score_result, init_database

# load the environment variables
load_dotenv()
init_database()

def get_ticker_document_data(tickers):

  ticker_results = {}

  for ticker in tickers:

    cik = str(ticker['cik_str'])
    padded_cik = cik.zfill(10)
    
    response = requests.get(f'https://data.sec.gov/submissions/CIK{padded_cik}.json',
                            headers={'User-Agent': os.environ['SEC_EDGAR_USER_AGENT']})
    
    response.raise_for_status()
    
    data = response.json()
    recent = data['filings']['recent']
    
    current_ticker_filings = []
    
    for form, filing_date, accession_no, primary_doc in zip(recent['form'],
                                                            recent['filingDate'],
                                                            recent['accessionNumber'],
                                                            recent['primaryDocument']):
    
      if form in ("10-K", "10-Q"):
        current_ticker_filings.append({'form': form,
                                        'filingDate': filing_date,
                                        'accessionNumber': accession_no,
                                        'primaryDocument': primary_doc,
                                        'ticker': ticker['ticker'],
                                        'cik_str': ticker['cik_str'],
                                        'title': ticker['title'],
                                        'sector': ticker['sector']})

    ticker_results[ticker['ticker']] = current_ticker_filings 

  return ticker_results



def batch_score():
  
  # read json file and convert to python object
  with open('./data/tickers.json') as f:
    TICKERS = json.load(f)

    documents_found = get_ticker_document_data(TICKERS)

    for ticker_name, list_of_documents in documents_found.items():
      for document in list_of_documents:

        # retreive correct data
        cik = document['cik_str']
        accession = document['accessionNumber']
        primary_document = document['primaryDocument']
        filing_date = document['filingDate']
        
        # Download filing
        try:
            raw_html = fetch_filing_document(cik, accession, primary_document)
            sections = extract_sections_from_filing(raw_html, document["form"])
        
        except Exception as e:
            print(f"Error fetching filing: {e}")
            continue
        
        mda = sections['mda']
        riskFactors = sections['riskFactors']

        if mda is None or riskFactors is None:
          print(ticker_name)
          continue

    
        scores = score_filing_sections(mda, riskFactors)
        forward_return = get_forward_returns(ticker_name, filing_date)
        save_score_result(document, filing_date, document['form'], accession, scores, forward_return) 
  

batch_score()
    




  


    