import pandas as pd
import sqlite3
import os

# Database path
DB_PATH = "./data/results.db"

def init_database():
    """Create the results table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filing_scores (
            ticker TEXT,
            company TEXT,
            sector TEXT,
            filing_date TEXT,
            form TEXT,
            accession TEXT,
            mda_positive REAL,
            mda_negative REAL,
            mda_uncertainty REAL,
            mda_litigious REAL,
            risk_positive REAL,
            risk_negative REAL,
            risk_uncertainty REAL,
            risk_litigious REAL,
            forward_return REAL,
            PRIMARY KEY (ticker, accession)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_score_result(ticker_data, filing_date, form, accession, scores, forward_return):
    """Save a single filing's sentiment scores and forward return to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO filing_scores 
        (ticker, company, sector, filing_date, form, accession, 
         mda_positive, mda_negative, mda_uncertainty, mda_litigious,
         risk_positive, risk_negative, risk_uncertainty, risk_litigious, forward_return)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticker_data["ticker"],
        ticker_data["title"],
        ticker_data["sector"],
        filing_date,
        form,
        accession,
        scores["mda"]["positive"],
        scores["mda"]["negative"],
        scores["mda"]["uncertainty"],
        scores["mda"]["litigious"],
        scores["risk_factors"]["positive"],
        scores["risk_factors"]["negative"],
        scores["risk_factors"]["uncertainty"],
        scores["risk_factors"]["litigious"],
        forward_return
    ))
    
    conn.commit()
    conn.close()

def get_all_scores_as_dataframe():
    """Load all results into a pandas DataFrame"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM filing_scores", conn)
    conn.close()
    return df

def export_to_csv(filename="./data/filing_scores.csv"):
    """Export all results to CSV"""
    df = get_all_scores_as_dataframe()
    df.to_csv(filename, index=False)
    print(f"Exported to {filename}")

