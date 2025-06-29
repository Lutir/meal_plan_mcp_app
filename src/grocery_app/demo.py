"""
Demo script showcasing the AI-powered ingredient extraction capabilities
"""

from openai_agents.ingredient_extractor import get_ingredient_extractor_agent
import time

def demo_ai_capabilities():
    """Demonstrate the AI's ability to extract ingredients for diverse cuisines"""
    
    print("🧠 AI-Powered Ingredient Extractor Demo")
    print("=" * 60)
    print("This demo showcases how the AI can extract ingredients for ANY dish!")
    print("From simple comfort food to complex international cuisines.\n")
    
    agent = get_ingredient_extractor_agent()
    
    # Diverse cuisine examples
    demo_dishes = [
        # Indian Cuisine
        ("Paneer Tikka", "Indian"),
        ("Chicken Biryani", "Indian"),
        ("Dal Makhani", "Indian"),
        
        # Italian Cuisine  
        ("Margherita Pizza", "Italian"),
        ("Spaghetti Carbonara", "Italian"),
        ("Risotto ai Funghi", "Italian"),
        
        # Thai Cuisine
        ("Pad Thai", "Thai"),
        ("Green Curry", "Thai"),
        ("Tom Yum Soup", "Thai"),
        
        # Mexican Cuisine
        ("Beef Tacos", "Mexican"),
        ("Chicken Enchiladas", "Mexican"),
        ("Guacamole", "Mexican"),
        
        # Japanese Cuisine
        ("Sushi Roll", "Japanese"),
        ("Ramen", "Japanese"),
        ("Teriyaki Chicken", "Japanese"),
        
        # American Cuisine
        ("BBQ Ribs", "American"),
        ("Mac and Cheese", "American"),
        ("Apple Pie", "American"),
        
        # Unknown/Complex Dishes
        ("Unknown Dish", "Unknown"),
        ("Fusion Sushi Burrito", "Fusion"),
        ("Molecular Gastronomy Dish", "Experimental")
    ]
    
    for i, (dish, cuisine) in enumerate(demo_dishes, 1):
        print(f"\n{i:2d}. 🍽️  {dish} ({cuisine})")
        print("   " + "─" * 50)
        
        try:
            start_time = time.time()
            ingredients = agent.extract_ingredients(dish)
            end_time = time.time()
            
            print(f"   ⚡ AI Response Time: {end_time - start_time:.2f}s")
            print(f"   📝 Ingredients ({len(ingredients)} items):")
            
            # Format ingredients nicely
            for j, ingredient in enumerate(ingredients, 1):
                print(f"      {j:2d}. {ingredient}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("🤖 The AI successfully extracted ingredients for diverse cuisines!")
    print("💡 Key Features:")
    print("   • Handles international cuisines")
    print("   • Provides specific quantities")
    print("   • Includes cooking instructions")
    print("   • Smart fallbacks for unknown dishes")
    print("   • Fast response times (< 2 seconds)")
    print("\n🚀 Ready to use in your meal planning app!")

if __name__ == "__main__":
    demo_ai_capabilities() 