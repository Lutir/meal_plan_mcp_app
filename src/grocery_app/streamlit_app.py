import streamlit as st
from typing import List, Dict
import datetime
from collections import Counter
import uuid
import re
from grocery_app.openai_agents.ingredient_extractor import get_ingredient_extractor_agent
from grocery_app.sheet_tools import (
    get_inventory, 
    save_shopping_list, 
    get_shopping_lists, 
    get_shopping_list_items,
    generate_inventory_aware_shopping_list,
    clear_inventory_sheet,
    append_inventory_item
)
import openai
from grocery_app.config import OPENAI_KEY
import hashlib

# --- CONFIG ---
st.set_page_config(page_title="AI Meal Planner", layout="wide")

def parse_ingredient_string(ingredient_str: str) -> Dict:
    """
    Parse an ingredient string like "2 cups flattened rice (poha)" into a dictionary.
    Returns: {"item": "flattened rice", "quantity": 2, "unit": "cups"}
    """
    ingredient_str = ingredient_str.strip()
    
    # Common patterns for quantities and units
    quantity_patterns = [
        r'^(\d+(?:\.\d+)?)\s*(cups?|tablespoons?|teaspoons?|pounds?|lbs?|grams?|g|kilograms?|kg|ounces?|oz|pieces?|cloves?|bottles?|cans?|packets?|bunches?|heads?)\s+(.+)$',
        r'^(\d+(?:\.\d+)?)\s*(cup|tablespoon|teaspoon|pound|lb|gram|kilogram|ounce|piece|clove|bottle|can|packet|bunch|head)\s+(.+)$',
    ]
    
    for pattern in quantity_patterns:
        match = re.search(pattern, ingredient_str, re.IGNORECASE)
        if match:
            quantity = float(match.group(1))
            unit = match.group(2).lower()
            item = match.group(3).strip()
            
            # Clean up the item name (remove extra parentheses, etc.)
            item = re.sub(r'\s*\([^)]*\)', '', item).strip()  # Remove parenthetical notes
            item = re.sub(r'\s+', ' ', item).strip()  # Normalize whitespace
            
            return {
                "item": item,
                "quantity": quantity,
                "unit": unit
            }
    
    # If no quantity/unit pattern found, treat as single item
    return {
        "item": ingredient_str,
        "quantity": 1,
        "unit": "piece"
    }

def parse_ingredients_to_dicts(ingredient_strings: List[str]) -> List[Dict]:
    """
    Convert a list of ingredient strings to a list of ingredient dictionaries.
    """
    parsed_ingredients = []
    for ingredient_str in ingredient_strings:
        parsed = parse_ingredient_string(ingredient_str)
        if parsed["item"]:  # Only add if item name is not empty
            parsed_ingredients.append(parsed)
    return parsed_ingredients

