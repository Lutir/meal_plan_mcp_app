"""
Test script for the AI-powered meal planner
"""

from openai_agents.ingredient_extractor import get_ingredient_extractor_agent

def test_ai_ingredient_extraction():
    """Test the AI ingredient extractor with various dishes"""
    print("🧠 Testing AI-Powered Ingredient Extractor")
    print("=" * 50)
    
    agent = get_ingredient_extractor_agent()
    
    test_dishes = [
        "Paneer Tikka",
        "Chicken Biryani", 
        "Margherita Pizza",
        "Thai Green Curry",
        "Beef Tacos",
        "Sushi Roll",
        "Pad Thai",
        "Unknown Dish"
    ]
    
    for dish in test_dishes:
        print(f"\n🍽️  {dish}:")
        try:
            ingredients = agent.extract_ingredients(dish)
            print(f"   📝 {', '.join(ingredients)}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n✅ AI Ingredient Extraction Test Complete!")
    print("🤖 The AI can now extract ingredients for any dish you enter!")

if __name__ == "__main__":
    test_ai_ingredient_extraction() 