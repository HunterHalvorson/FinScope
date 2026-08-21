import json, requests, os
from dotenv import load_dotenv
from services.edgar import fetch_filing_document
from services.text_extraction import extract_sections_from_filing
from services.sentiment import score_filing_sections
from services.returns import get_forward_returns
from services.results import save_score_result, init_database
from services.embeddings import embed_text, chunk_text
import chromadb

# load the environment variables
load_dotenv()
init_database()

# Initialize Chroma WITHOUT embedding function
chroma_client = chromadb.PersistentClient(path="./data/chroma")
collection = chroma_client.get_or_create_collection(name='filings')

def filing_already_in_chroma(ticker_name, accession):
    """Check if filing already exists in Chroma"""
    try:
        results = collection.get(
            where={
                "$and": [
                    {"ticker": {"$eq": ticker_name}},
                    {"accession": {"$eq": accession}}
                ]
            },
            limit=1
        )
        return len(results["ids"]) > 0
    except Exception as e:
        print(f"Error checking Chroma: {e}")
        return False


def get_ticker_document_data(tickers):
    """Fetch recent 10-K and 10-Q filings for tickers"""
    ticker_results = {}

    for ticker in tickers:
        cik = str(ticker['cik_str'])
        padded_cik = cik.zfill(10)
        
        try:
            response = requests.get(
                f'https://data.sec.gov/submissions/CIK{padded_cik}.json',
                headers={'User-Agent': os.environ['SEC_EDGAR_USER_AGENT']}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching data for {ticker['ticker']}: {e}")
            continue
        
        data = response.json()
        recent = data['filings']['recent']
        
        current_ticker_filings = []
        
        for form, filing_date, accession_no, primary_doc in zip(
            recent['form'],
            recent['filingDate'],
            recent['accessionNumber'],
            recent['primaryDocument']
        ):
            if form in ("10-K", "10-Q"):
                current_ticker_filings.append({
                    'form': form,
                    'filingDate': filing_date,
                    'accessionNumber': accession_no,
                    'primaryDocument': primary_doc,
                    'ticker': ticker['ticker'],
                    'cik_str': ticker['cik_str'],
                    'title': ticker['title'],
                    'sector': ticker['sector']
                })

        ticker_results[ticker['ticker']] = current_ticker_filings 

    return ticker_results


def batch_score():
    """Main batch scoring function"""
    
    with open('./data/tickers.json') as f:
        TICKERS = json.load(f)
        documents_found = get_ticker_document_data(TICKERS)

        for ticker_name, list_of_documents in documents_found.items():
            for document in list_of_documents:
                # Retrieve correct data
                cik = document['cik_str']
                accession = document['accessionNumber']
                primary_document = document['primaryDocument']
                filing_date = document['filingDate']
                
                # Check if already in Chroma
                if filing_already_in_chroma(ticker_name, accession):
                    print(f"⊘ {ticker_name} {accession} already in Chroma, skipping...")
                    continue
                
                # Download filing
                try:
                    raw_html = fetch_filing_document(cik, accession, primary_document)
                    sections = extract_sections_from_filing(raw_html, document["form"])
                except Exception as e:
                    print(f"Error fetching filing {accession}: {e}")
                    continue
                
                mda = sections.get('mda')
                riskFactors = sections.get('riskFactors')

                if mda is None or riskFactors is None:
                    print(f"⊘ Missing sections for {ticker_name} {accession}, skipping...")
                    continue

                try:
                    # Chunk text
                    mda_chunks = chunk_text(mda)
                    riskFactor_chunks = chunk_text(riskFactors)
                    
                    # Embed chunks
                    mda_embed = embed_text(mda_chunks)
                    riskFactor_embed = embed_text(riskFactor_chunks)

                    # Create metadata
                    mda_metadata = [
                        {
                            "ticker": ticker_name,
                            "cik": cik,
                            "company": document["title"],
                            "sector": document["sector"],
                            "filing_date": filing_date,
                            "form": document["form"],
                            "accession": accession,
                            "section": "mda",
                            "chunk_index": i
                        } 
                        for i in range(len(mda_chunks))
                    ]
                    
                    risk_factor_metadata = [
                        {
                            "ticker": ticker_name,
                            "cik": cik,
                            "company": document["title"],
                            "sector": document["sector"],
                            "filing_date": filing_date,
                            "form": document["form"],
                            "accession": accession,
                            "section": "riskFactors",
                            "chunk_index": i
                        } 
                        for i in range(len(riskFactor_chunks))
                    ]

                    # Create IDs
                    mda_ids = [f"{ticker_name}-{accession}-mda-{i}" for i in range(len(mda_chunks))]
                    rf_ids = [f"{ticker_name}-{accession}-riskfactors-{i}" for i in range(len(riskFactor_chunks))]

                    # Add to Chroma
                    collection.add(
                        documents=mda_chunks + riskFactor_chunks,
                        ids=mda_ids + rf_ids,
                        embeddings=mda_embed + riskFactor_embed,
                        metadatas=mda_metadata + risk_factor_metadata
                    )
                    
                    print(f"✓ Embedded {len(mda_chunks) + len(riskFactor_chunks)} chunks for {ticker_name} {accession}")

                except Exception as e:
                    print(f"Error embedding {accession}: {e}")
                    continue
                
                # Score and save results
                try:
                    scores = score_filing_sections(mda, riskFactors)
                    forward_return = get_forward_returns(ticker_name, filing_date)
                    save_score_result(document, filing_date, document['form'], accession, scores, forward_return)
                except Exception as e:
                    print(f"Error saving results for {accession}: {e}")
                    continue


if __name__ == "__main__":
    batch_score()