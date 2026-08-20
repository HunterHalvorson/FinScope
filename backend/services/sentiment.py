import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import re

nltk.download('punkt_tab')

LM_dictionary = pd.read_csv('./data/Loughran-McDonald.csv')
positive = set(LM_dictionary[LM_dictionary['Positive'] != 0]['Word'].to_list())
negative = set(LM_dictionary[LM_dictionary['Negative'] != 0]['Word'].to_list())
uncertainty = set(LM_dictionary[LM_dictionary['Uncertainty'] != 0]['Word'].to_list())
litigious = set(LM_dictionary[LM_dictionary['Litigious'] != 0]['Word'].to_list())


def score_text(text: str):
  pattern_to_find = r"[^\w\s]"

  no_punctuation_string = re.sub(pattern_to_find, "", text)
  tokenized_word = word_tokenize(no_punctuation_string)
  tokenized_lower = pd.Series(tokenized_word).str.lower().to_list()

  total_no_words = len(tokenized_lower)

  positive_count, negative_count, uncertainty_count, litigious_count = 0, 0, 0, 0

  for i in range(total_no_words):
    if tokenized_lower[i].upper() in positive:
      positive_count += 1
    if tokenized_lower[i].upper() in negative:
      negative_count += 1
    if tokenized_lower[i].upper() in uncertainty:
      uncertainty_count += 1
    if tokenized_lower[i].upper() in litigious:
      litigious_count += 1
    

  return {
    "positive": positive_count / total_no_words,
    "negative": negative_count / total_no_words,
    "uncertainty" : uncertainty_count / total_no_words,
    "litigious": litigious_count / total_no_words 
  }

result = score_text("This is a great opportunity but we face significant risks")
print(result)


def score_filing_sections(mda_text: str, risk_text: str):
  mda = score_text(mda_text)
  risk = score_text(risk_text)
  return {"mda": mda, "risk_factors": risk}









