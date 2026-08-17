import requests, os, json
from dotenv import load_dotenv

load_dotenv()

# nvda_cik = "CIK0001045810"

# headers = {
#     "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"]
# }

# response = requests.get(f'https://data.sec.gov/submissions/{nvda_cik}.json',
#                         headers=headers)


# data = response.json()
# recent = data['filings']['recent']

# filings = []

# for form, filing_date, accession_no, primary_doc in zip(recent['form'], recent['filingDate'], recent['accessionNumber'], recent['primaryDocument']):
#   if form in ("10-K", "10-Q"):
#     filings.append({'form': form, 'filingDate': filing_date, 'accessionNumber': accession_no, 'primaryDocument': primary_doc})

# print(len(filings))
# for f in filings[:5]:
#     print(f)



  