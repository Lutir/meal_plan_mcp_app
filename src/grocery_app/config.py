from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into os.environ

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
GMAIL_PATH  = os.getenv("GMAIL_CREDENTIALS_JSON")
GROCERIES_INVENTORY_SHEET_ID = os.getenv("GROCERIES_INVENTORY_SHEET_ID")
