"""
Inventory Manager Agent
Handles inventory assessment and initial order creation
"""

from typing import Dict, List, Any
from grocery_app.agent_base import BaseAgent, AgentResult, AgentContext
from grocery_app.sheet_tools import get_inventory, add_to_order_sheet, clear_order_sheet


class InventoryManagerAgent(BaseAgent):
    """Agent responsible for inventory assessment and initial order creation"""
    
    def __init__(self):
        super().__init__(
            name="InventoryManager",
            description="Assesses current inventory and creates initial grocery orders"
        )
        self.add_tool(get_inventory)
        self.add_tool(add_to_order_sheet)
        self.add_tool(clear_order_sheet)
    
    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute inventory assessment and order creation"""
        try:
            self.log("Starting inventory assessment")
            
            # Get current inventory from Google Sheets
            inventory = get_inventory()
            if not inventory:
                return AgentResult(
                    success=False,
                    data=None,
                    message="No inventory data found"
                )
            
            # Update context with inventory
            context.inventory = inventory
            
            # Analyze inventory for low/out-of-stock items
            low_stock_items = []
            out_of_stock_items = []
            
            for item in inventory:
                if item["quantity"] == 0:
                    out_of_stock_items.append(item)
                elif item["quantity"] <= 1:  # Consider items with 1 or less as low stock
                    low_stock_items.append(item)
            
            # Create initial order recommendations
            initial_order = []
            
            # Add out-of-stock items with default quantities
            for item in out_of_stock_items:
                default_qty = self._get_default_quantity(item["unit"])
                initial_order.append({
                    "item": item["item"],
                    "quantity": default_qty,
                    "unit": item["unit"],
                    "reason": "out_of_stock"
                })
            
            # Add low stock items with top-up quantities
            for item in low_stock_items:
                top_up_qty = self._get_top_up_quantity(item["unit"])
                initial_order.append({
                    "item": item["item"],
                    "quantity": top_up_qty,
                    "unit": item["unit"],
                    "reason": "low_stock"
                })
            
            # Clear existing order sheet and add new items
            clear_order_sheet()
            for order_item in initial_order:
                add_to_order_sheet(
                    order_item["item"],
                    order_item["quantity"],
                    order_item["unit"]
                )
            
            # Prepare result data
            result_data = {
                "inventory_count": len(inventory),
                "out_of_stock_count": len(out_of_stock_items),
                "low_stock_count": len(low_stock_items),
                "initial_order": initial_order,
                "out_of_stock_items": out_of_stock_items,
                "low_stock_items": low_stock_items
            }
            
            self.log(f"Assessment complete: {len(inventory)} items, {len(out_of_stock_items)} out of stock, {len(low_stock_items)} low stock")
            
            return AgentResult(
                success=True,
                data=result_data,
                message=f"Inventory assessment complete. Found {len(out_of_stock_items)} out-of-stock and {len(low_stock_items)} low-stock items.",
                next_agent="MealPlanner",  # Handoff to meal planner
                context_updates={
                    "inventory": inventory,
                    "initial_order": initial_order
                }
            )
            
        except Exception as e:
            self.log(f"Error during inventory assessment: {str(e)}", "ERROR")
            return AgentResult(
                success=False,
                data=None,
                message=f"Error during inventory assessment: {str(e)}"
            )
    
    def _get_default_quantity(self, unit: str) -> float:
        """Get default quantity for out-of-stock items based on unit"""
        default_quantities = {
            "pieces": 2,
            "pcs": 2,
            "cans": 3,
            "bottles": 2,
            "packets": 2,
            "bags": 1,
            "boxes": 1,
            "kg": 1.0,
            "liters": 1.0,
            "ml": 500.0,
            "grams": 500.0
        }
        
        # Try exact match first
        if unit.lower() in default_quantities:
            return default_quantities[unit.lower()]
        
        # Try partial match
        for key, value in default_quantities.items():
            if key in unit.lower():
                return value
        
        # Default fallback
        return 1.0
    
    def _get_top_up_quantity(self, unit: str) -> float:
        """Get top-up quantity for low-stock items"""
        # For low stock, add 1-2 more of the same unit
        if any(key in unit.lower() for key in ["pieces", "pcs", "cans", "bottles", "packets"]):
            return 2.0
        elif any(key in unit.lower() for key in ["kg", "liters"]):
            return 1.0
        else:
            return 1.0 