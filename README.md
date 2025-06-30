# 🍽️ Grocery App: AI Meal Planner & Inventory

## 🚀 Project Status (June 2025)

This project is a modern, AI-powered meal planning and grocery inventory management app with a beautiful Streamlit UI. It is designed for maximum intelligence and flexibility, with Google Sheets integration and OpenAI Agents SDK for ingredient extraction.

---

## 🎬 **Demo Videos**

See the app in action! Watch these quick demos to understand how the app works:

### 📋 Meal Planner Demo
![Meal Planner Demo](src/demo/Meal%20Planner.mov)

*Watch how to plan meals, extract ingredients with AI, and generate inventory-aware shopping lists.*

### 📦 Inventory Checker Demo  
![Inventory Checker Demo](src/demo/Inventory%20Checker.mov)

*See how to manage your inventory directly in the app with Google Sheets integration.*

---

## ✅ **What is Implemented**

### 1. **Editable Inventory Management (Google Sheets)**
- **UI:** Sidebar toggle lets you switch to "Inventory Checker".
- **Features:**
  - View your current inventory (read from Google Sheets).
  - Add, edit, or remove items (name, quantity, unit).
  - Save changes back to Google Sheets.
  - Refresh inventory with a button.

### 2. **Flexible Meal Planning UI**
- **UI:** Sidebar toggle lets you switch to "Meal Planner".
- **Features:**
  - Plan meals for any number of days (1-7) with slider.
  - Customizable meals per day with checkboxes.
  - Enter any dish name for each meal.
  - Flexible: you can skip meals, plan for 1–7 days, etc.
  - Day-by-day or master view (all days at once).

### 3. **AI-Powered Ingredient Extraction**
- **How it works:**
  - For each dish you enter, the app uses an **OpenAI Agent** (via the OpenAI Agents SDK) to extract a list of main raw ingredients.
  - The agent uses its own AI knowledge and can call the `get_recipe_ingredients` tool for a few common dishes.
  - **Excludes**: Spices, oil, salt, pepper, and pantry staples. Only main raw ingredients are included.

### 4. **Inventory-Aware Shopping List Generation** ⭐ **NEW!**
- **Features:**
  - **Smart Inventory Subtraction**: Automatically subtracts what you already have from what you need.
  - **Unit Matching**: Intelligently handles different units (e.g., "bottles" vs "gallons" of milk).
  - **Status Grouping**: Groups items by inventory status for better organization.
  - **Google Sheets Integration**: Saves shopping lists with metadata and individual items.
  - **Historical Tracking**: View and manage all your saved shopping lists.

### 5. **Shopping Lists Management** ⭐ **NEW!**
- **UI:** Sidebar toggle lets you switch to "Shopping Lists".
- **Features:**
  - View all saved shopping lists with creation dates and item counts.
  - Select and view individual shopping list items.
  - Track completion status of shopping items.
  - Persistent storage in Google Sheets with separate sheets for each list.

### 6. **Three Main Views**
- **🍽️ Meal Planner**: Plan meals and generate AI-powered shopping lists
- **📦 Inventory Checker**: Edit and manage your current inventory
- **🛒 Shopping Lists**: View and manage saved shopping lists

---

## 🟡 **Coming Soon!:**
- **Order/export to Instacart or other services.**
- **Email Integration where you can export Meal Plans and share it with people.**
- **AI meal suggestions based on inventory.**
- **Nutrition/price lookup tools.**
- **Multi-agent orchestration (handoffs between agents).**

---

## 🧠 **How the Workflow Operates**

1. **Edit inventory** in the UI (Google Sheets backend).
2. **Plan meals** in the UI.
3. **AI agent extracts ingredients** for each dish (no fallback, fully agentic).
4. **App generates inventory-aware shopping list** (subtracts what you have).
5. **Save shopping list** to Google Sheets for future reference.

---

## 🖥️ **How to Use**

- Open the app with:
  ```bash
  poetry run streamlit run src/grocery_app/streamlit_app.py
  ```
- Use the sidebar to switch between "Meal Planner", "Inventory Checker", and "Shopping Lists".
- Edit your inventory as needed.
- Plan your meals.
- Get an AI-generated, inventory-aware shopping list for your plan.
- Save and manage your shopping lists.

---

## 🗂️ **Project Structure**

```
src/grocery_app/
├── streamlit_app.py          # Main Streamlit UI with three views
├── sheet_tools.py            # Google Sheets integration (inventory + shopping lists)
├── openai_agents/
│   ├── __init__.py           # Package initialization
│   └── ingredient_extractor.py # AI-powered ingredient extraction agent
├── config.py                 # Configuration and environment variables
└── __init__.py               # Package initialization
```

**Key Files:**
- **`streamlit_app.py`**: Main application with three views (Meal Planner, Inventory Checker, Shopping Lists)
- **`sheet_tools.py`**: Google Sheets integration for inventory management and shopping list storage
- **`ingredient_extractor.py`**: OpenAI-powered ingredient extraction from meal names
- **`config.py`**: Environment variables and configuration settings

---

## 📝 **Environment Variables**

Set up your `.env` or environment variables for:
- `OPENAI_API_KEY` (for OpenAI Agents SDK)
- `GOOGLE_SHEETS_CREDENTIALS_JSON` (path to your Google Sheets service account JSON)
- `GROCERIES_INVENTORY_SHEET_ID` (your Google Sheet ID)

---

## 🧩 **Extending the App**
- Add order/export features to send your list to Instacart, Amazon Fresh, etc.
- Add AI meal suggestions based on current inventory.
- Add more AI tools (nutrition lookup, price lookup, etc.) as Python functions and register them with the agent.
- Add multi-agent orchestration for more complex workflows.

---

## 🏁 **Summary**
- **Editable inventory** (Google Sheets)
- **Flexible meal planner**
- **AI-powered ingredient extraction** (no fallback/manual logic)
- **Inventory-aware shopping list generation** ⭐
- **Shopping list management** ⭐
- **Three main views** for complete workflow
- **Ready for further AI and automation features!**

---

**Ready to commit!**
