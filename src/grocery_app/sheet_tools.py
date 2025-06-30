# src/grocery_app/sheets_tool.py
from typing import List, Dict, Optional
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from grocery_app.config import GOOGLE_SHEETS_CREDENTIALS_JSON, GROCERIES_INVENTORY_SHEET_ID

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Ensure required environment variables are set
if not GOOGLE_SHEETS_CREDENTIALS_JSON:
    raise ValueError("GOOGLE_SHEETS_CREDENTIALS_JSON environment variable is required")
if not GROCERIES_INVENTORY_SHEET_ID:
    raise ValueError("GROCERIES_INVENTORY_SHEET_ID environment variable is required")

_creds = Credentials.from_service_account_file(
    GOOGLE_SHEETS_CREDENTIALS_JSON, scopes=SCOPES
)
_svc = build("sheets", "v4", credentials=_creds).spreadsheets()


def get_inventory(
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet1"
) -> List[Dict]:
    """Read Sheet1!A2:C and return list of {"item", "quantity", "unit"}."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
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
        unit = row[2].strip() if len(row) > 2 and row[2] else ""
        inventory.append({"item": item, "quantity": qty, "unit": unit})
    return inventory


def get_order_sheet(
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet2"
) -> List[Dict]:
    """Read order sheet and return list of {"item", "quantity", "unit"}."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
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
        unit = row[2].strip() if len(row) > 2 and row[2] else ""
        orders.append({"item": item, "quantity": qty, "unit": unit})
    return orders


def get_shopping_lists(
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "ShoppingLists"
) -> List[Dict]:
    """Read shopping lists sheet and return list of shopping lists with metadata."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
    try:
        resp = _svc.values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A2:E"
        ).execute()
        values = resp.get("values", [])
        shopping_lists = []
        for row in values:
            if not row or not row[0].strip():
                continue
            list_id = row[0].strip()
            date_created = row[1].strip() if len(row) > 1 and row[1] else ""
            meal_plan = row[2].strip() if len(row) > 2 and row[2] else ""
            total_items = int(row[3]) if len(row) > 3 and row[3] else 0
            status = row[4].strip() if len(row) > 4 and row[4] else "active"
            shopping_lists.append({
                "list_id": list_id,
                "date_created": date_created,
                "meal_plan": meal_plan,
                "total_items": total_items,
                "status": status
            })
        return shopping_lists
    except Exception:
        # If sheet doesn't exist, return empty list
        return []


def save_shopping_list(
    list_id: str,
    meal_plan: str,
    shopping_items: List[Dict],
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "ShoppingLists"
) -> str:
    """Save a shopping list to Google Sheets."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
    try:
        # First, ensure the shopping lists sheet exists
        try:
            _svc.values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1"
            ).execute()
        except Exception:
            # Create the sheet if it doesn't exist
            _svc.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": sheet_name,
                                    "gridProperties": {
                                        "rowCount": 1000,
                                        "columnCount": 10
                                    }
                                }
                            }
                        }
                    ]
                }
            ).execute()
            
            # Add headers
            _svc.values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:E1",
                valueInputOption="RAW",
                body={"values": [["List ID", "Date Created", "Meal Plan", "Total Items", "Status"]]}
            ).execute()
        
        # Add shopping list metadata
        from datetime import datetime
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M")
        total_items = len(shopping_items)
        
        _svc.values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:E",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [[list_id, date_created, meal_plan, total_items, "active"]]}
        ).execute()
        
        # Save individual items to a separate sheet
        items_sheet_name = f"ShoppingList_{list_id}"
        try:
            _svc.values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{items_sheet_name}!A1"
            ).execute()
        except Exception:
            # Create items sheet
            _svc.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": items_sheet_name,
                                    "gridProperties": {
                                        "rowCount": 1000,
                                        "columnCount": 5
                                    }
                                }
                            }
                        }
                    ]
                }
            ).execute()
            
            # Add headers
            _svc.values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{items_sheet_name}!A1:D1",
                valueInputOption="RAW",
                body={"values": [["Item", "Quantity", "Unit", "Status"]]}
            ).execute()
        
        # Clear existing items and add new ones
        _svc.values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{items_sheet_name}!A2:D"
        ).execute()
        
        # Add shopping items
        items_data = []
        for item in shopping_items:
            items_data.append([
                item["item"],
                item["quantity"],
                item["unit"],
                "pending"
            ])
        
        if items_data:
            _svc.values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{items_sheet_name}!A:D",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": items_data}
            ).execute()
        
        return f"✅ Shopping list '{list_id}' saved with {total_items} items"
    except Exception as e:
        return f"❌ Error saving shopping list: {str(e)}"


