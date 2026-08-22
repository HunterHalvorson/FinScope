import requests
import os
import json
import chromadb

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from helper_functions import load_and_return_ticker_data
from services.edgar import fetch_filing_document
from services.text_extraction import extract_sections_from_filing
from services.embeddings import embed_text, chunk_text
from services.sentiment import score_filing_sections
from services.results import init_database, save_score_result
from services.returns import get_forward_returns
from analysis.event_study import get_event_study_data


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Initialize FastAPI
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# Initialize database
# --------------------------------------------------

init_database()


# --------------------------------------------------
# Initialize Chroma
# --------------------------------------------------

# Chroma stores vectors that were already created
# by embed_text().
#
# We do NOT give Chroma an embedding function here.

chroma_client = chromadb.PersistentClient(
    path="./data/chroma"
)

collection = chroma_client.get_or_create_collection(
    name="filings"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# Load ticker data
# --------------------------------------------------

with open("./data/tickers.json") as f:
    TICKERS = json.load(f)


@app.get("/results")
def get_results(ticker: str):

    from services.results import get_all_scores_as_dataframe

    df = get_all_scores_as_dataframe()

    df_filtered = df[df["ticker"] == ticker]

    return df_filtered.to_dict(orient="records")


@app.get("/analysis/event-study/{ticker}")
def event_study(ticker):
    return get_event_study_data(ticker)


# --------------------------------------------------
# GET FILINGS FOR A TICKER
# --------------------------------------------------

@app.get("/filings/{ticker}")
def get_filings(ticker: str):

    ticker_data = load_and_return_ticker_data(
        TICKERS,
        ticker
    )

    cik = str(ticker_data["cik_str"])
    padded_cik = cik.zfill(10)

    response = requests.get(
        f"https://data.sec.gov/submissions/CIK{padded_cik}.json",
        headers={
            "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"]
        }
    )

    response.raise_for_status()

    data = response.json()

    recent = data["filings"]["recent"]

    filings = []

    for form, filing_date, accession_no, primary_doc in zip(
        recent["form"],
        recent["filingDate"],
        recent["accessionNumber"],
        recent["primaryDocument"]
    ):

        if form in ("10-K", "10-Q"):

            filings.append({
                "form": form,
                "filingDate": filing_date,
                "accessionNumber": accession_no,
                "primaryDocument": primary_doc
            })

    return filings


# --------------------------------------------------
# INGEST FILING
# --------------------------------------------------

