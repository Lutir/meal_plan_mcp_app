# 🍽️ AI Meal Planner & Grocery App

A **truly AI-powered** meal planning and grocery inventory management application that uses OpenAI GPT-4o-mini for intelligent ingredient extraction.

## ✨ Features

- **🧠 AI-Powered Ingredient Extraction**: Uses OpenAI GPT-4o-mini to intelligently extract ingredients for ANY dish
- **Day-by-Day Meal Planning**: Plan your meals one day at a time with a clean, intuitive interface
- **Master View**: Fill all days at once when you're in a rush
- **Smart Shopping Lists**: Generate optimized shopping lists based on your meal plan
- **Minimal Database**: Only essential fallbacks - AI handles everything else
- **Google Sheets Integration**: Store inventory and orders in Google Sheets
- **Hybrid Agent Architecture**: Combines fast custom agents with AI agents for optimal performance

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Poetry
- OpenAI API key
- Google Sheets API credentials

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd grocery_app

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and Google Sheets credentials
```

### Run the App
```bash
# Start the Streamlit app
poetry run streamlit run src/grocery_app/streamlit_app.py
```

## 📁 Project Structure

```
src/grocery_app/
├── streamlit_app.py          # 🎯 Main Streamlit UI with inventory editor and meal planner
├── config.py                 # ⚙️ Configuration and environment variables
├── sheet_tools.py           # 📊 Google Sheets integration for inventory
├── agent_base.py            # 🏗️ Base classes for custom agents (legacy)
├── test_app.py              # 🧪 AI testing script
├── custom_agents/           # ⚡ Custom agent implementations (legacy)
│   ├── inventory_manager.py # 📦 Inventory management agent
│   └── shopping_optimizer.py # 🛒 Shopping optimization agent
├── openai_agents/           # 🤖 AI-powered agents using OpenAI Agents SDK
│   └── ingredient_extractor.py # 🍽️ AI ingredient extraction agent
└── demo.py                  # 🎬 Demo script showcasing AI capabilities
```

## 🎯 How It Works

### 1. Editable Inventory Management
- **Sidebar Toggle**: Switch between "Inventory Checker" and "Meal Planner" modes
- **Google Sheets Backend**: All inventory data stored in Google Sheets
- **Real-time Editing**: Add, edit, or remove items directly in the UI
- **Auto-save**: Changes are immediately saved back to Google Sheets

### 2. Flexible Meal Planning
- **Customizable Planning**: Choose number of days (1-7) and meals per day
- **Free-form Entry**: Enter any dish name (e.g., "Thai Green Curry", "Beef Tacos", "Sushi Roll")
- **Skip Meals**: Optional meal planning - you can leave meals empty
- **Dynamic Interface**: UI adapts to your planning preferences

### 3. AI-Powered Ingredient Extraction
- **OpenAI Agents SDK**: Uses GPT-4o-mini for intelligent ingredient extraction
- **Fully Agentic**: No fallback databases or manual logic - pure AI
- **Smart Filtering**: Excludes spices, oils, salt, pepper, and pantry staples
- **Raw Ingredients Only**: Focuses on main ingredients needed for shopping

### 4. Shopping List Generation
- **Aggregation**: Combines all ingredients from your meal plan
- **Deduplication**: Removes duplicates and counts quantities
- **Clean Output**: Generates a final, organized shopping list
- **Ready for Use**: Copy-paste ready for any grocery service

## 🔧 Architecture

### Current Implementation
- **🎯 Streamlit UI**: Single-page app with sidebar navigation
- **🤖 OpenAI Agents**: AI-powered ingredient extraction via OpenAI Agents SDK
- **📊 Google Sheets**: Inventory storage and management
- **🧠 Pure AI**: No static databases or fallback logic

### Agent Architecture
- **AI Ingredient Extractor**: Uses OpenAI GPT-4o-mini with custom tools
- **Tool Integration**: Can call `get_recipe_ingredients` function when helpful
- **Error Handling**: Clear error messages if AI extraction fails
- **Async Support**: Handles asyncio properly in Streamlit environment

### Data Flow
1. **Inventory**: Google Sheets ↔ Streamlit UI (bidirectional)
2. **Meal Planning**: User input → Streamlit state management
3. **Ingredient Extraction**: Dish names → OpenAI Agent → Ingredient lists
4. **Shopping List**: Aggregated ingredients → Deduplicated list → UI display

## 🧠 AI Capabilities

The AI can extract ingredients for:
- **International Cuisines**: Thai, Indian, Italian, Mexican, Japanese, etc.
- **Complex Dishes**: Biryani, Curry, Pizza, Sushi, Tacos, etc.
- **Regional Variations**: Different styles and preparations
- **Unknown Dishes**: Intelligent fallbacks for unfamiliar dishes

### Example AI Output
```
🍽️ Thai Green Curry:
📝 1 tablespoon vegetable oil, 2-3 tablespoons green curry paste, 
1 can (400ml) coconut milk, 400g chicken breast, 1 cup eggplant, 
1 cup bell peppers, 1 cup bamboo shoots, 2-3 kaffir lime leaves, 
1 tablespoon fish sauce, 1 tablespoon sugar, fresh basil leaves, 
salt to taste, lime wedges for serving
```

## 🛠️ Development

### Adding New AI Capabilities
- Extend the `AIngredientExtractorAgent` class
- Add new MCP tools for external data sources
- Enhance the AI prompts for better ingredient extraction

### Extending Agents
- Custom agents inherit from `BaseAgent` in `agent_base.py`
- AI agents use the OpenAI Agents SDK
- MCP tools provide external data access

## 📝 Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id
```

## 🧪 Testing

Test the AI ingredient extraction:
```bash
poetry run python src/grocery_app/test_app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
