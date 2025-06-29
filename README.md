# Smart Grocery Assistant with AI Agents & MCP 🛒

**Automate your weekly meal planning and grocery runs**—because let’s face it, we’re all a bit lazy sometimes! This project uses OpenAI’s Model Context Protocol (MCP) to build friendly AI agents that:

- Track your pantry staples in Google Sheets
- Collect your meal plan for the week
- Figure out what you’re missing
- And (with a quick “Yes!” from you) place the Instacart order!

---

## 🚀 High-Level Workflow

1. **Inventory Tracker Agent**  
   Kicks things off by asking your staple items (tomatoes, potatoes, milk, etc.) and saving counts to a `Inventory` sheet.  
2. **Meal Planner Agent**  
   Walks you through each day’s meals (Breakfast, Lunch, Dinner), writing your answers into a `Meals` sheet.  
3. **Shopping Cart Generator**  
   Breaks down each dish into ingredients, diffs against your inventory, and spits out a `ShoppingCart_<YYYY-WW>` sheet with missing items.  
4. **Review & Order Agent**  
   Emails you the shopping cart for a quick review. On a 👍 reply, it hits the Instacart API to build your cart at your favorite store and sends you the confirmation link.  
5. **Scheduler**  
   Fires everything off on your schedule (e.g. every Friday at 10 AM).

---

## 🧠 Agents & Components

| Agent                       | What It Does                                         |
|-----------------------------|------------------------------------------------------|
| **Inventory Tracker**       | Interactive prompts → updates your `Inventory` sheet |
| **Meal Planner**            | Collects 7-day meal plan → writes to `Meals` sheet   |
| **Shopping Cart Generator** | Computes missing ingredients → creates weekly cart    |
| **Review & Ordering**       | Emails cart → on approval calls Instacart API       |
| **Scheduler**               | Triggers the full flow at your chosen times         |

---

## 💻 Tech Stack & Tools

- **Python 3.10+** with Poetry for clean dependency & venv management
- **OpenAI GPT-4o** + MCP function calls for agent brains
- **Streamlit** (future UI/dashboard)
- **Google Sheets API** (Inventory & Meals)
- **Gmail API** (Notifications)
- **Instacart API** (Order creation)
- **python-dotenv** for loading `.env` secrets
- **Cron / GitHub Actions** for scheduling

---

## 🎬 Demo Video

> _Coming soon: a quick screen capture of the agents in action!_

---

## ⚙️ Setup & Installation

```bash
# 1. Clone the repo
git clone https://github.com/Lutir/meal_plan_mcp_app.git
cd meal_plan_mcp_app

# 2. Install dependencies
poetry install

# 3. Create a .env file with:
#    OPENAI_API_KEY
#    GOOGLE_SHEETS_CREDENTIALS_JSON=/path/to/service-account.json
#    GMAIL_CREDENTIALS_JSON=/path/to/service-account.json

# 4. Share your Google Sheet with the service account's email
#    Create tabs: Inventory, Meals, ShoppingCart_<YYYY-WW>

# 5. Run the quick tests:
poetry run python src/grocery_app/test_openai.py
poetry run python src/grocery_app/test_sheets.py

# 6. Manually trigger the workflow:
poetry run python src/grocery_app/weekly_trigger.py