@app.post("/filings/{ticker}/{accession}/ingest")
def ingestion_pipeline(
    ticker: str,
    accession: str,
    primary_document: str
):

    # --------------------------------------------------
    # Get ticker information
    # --------------------------------------------------

    ticker_data = load_and_return_ticker_data(
        TICKERS,
        ticker
    )

    cik = str(ticker_data["cik_str"])
    padded_cik = cik.zfill(10)


    # --------------------------------------------------
    # Get filing metadata from SEC
    # --------------------------------------------------

    response = requests.get(
        f"https://data.sec.gov/submissions/CIK{padded_cik}.json",
        headers={
            "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"]
        }
    )

    response.raise_for_status()

    data = response.json()

    recent = data["filings"]["recent"]

    filing_date = None
    filing_form = None


    for form, date, accession_no in zip(
        recent["form"],
        recent["filingDate"],
        recent["accessionNumber"]
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


    # --------------------------------------------------
    # Download filing
    # --------------------------------------------------

    try:

        raw_html = fetch_filing_document(
            cik,
            accession,
            primary_document
        )

        sections = extract_sections_from_filing(
            raw_html
        )

    except Exception as e:

        print(f"Error fetching filing: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    # --------------------------------------------------
    # Get sections
    # --------------------------------------------------

    mda = sections.get("mda")
    riskFactors = sections.get("riskFactors")


    if mda is None or riskFactors is None:

        raise HTTPException(
            status_code=400,
            detail="Could not extract MDA or Risk Factors sections"
        )


    # --------------------------------------------------
    # Chunk text
    # --------------------------------------------------

    mda_chunks = chunk_text(mda)

    riskFactor_chunks = chunk_text(riskFactors)


    # --------------------------------------------------
    # Create embeddings
    # --------------------------------------------------

    mda_embed = embed_text(mda_chunks)

    riskFactor_embed = embed_text(riskFactor_chunks)


    # --------------------------------------------------
    # Create MDA metadata
    # --------------------------------------------------

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


    # --------------------------------------------------
    # Create Risk Factors metadata
    # --------------------------------------------------

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


    # --------------------------------------------------
    # Combine chunks
    # --------------------------------------------------

    combined_chunks = (
        mda_chunks +
        riskFactor_chunks
    )


    # --------------------------------------------------
    # Combine embeddings
    # --------------------------------------------------

    combined_embeddings = (
        mda_embed +
        riskFactor_embed
    )


    # --------------------------------------------------
    # Create IDs
    # --------------------------------------------------

    ids = []

    for i in range(len(mda_chunks)):

        ids.append(
            f"{ticker_data['ticker']}-{accession}-mda-{i}"
        )

    for i in range(len(riskFactor_chunks)):

        ids.append(
            f"{ticker_data['ticker']}-{accession}-riskfactors-{i}"
        )


    # --------------------------------------------------
    # Combine metadata
    # --------------------------------------------------

    combined_metadata = (
        mda_metadata +
        risk_factor_metadata
    )


    # --------------------------------------------------
    # Store everything in Chroma
    # --------------------------------------------------

    try:

        collection.add(
            documents=combined_chunks,
            ids=ids,
            embeddings=combined_embeddings,
            metadatas=combined_metadata
        )

    except Exception as e:

        print(f"Error adding filing to Chroma: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {

        "status": "success",

        "ticker": ticker_data["ticker"],

        "accession": accession,

        "filing_date": filing_date,

        "form": filing_form,

        "mda_chunks_added": len(mda_chunks),

        "risk_factor_chunks_added": len(riskFactor_chunks),

        "total_chunks_added": len(combined_chunks),

        "message": (
            f"Successfully ingested "
            f"{len(combined_chunks)} chunks into Chroma"
        )
    }


# --------------------------------------------------
# SCORE FILING
# --------------------------------------------------

@app.post("/filings/{ticker}/{accession}/score")
def score(
    ticker: str,
    accession: str,
    primary_document: str
):

    # --------------------------------------------------
    # Get ticker information
    # --------------------------------------------------

    ticker_data = load_and_return_ticker_data(
        TICKERS,
        ticker
    )

    cik = str(ticker_data["cik_str"])

    padded_cik = cik.zfill(10)


    # --------------------------------------------------
    # Get filing metadata
    # --------------------------------------------------

    response = requests.get(
        f"https://data.sec.gov/submissions/CIK{padded_cik}.json",
        headers={
            "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"]
        }
    )

    response.raise_for_status()

    data = response.json()

    recent = data["filings"]["recent"]

    filing_date = None
    filing_form = None


    for form, date, accession_no in zip(
        recent["form"],
        recent["filingDate"],
        recent["accessionNumber"]
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


    # --------------------------------------------------
    # Download filing
    # --------------------------------------------------

    try:

        raw_html = fetch_filing_document(
            cik,
            accession,
            primary_document
        )

        sections = extract_sections_from_filing(
            raw_html
        )

    except Exception as e:

        print(f"Error fetching filing: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    # --------------------------------------------------
    # Get sections
    # --------------------------------------------------

    mda = sections.get("mda")
    riskFactors = sections.get("riskFactors")


    if mda is None or riskFactors is None:

        raise HTTPException(
            status_code=400,
            detail="Could not extract MDA or Risk Factors sections"
        )


    # --------------------------------------------------
    # Score filing
    # --------------------------------------------------

    scores = score_filing_sections(
        mda,
        riskFactors
    )


    # --------------------------------------------------
    # Calculate forward return
    # --------------------------------------------------

    forward_return = get_forward_returns(
        ticker,
        filing_date
    )


    # --------------------------------------------------
    # Save results
    # --------------------------------------------------

    save_score_result(
        ticker_data,
        filing_date,
        filing_form,
        accession,
        scores,
        forward_return
    )


    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {

        "status": "success",

        "ticker": ticker_data["ticker"],

        "accession": accession,

        "filing_date": filing_date,

        "form": filing_form,

        "scores": scores,

        "forward_return": forward_return
    }


# --------------------------------------------------
# CHAT / RAG
# --------------------------------------------------

@app.post("/chat")
def chat(ticker: str, query: str):

    # --------------------------------------------------
    # Create embedding for user's question
    # --------------------------------------------------

    query_embedding = embed_text([query])[0]


    # --------------------------------------------------
    # Search Chroma
    # --------------------------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],

        where={
            "ticker": ticker
        },

        n_results=5
    )


    # --------------------------------------------------
    # Get retrieved documents
    # --------------------------------------------------

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]


    # --------------------------------------------------
    # Check if documents were found
    # --------------------------------------------------

    if not documents:

        return {
            "answer": (
                f"No documents found for {ticker}. "
                f"Try a different query."
            ),
            "sources": []
        }


    # --------------------------------------------------
    # Format context
    # --------------------------------------------------

    context = "\n\n".join(documents)


    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    template = """You are an expert financial analyst specializing in SEC filing analysis.

    Your role: Answer questions about {ticker}'s SEC filings based ONLY on the provided context.

    IMPORTANT INSTRUCTIONS:
    - Only use information from the provided context
    - If the answer is not in the context, clearly state: "This information is not available in the provided filings."
    - Be concise but thorough
    - Always start your response with the company ticker in bold: **{ticker}**
    - Always include a clear header that directly addresses the question
    - Use numbered lists when presenting multiple related points (risks, strategies, metrics, etc.)
    - Use prose format when explaining concepts, narratives, or single complex topics
    - Cite specific details from the filings when possible

    Context from {ticker} SEC Filings:
    {context}

    Question: {question}

    ---

    RESPONSE FORMAT GUIDELINES:

    For "What are the..." questions → Use numbered list format:
    "**{ticker}**

    Here are the main [topic]:
    1. [Point 1] - [Explanation]
    2. [Point 2] - [Explanation]"

    For "How/Why/Explain..." questions → Use prose format with clear sections:
    "**{ticker}**

    [Direct answer with main point]

    [Supporting detail 1]
    [Supporting detail 2]"

    For "What is the..." questions → Use descriptive format:
    "**{ticker}**

    [Definition/Description]

    Key aspects:
    1. [Aspect 1]
    2. [Aspect 2]"

    For comparison questions → Use side-by-side or alternating format:
    "**{ticker}**

    [Topic A]: [Details]
    [Topic B]: [Details]"

    ---

    Provide your answer now:
    """

    prompt = ChatPromptTemplate.from_template(template)


    # --------------------------------------------------
    # Initialize OpenAI
    # --------------------------------------------------

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ.get("OPENAI_API_KEY")
    )


    # --------------------------------------------------
    # Build chain
    # --------------------------------------------------

    chain = prompt | llm | StrOutputParser()


    # --------------------------------------------------
    # Generate answer
    # --------------------------------------------------

    answer = chain.invoke({

        "ticker": ticker,

        "context": context,

        "question": query
    })


    # --------------------------------------------------
    # Create sources
    # --------------------------------------------------

    sources = []

    for i in range(len(documents)):

        sources.append({

            "chunk": documents[i][:200] + "...",

            "filing_date": metadatas[i].get("filing_date"),

            "section": metadatas[i].get("section"),

            "form": metadatas[i].get("form")
        })


    # --------------------------------------------------
    # Return answer
    # --------------------------------------------------

    return {

        "answer": answer,

        "sources": sources
    }


# --------------------------------------------------
# Run directly with Python
# --------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )