from services.results import get_all_scores_as_dataframe
import pandas as pd


def extract_features():
  df = get_all_scores_as_dataframe()

  df['filing_date'] = pd.to_datetime(df['filing_date'])
  df = df.sort_values(['ticker', 'filing_date'])

  df['mda_net_sentiment'] = df['mda_positive'] - df['mda_negative']
  df['risk_net_sentiment'] = df['risk_positive'] - df['risk_negative']
  df['overall_sentiment'] = df['mda_net_sentiment'] + df['risk_net_sentiment']
  df['overall_uncertainty'] = df['mda_uncertainty'] + df['risk_uncertainty']
  df['overall_litigious'] = df['mda_litigious'] + df['risk_litigious']

  df['sentiment_change'] = df.groupby('ticker')['overall_sentiment'].diff()
  
  return df

