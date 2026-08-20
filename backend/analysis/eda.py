from analysis.features import extract_features
import pandas as pd

df = extract_features()

# 1. Dataset sanity check
print(f"Total number of filings {len(df)}")
print(f"Number of unique tickers {len(df['ticker'].unique())}")
print(f"Number of 10-K {len(df[df['form'] == '10-K'])}")
print(f"Number of 10-Q {len(df[df['form'] == '10-Q'])}")
print(f"Number of filings per ticker {df.groupby('ticker').count()}")

