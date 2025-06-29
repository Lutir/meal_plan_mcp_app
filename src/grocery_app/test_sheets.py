from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from grocery_app.config import SHEETS_PATH, GROCERIES_INVENTORY_SHEET_ID

creds = Credentials.from_service_account_file(SHEETS_PATH, scopes=["https://www.googleapis.com/auth/spreadsheets"])
service = build("sheets", "v4", credentials=creds)
result = service.spreadsheets().values().get(spreadsheetId=GROCERIES_INVENTORY_SHEET_ID, range="A1").execute()
print("A1 value:", result.get("values"))
