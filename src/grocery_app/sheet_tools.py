# src/grocery_app/sheets_tool.py
from typing import List, Dict
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from grocery_app.config import GOOGLE_SHEETS_CREDENTIALS_JSON, GROCERIES_INVENTORY_SHEET_ID

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_creds = Credentials.from_service_account_file(
    GOOGLE_SHEETS_CREDENTIALS_JSON, scopes=SCOPES
)
_svc = build("sheets", "v4", credentials=_creds).spreadsheets()


def get_inventory(
    spreadsheet_id: str = GROCERIES_INVENTORY_SHEET_ID,
    sheet_name: str = "Sheet1"
) -> List[Dict]:
    """Read Sheet1!A2:C and return list of {"item", "quantity", "unit"}."""
    resp = _svc.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A2:C"
    ).execute()
    values = resp.get("values", [])
    inventory = []
    for row in values:
        if not row or not row[0].strip():
            continue
        item = row[0].strip()
        qty = float(row[1]) if len(row) > 1 and row[1] else 0.0
        unit = row[2].strip() if len(row) > 2 else ""
        inventory.append({"item": item, "quantity": qty, "unit": unit})
    return inventory


def get_order_sheet(
    spreadsheet_id: str = GROCERIES_INVENTORY_SHEET_ID,
    sheet_name: str = "Sheet2"
) -> List[Dict]:
    """Read order sheet and return list of {"item", "quantity", "unit"}."""
    resp = _svc.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A2:C"
    ).execute()
    values = resp.get("values", [])
    orders = []
    for row in values:
        if not row or not row[0].strip():
            continue
        item = row[0].strip()
        qty = float(row[1]) if len(row) > 1 and row[1] else 0.0
        unit = row[2].strip() if len(row) > 2 else ""
        orders.append({"item": item, "quantity": qty, "unit": unit})
    return orders


def add_to_order_sheet(
    item: str,
    quantity: float,
    unit: str = "",
    spreadsheet_id: str = GROCERIES_INVENTORY_SHEET_ID,
    sheet_name: str = "Sheet2",
) -> str:
    """Add an item to the order sheet."""
    try:
        # Check if item already exists in order sheet
        existing_orders = get_order_sheet(spreadsheet_id, sheet_name)
        for order in existing_orders:
            if order["item"].lower() == item.lower():
                # Update existing order
                _svc.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A{existing_orders.index(order) + 2}:C{existing_orders.index(order) + 2}",
                    valueInputOption="RAW",
                    body={"values": [[item, quantity, unit]]}
                ).execute()
                return f"✅ Updated order for {item}: {quantity} {unit or 'units'}"
        
        # Add new order
        _svc.values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:C",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [[item, quantity, unit]]}
        ).execute()
        return f"✅ Added {item}: {quantity} {unit or 'units'} to order sheet"
    except Exception as e:
        return f"❌ Error adding to order sheet: {str(e)}"


def clear_order_sheet(
    spreadsheet_id: str = GROCERIES_INVENTORY_SHEET_ID,
    sheet_name: str = "Sheet2",
) -> str:
    """Clear all items from the order sheet."""
    try:
        # Clear all data except header
        _svc.values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A2:C"
        ).execute()
        return "✅ Order sheet cleared"
    except Exception as e:
        return f"❌ Error clearing order sheet: {str(e)}"


def update_inventory_item(
    item: str,
    quantity: float,
    unit: str = "",
    spreadsheet_id: str = GROCERIES_INVENTORY_SHEET_ID,
    sheet_name: str = "Sheet1",
) -> None:
    """Update existing row for `item`, or append if not found."""
    inv = get_inventory(spreadsheet_id, sheet_name)
    for idx, row in enumerate(inv, start=2):
        if row["item"].lower() == item.lower():
            _svc.values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A{idx}:C{idx}",
                valueInputOption="RAW",
                body={"values": [[item, quantity, unit]]}
            ).execute()
            return
    append_inventory_item(item, quantity, unit, spreadsheet_id, sheet_name)


def append_inventory_item(
    item: str,
    quantity: float,
    unit: str = "",
    spreadsheet_id: str = GROCERIES_INVENTORY_SHEET_ID,
    sheet_name: str = "Sheet1",
) -> None:
    """Append a new row with item, quantity, unit."""
    _svc.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:C",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [[item, quantity, unit]]}
    ).execute()
