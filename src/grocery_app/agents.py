def ask_inventory() -> dict:
    """Prompt user for current inventory; returns {item: qty}"""

def ask_meal_plan() -> dict:
    """Prompt user for each day’s meals; returns {day: [meals]}"""

def diff_inventory(meals: dict, inventory: dict) -> list:
    """Compare meals → ingredients vs. inventory; return missing items"""

def send_email(subject: str, body: str) -> None:
    """Send an email via Gmail API"""

def create_instacart_order(items: list, store_id: str) -> str:
    """(Stub) Create an Instacart order and return order URL"""