def get_shopping_list_items(
    list_id: str,
    spreadsheet_id: Optional[str] = None,
    sheet_name: Optional[str] = None
) -> List[Dict]:
    """Get items for a specific shopping list."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
    if sheet_name is None:
        sheet_name = f"ShoppingList_{list_id}"
    
    try:
        resp = _svc.values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A2:D"
        ).execute()
        values = resp.get("values", [])
        items = []
        for row in values:
            if not row or not row[0].strip():
                continue
            item = row[0].strip()
            qty = float(row[1]) if len(row) > 1 and row[1] else 0.0
            unit = row[2].strip() if len(row) > 2 and row[2] else ""
            status = row[3].strip() if len(row) > 3 and row[3] else "pending"
            items.append({
                "item": item,
                "quantity": qty,
                "unit": unit,
                "status": status
            })
        return items
    except Exception:
        return []


def generate_inventory_aware_shopping_list(
    required_ingredients: List[Dict],
    spreadsheet_id: Optional[str] = None,
    inventory_sheet: str = "Sheet1"
) -> List[Dict]:
    """Generate inventory-aware shopping list by subtracting current inventory from required ingredients."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
    current_inventory = get_inventory(spreadsheet_id, inventory_sheet)
    
    # Create inventory lookup dictionary
    inventory_lookup = {}
    for item in current_inventory:
        key = item["item"].lower().strip()
        inventory_lookup[key] = {
            "quantity": item["quantity"],
            "unit": item["unit"]
        }
    
    shopping_list = []
    
    for ingredient in required_ingredients:
        item_name = ingredient["item"].lower().strip()
        required_qty = ingredient["quantity"]
        required_unit = ingredient["unit"]
        
        if item_name in inventory_lookup:
            # Item exists in inventory
            available_qty = inventory_lookup[item_name]["quantity"]
            available_unit = inventory_lookup[item_name]["unit"]
            
            # If units match, subtract available from required
            if available_unit.lower() == required_unit.lower():
                needed_qty = max(0, required_qty - available_qty)
                if needed_qty > 0:
                    shopping_list.append({
                        "item": ingredient["item"],
                        "quantity": needed_qty,
                        "unit": required_unit,
                        "inventory_status": f"Have {available_qty} {available_unit}"
                    })
            else:
                # Units don't match, add to shopping list
                shopping_list.append({
                    "item": ingredient["item"],
                    "quantity": required_qty,
                    "unit": required_unit,
                    "inventory_status": f"Have {available_qty} {available_unit} (different unit)"
                })
        else:
            # Item not in inventory, add to shopping list
            shopping_list.append({
                "item": ingredient["item"],
                "quantity": required_qty,
                "unit": required_unit,
                "inventory_status": "Not in inventory"
            })
    
    return shopping_list


def add_to_order_sheet(
    item: str,
    quantity: float,
    unit: str = "",
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet2",
) -> str:
    """Add an item to the order sheet."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
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
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet2",
) -> str:
    """Clear all items from the order sheet."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
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
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet1",
) -> None:
    """Update existing row for `item`, or append if not found."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
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
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet1",
) -> None:
    """Append a new row with item, quantity, unit."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
    _svc.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:C",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [[item, quantity, unit]]}
    ).execute()


def clear_inventory_sheet(
    spreadsheet_id: Optional[str] = None,
    sheet_name: str = "Sheet1",
) -> str:
    """Clear all items from the inventory sheet."""
    if spreadsheet_id is None:
        spreadsheet_id = GROCERIES_INVENTORY_SHEET_ID
    try:
        # Clear all data except header
        _svc.values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A2:C"
        ).execute()
        return "✅ Inventory sheet cleared"
    except Exception as e:
        return f"❌ Error clearing inventory sheet: {str(e)}"
