import os
from dotenv import load_dotenv

# load the variables from .env into the system environment
load_dotenv()

OPENAI_API_KEY = os.getenv('OPEN_API_KEY')
SEC_EDGAR_USER_AGENT = os.getenv('SEC_EDGAR_USER_AGENT')