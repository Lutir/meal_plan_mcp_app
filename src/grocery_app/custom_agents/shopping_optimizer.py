"""
Shopping Optimizer Agent
Combines inventory needs with meal ingredients and creates final shopping list
"""

from typing import Dict, List, Any
from grocery_app.agent_base import BaseAgent, AgentResult, AgentContext
from grocery_app.sheet_tools import add_to_order_sheet, get_order_sheet


class ShoppingOptimizerAgent(BaseAgent):
    """Agent responsible for creating final optimized shopping list"""
    
    def __init__(self):
        super().__init__(
            name="ShoppingOptimizer",
            description="Combines inventory needs with meal ingredients and creates final shopping list"
        )
        self.add_tool(add_to_order_sheet)
        self.add_tool(get_order_sheet)
    
    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute shopping list optimization"""
        try:
            self.log("Starting shopping list optimization")
            
            # Get required ingredients from meal planning
            required_ingredients = context.metadata.get("required_ingredients", [])
            
            # Get current inventory
            current_inventory = context.inventory
            
            # Create final shopping list by combining needs and removing what we have
            final_shopping_list = self._create_final_shopping_list(
                required_ingredients, 
                current_inventory,
                context
            )
            
            # Update the order sheet with final list
            self._update_order_sheet(final_shopping_list)
            
            # Update context with final shopping list
            context.shopping_list = final_shopping_list
            
            self.log(f"Final shopping list created with {len(final_shopping_list)} items")
            
            return AgentResult(
                success=True,
                data=final_shopping_list,
                message=f"Final shopping list created with {len(final_shopping_list)} items",
                context_updates={
                    "shopping_list": final_shopping_list
                }
            )
            
        except Exception as e:
            self.log(f"Error during shopping optimization: {str(e)}", "ERROR")
            return AgentResult(
                success=False,
                data=None,
                message=f"Error during shopping optimization: {str(e)}"
            )
    
    def _create_final_shopping_list(self, required_ingredients: List[Dict], current_inventory: List[Dict], context: AgentContext) -> List[Dict]:
        """Create final shopping list by combining needs and removing what we have"""
        
        # Create inventory lookup
        inventory_lookup = {}
        for item in current_inventory:
            inventory_lookup[item["item"].lower()] = item["quantity"]
        
        final_list = []
        
        for ingredient in required_ingredients:
            item_name = ingredient["item"].lower()
            needed_qty = ingredient["quantity"]
            
            # Check if we have this item in inventory
            if item_name in inventory_lookup:
                available_qty = inventory_lookup[item_name]
                if available_qty >= needed_qty:
                    # We have enough, skip this item
                    continue
                else:
                    # We need more
                    additional_needed = needed_qty - available_qty
                    final_list.append({
                        "item": ingredient["item"],
                        "quantity": additional_needed,
                        "unit": ingredient["unit"],
                        "reason": "meal_planning",
                        "sources": ingredient.get("sources", [])
                    })
            else:
                # We don't have this item at all
                final_list.append({
                    "item": ingredient["item"],
                    "quantity": needed_qty,
                    "unit": ingredient["unit"],
                    "reason": "meal_planning",
                    "sources": ingredient.get("sources", [])
                })
        
        # Add any items from initial inventory order that aren't covered by meal planning
        initial_order = context.metadata.get("initial_order", [])
        for order_item in initial_order:
            item_name = order_item["item"].lower()
            
            # Check if this item is already in our final list
            already_included = any(
                item["item"].lower() == item_name 
                for item in final_list
            )
            
            if not already_included:
                final_list.append({
                    "item": order_item["item"],
                    "quantity": order_item["quantity"],
                    "unit": order_item["unit"],
                    "reason": order_item["reason"],
                    "sources": ["inventory_assessment"]
                })
        
        return final_list
    
    def _update_order_sheet(self, shopping_list: List[Dict]):
        """Update the order sheet with the final shopping list"""
        # Clear existing order sheet
        from grocery_app.sheet_tools import clear_order_sheet
        clear_order_sheet()
        
        # Add new items
        for item in shopping_list:
            add_to_order_sheet(
                item["item"],
                item["quantity"],
                item["unit"]
            )
    
    def _categorize_items(self, shopping_list: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize items by store section for better shopping experience"""
        categories = {
            "produce": [],
            "dairy": [],
            "pantry": [],
            "frozen": [],
            "beverages": [],
            "other": []
        }
        
        category_mappings = {
            "produce": ["vegetables", "fruits", "onions", "tomatoes", "garlic"],
            "dairy": ["milk", "eggs", "butter", "yogurt", "cheese"],
            "pantry": ["rice", "pasta", "oats", "oil", "spices", "soy sauce"],
            "frozen": ["frozen vegetables", "frozen fruits"],
            "beverages": ["juice", "soda", "water"]
        }
        
        for item in shopping_list:
            item_name = item["item"].lower()
            categorized = False
            
            for category, keywords in category_mappings.items():
                if any(keyword in item_name for keyword in keywords):
                    categories[category].append(item)
                    categorized = True
                    break
            
            if not categorized:
                categories["other"].append(item)
        
        return categories 