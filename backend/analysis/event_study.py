import pandas as pd
from services.results import get_all_scores_as_dataframe
import matplotlib.pyplot as plt

def get_event_study_data():

  df = get_all_scores_as_dataframe()
  df['mda_sentiment'] = df['mda_positive'] - df['mda_negative']
  df['risk_sentiment'] = df['risk_positive'] - df['risk_negative']

  analysis_df = df[['mda_sentiment', 'risk_sentiment', 'forward_return']].dropna()

  correlation_mda = analysis_df["mda_sentiment"].corr(analysis_df["forward_return"])
  correlation_risk = analysis_df["risk_sentiment"].corr(analysis_df["forward_return"])

  print("Correlation_mda:", correlation_mda)
  print("Correlation_risk:", correlation_risk)

  plt.scatter(
      analysis_df["mda_sentiment"],
      analysis_df["forward_return"]
  )

  plt.xlabel("MD&A Sentiment")
  plt.ylabel("Forward Return")
  plt.title("MD&A Sentiment vs Forward Stock Return")

  plt.show()

  return {
        "mdaCorr": correlation_mda,
        "riskCorr": correlation_risk,
        "data": analysis_df.to_dict(orient="records")
    }