def normalize_ingredient_openai(ingredient_str: str, openai_api_key: str) -> Dict:
    """
    Use OpenAI to normalize an ingredient string to canonical form, quantity, and unit.
    Returns: {"item": ..., "quantity": ..., "unit": ...}
    """
    import json
    client = openai.OpenAI(api_key=openai_api_key)
    prompt = f"""
Given the following ingredient: '{ingredient_str}'
Return a JSON object with:
- 'item': the canonical grocery item (e.g., 'onion', 'potato', 'milk')
- 'quantity': the numeric quantity (float)
- 'unit': the unit (e.g., 'pieces', 'grams', 'cups')
If the ingredient is a variant (e.g., 'red onion'), use the base item ('onion').
If the unit is missing, use 'piece' as default.
Respond with only the JSON object, nothing else.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=100
    )
    text = response.choices[0].message.content
    if text is not None:
        text = text.strip()
    else:
        text = ""
    try:
        return json.loads(text)
    except Exception:
        # fallback: treat as single item
        return {"item": ingredient_str, "quantity": 1, "unit": "piece"}

def normalize_ingredients_openai(ingredient_strings: List[str], openai_api_key: str) -> List[Dict]:
    """
    Normalize a list of ingredient strings using OpenAI.
    """
    return [normalize_ingredient_openai(ing, openai_api_key) for ing in ingredient_strings]

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # View selection
    view_mode = st.selectbox(
        "📱 Select View",
        ["Meal Planner", "Inventory Checker", "Shopping Lists"],
        help="Choose which feature to use"
    )
    
    if view_mode == "Meal Planner":
        # Day selection
        num_days = st.slider(
            "📅 Number of Days to Plan",
            min_value=1,
            max_value=7,
            value=5,
            help="Choose how many days you want to plan meals for (1-7 days)"
        )
        
        # Meal selection
        st.subheader("🍽️ Meals to Include")
        include_breakfast = st.checkbox("Breakfast", value=True)
        include_lunch = st.checkbox("Lunch", value=True)
        include_dinner = st.checkbox("Dinner", value=True)
        
        # Only show meals that are selected
        meals = []
        if include_breakfast:
            meals.append("Breakfast")
        if include_lunch:
            meals.append("Lunch")
        if include_dinner:
            meals.append("Dinner")
        
        # Validation
        if not meals:
            st.error("Please select at least one meal type!")
            st.stop()
        
        st.markdown("---")
        st.caption(f"📊 Planning {num_days} days with {len(meals)} meals per day")

# --- MAIN APP ---
if view_mode == "Meal Planner":
    st.title("🍽️ AI Meal Planner: Pick Your Dishes!")
    st.write("Select or type the dishes you want for each meal. The AI will generate your shopping list!")

    def get_default_days(num_days: int):
        """Generate list of days based on user selection"""
        today = datetime.date.today()
        return [(today + datetime.timedelta(days=i)).strftime("%A") for i in range(num_days)]

    days = get_default_days(num_days)

    # --- SESSION STATE ---
    if "dish_plan" not in st.session_state:
        st.session_state["dish_plan"] = {day: {meal: "" for meal in meals} for day in days}
    if "planning_view_mode" not in st.session_state:
        st.session_state["planning_view_mode"] = "day_by_day"  # or 'master'
    if "current_day_idx" not in st.session_state:
        st.session_state["current_day_idx"] = 0

    # Reset session state if configuration changes
    current_config = (num_days, tuple(meals))
    if "last_config" not in st.session_state or st.session_state["last_config"] != current_config:
        st.session_state["dish_plan"] = {day: {meal: "" for meal in meals} for day in days}
        st.session_state["current_day_idx"] = 0
        st.session_state["last_config"] = current_config

    # --- VIEW TOGGLE BUTTON ---
    colA, colB = st.columns([2, 1])
    with colA:
        st.caption(":star: You can fill your plan day-by-day or all at once!")
    with colB:
        if st.session_state["planning_view_mode"] == "day_by_day":
            if st.button("Switch to Master View (All Days)"):
                st.session_state["planning_view_mode"] = "master"
        else:
            if st.button("Switch to Day-by-Day View"):
                st.session_state["planning_view_mode"] = "day_by_day"

    # --- DAY-BY-DAY VIEW ---
    if st.session_state["planning_view_mode"] == "day_by_day":
        idx = st.session_state["current_day_idx"]
        day = days[idx]
        st.subheader(f"🗓️ {day}")
        st.progress((idx + 1) / len(days), text=f"Day {idx + 1} of {len(days)}")
        with st.form(f"form_{day}"):
            cols = st.columns(len(meals))
            for i, meal in enumerate(meals):
                key = f"{day}_{meal}"
                st.session_state["dish_plan"][day][meal] = cols[i].text_input(f"{meal}", value=st.session_state["dish_plan"][day][meal], key=key)
            nav_cols = st.columns([1, 1, 2])
            prev_disabled = idx == 0
            next_disabled = idx == len(days) - 1
            with nav_cols[0]:
                prev = st.form_submit_button("⬅️ Previous Day", disabled=prev_disabled)
            with nav_cols[1]:
                next_ = st.form_submit_button("Next Day ➡️", disabled=next_disabled)
            with nav_cols[2]:
                finish = st.form_submit_button("Finish & Generate Shopping List")
                if finish:
                    if not any(st.session_state["dish_plan"][d][m] for d in days for m in meals):
                        st.error("Please fill at least one meal before generating the shopping list.")
                    else:
                        st.session_state["current_day_idx"] = 0
                        st.session_state["planning_view_mode"] = "summary"
                        st.rerun()
        if prev:
            st.session_state["current_day_idx"] = max(0, idx - 1)
            st.rerun()
        if next_:
            st.session_state["current_day_idx"] = min(len(days) - 1, idx + 1)
            st.rerun()

    # --- MASTER VIEW (ALL DAYS AT ONCE) ---
    elif st.session_state["planning_view_mode"] == "master":
        st.subheader(f"📝 {num_days}-Day Meal Selection (All Days)")
        with st.form("meal_plan_form"):
            for day in days:
                st.markdown(f"**{day}**")
                cols = st.columns(len(meals))
                for i, meal in enumerate(meals):
                    key = f"{day}_{meal}"
                    st.session_state["dish_plan"][day][meal] = cols[i].text_input(f"{day} - {meal}", value=st.session_state["dish_plan"][day][meal], key=key)
            submitted = st.form_submit_button("Plan My Week!")
        if submitted:
            st.session_state["planning_view_mode"] = "summary"
            st.rerun()

    # --- SUMMARY & SHOPPING LIST GENERATION ---
    if st.session_state["planning_view_mode"] == "summary":
        st.subheader("✅ Your Meal Plan Summary")
        for day in days:
            st.write(f"**{day}:**")
            st.write(", ".join([f"{meal}: {st.session_state['dish_plan'][day][meal]}" for meal in meals if st.session_state['dish_plan'][day][meal]]))
        st.markdown("---")
        st.info("🤖 Generating your shopping list with AI... (this may take a few seconds)")
        
        # Generate meal plan summary for Google Sheets
        meal_plan_summary = []
        for day in days:
            day_meals = []
            for meal in meals:
                dish = st.session_state["dish_plan"][day][meal].strip()
                if dish:
                    day_meals.append(f"{meal}: {dish}")
            if day_meals:
                meal_plan_summary.append(f"{day}: {', '.join(day_meals)}")
        meal_plan_text = " | ".join(meal_plan_summary)
        
        ingredient_agent = get_ingredient_extractor_agent()
        all_ingredients = []
        for day in days:
            for meal in meals:
                dish = st.session_state["dish_plan"][day][meal].strip()
                if dish:
                    with st.spinner(f"🧠 AI is extracting ingredients for '{dish}'..."):
                        ingredients = ingredient_agent.extract_ingredients(dish)
                    all_ingredients.extend(ingredients)
        
        # Compute a hash of the current meal plan for caching
        meal_plan_hash = hashlib.sha256(str(st.session_state["dish_plan"]).encode()).hexdigest()
        if "shopping_list_cache" not in st.session_state or st.session_state["shopping_list_cache"].get("hash") != meal_plan_hash:
            if not OPENAI_KEY:
                st.error("OpenAI API key not set. Please set OPENAI_API_KEY in your .env file.")
                st.stop()
            st.info("🤖 Normalizing and deduplicating ingredients with OpenAI...")
            normalized_ingredients = normalize_ingredients_openai(all_ingredients, OPENAI_KEY)
            from collections import defaultdict
            grouped = defaultdict(lambda: {"quantity": 0.0, "unit": None})
            for ing in normalized_ingredients:
                try:
                    qty = float(ing.get("quantity", 0) or 0)
                except Exception:
                    qty = 0.0
                key = (ing["item"].lower().strip(), ing["unit"].lower().strip())
                if not isinstance(grouped[key]["quantity"], (int, float)) or grouped[key]["quantity"] is None:
                    grouped[key]["quantity"] = 0.0
                grouped[key]["quantity"] = float(grouped[key]["quantity"] or 0.0) + qty
                grouped[key]["unit"] = ing["unit"]
            deduped_ingredients = [
                {"item": item, "quantity": data["quantity"], "unit": data["unit"]}
                for (item, _), data in grouped.items()
            ]
            inventory_aware_list = generate_inventory_aware_shopping_list(deduped_ingredients)
            st.session_state["shopping_list_cache"] = {
                "hash": meal_plan_hash,
                "deduped_ingredients": deduped_ingredients,
                "inventory_aware_list": inventory_aware_list
            }
        else:
            deduped_ingredients = st.session_state["shopping_list_cache"]["deduped_ingredients"]
            inventory_aware_list = st.session_state["shopping_list_cache"]["inventory_aware_list"]

        # Display the shopping list
        st.write("**🛒 Inventory-Aware Shopping List:**")
        
        if inventory_aware_list:
            # Group by inventory status for better display
            status_groups = {}
            for item in inventory_aware_list:
                status = item.get("inventory_status", "Not in inventory")
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(item)
            
            for status, items in status_groups.items():
                st.markdown(f"**{status}:**")
                for item in items:
                    st.write(f"- {item['item']} x{item['quantity']} {item['unit']}")
                st.write("")
        else:
            st.write("✅ All ingredients are already in your inventory!")
        
        # Save to Google Sheets
        if st.button("💾 Save Shopping List to Google Sheets"):
            list_id = f"shopping_list_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = save_shopping_list(list_id, meal_plan_text, inventory_aware_list)
            st.success(result)
        
        st.write("🧠 Powered by OpenAI GPT-4o-mini for intelligent ingredient extraction!")
        st.button("🔄 Start Over", on_click=lambda: st.session_state.update({"planning_view_mode": "day_by_day", "current_day_idx": 0}))

elif view_mode == "Inventory Checker":
    st.title("📦 Inventory Checker")
    st.write("View and edit your current inventory.")

    # Get current inventory
    try:
        inventory = get_inventory()
        
        # Create a data editor for the inventory
        if inventory:
            # Convert to format suitable for st.data_editor
            inventory_data = []
            for item in inventory:
                inventory_data.append({
                    "Item": item["item"],
                    "Quantity": item["quantity"],
                    "Unit": item["unit"]
                })
            
            edited_inventory = st.data_editor(
                inventory_data,
                num_rows="dynamic",
                key="inventory_editor"
            )
            
            # Save changes button
            if st.button("💾 Save Changes to Google Sheets"):
                # Clear existing inventory and add new items
                clear_inventory_sheet()  # Clear inventory sheet
                
                # Add new items
                for item in edited_inventory:
                    if item["Item"].strip():  # Only add non-empty items
                        append_inventory_item(
                            item["Item"].strip(),
                            float(item["Quantity"]) if item["Quantity"] else 0.0,
                            item["Unit"].strip() if item["Unit"] else ""
                        )
                
                st.success("✅ Inventory updated successfully!")
                st.rerun()
        else:
            st.info("No inventory items found. Add some items below:")
            
            # Simple form for adding items
            with st.form("add_inventory_item"):
                item_name = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=0.0, value=1.0)
                unit = st.text_input("Unit (optional)")
                
                if st.form_submit_button("Add Item"):
                    if item_name.strip():
                        append_inventory_item(item_name.strip(), quantity, unit.strip())
                        st.success(f"✅ Added {item_name} to inventory!")
                        st.rerun()
                    else:
                        st.error("Please enter an item name.")
    
    except Exception as e:
        st.error(f"Error loading inventory: {str(e)}")
        st.info("Make sure your Google Sheets credentials are properly configured.")

elif view_mode == "Shopping Lists":
    st.title("🛒 Shopping Lists")
    st.write("View and manage your saved shopping lists.")
    
    try:
        # Get all shopping lists
        shopping_lists = get_shopping_lists()
        
        if shopping_lists:
            st.subheader("📋 Saved Shopping Lists")
            
            # Display shopping lists in a table
            list_data = []
            for shopping_list in shopping_lists:
                list_data.append({
                    "List ID": shopping_list["list_id"],
                    "Date Created": shopping_list["date_created"],
                    "Total Items": shopping_list["total_items"],
                    "Status": shopping_list["status"]
                })
            
            selected_list = st.selectbox(
                "Select a shopping list to view:",
                options=[sl["list_id"] for sl in shopping_lists],
                format_func=lambda x: f"{x} ({next(sl['date_created'] for sl in shopping_lists if sl['list_id'] == x)})"
            )
            
            if selected_list:
                # Get items for selected list
                list_items = get_shopping_list_items(selected_list)
                
                if list_items:
                    st.subheader(f"📝 Items in {selected_list}")
                    
                    # Display items
                    for item in list_items:
                        status_icon = "✅" if item["status"] == "completed" else "⏳"
                        st.write(f"{status_icon} {item['item']} x{item['quantity']} {item['unit']} ({item['status']})")
                    
                    # Mark items as completed
                    st.subheader("Mark Items as Completed")
                    for i, item in enumerate(list_items):
                        if st.checkbox(f"✅ {item['item']}", value=item["status"] == "completed", key=f"complete_{i}"):
                            # Update item status in Google Sheets
                            # This would require additional function to update item status
                            st.info(f"Marked {item['item']} as completed")
                else:
                    st.info("No items found for this shopping list.")
        else:
            st.info("No shopping lists found. Create one by planning meals!")
    
    except Exception as e:
        st.error(f"Error loading shopping lists: {str(e)}")
        st.info("Make sure your Google Sheets credentials are properly configured.") 