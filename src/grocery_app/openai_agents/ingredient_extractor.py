import os
import logging
from typing import List
import asyncio
from agents import Agent, Runner, function_tool  # OpenAI Agents SDK
from grocery_app.config import OPENAI_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set the OpenAI API key
if OPENAI_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY

@function_tool
def get_recipe_ingredients(dish_name: str) -> List[str]:
    """
    Minimal fallback for very common dishes (used as a tool by the agent, not as a fallback in code).
    """
    common_dishes = {
        "paneer tikka": ["paneer", "yogurt", "onion", "bell pepper", "garlic", "ginger"],
        "dal": ["lentils", "onions", "tomatoes", "garlic", "ginger", "oil"],
        "roti": ["wheat flour", "water", "oil"],
    }
    dish_lower = dish_name.lower().strip()
    return common_dishes.get(dish_lower, [])

class AIngredientExtractorAgent:
    """
    AI-powered ingredient extractor using OpenAI Agents SDK.
    Excludes spices, oil, salt, pepper, and pantry staples. Only includes main raw ingredients.
    """
    def __init__(self):
        self.agent = Agent(
            name="AI Ingredient Extractor",
            instructions="""
            You are a culinary expert and ingredient specialist. Your job is to extract the main raw ingredients needed to cook any dish.

            Guidelines:
            1. For any dish name provided, return a comprehensive list of main raw ingredients (vegetables, proteins, grains, dairy, etc).
            2. Do NOT include spices, oil, salt, pepper, or other pantry staples.
            3. Focus on ingredients a home cook would need to buy fresh or as main components.
            4. Exclude common cooking ingredients like oil, salt, pepper, and spices unless they are a main feature of the dish.
            5. Be specific but practical - don't list every possible variation.
            6. Return your response as a Python list of ingredient strings, with quantities where appropriate.
            Example: ["2 eggs", "1 onion", "1 tomato", "200g chicken", "1 cup rice"]
            Only include the main raw ingredients!
            """,
            model="gpt-4o-mini",
            tools=[get_recipe_ingredients]
        )

    def extract_ingredients(self, dish_name: str) -> List[str]:
        logging.info(f"Extracting ingredients for: {dish_name}")
        prompt = f"""
        Please provide the main raw ingredients needed to cook '{dish_name}'.
        Only include vegetables, proteins, grains, dairy, and other main components. Do NOT include spices, oil, salt, pepper, or pantry staples.
        Return a Python list of ingredient strings with quantities where appropriate.
        """
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                result = asyncio.run(Runner.run(self.agent, prompt))
            else:
                result = asyncio.run(Runner.run(self.agent, prompt))
            logging.info(f"AI agent result for '{dish_name}': {result.final_output}")
            import ast
            try:
                response_text = result.final_output.strip()
                if '[' in response_text and ']' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    list_str = response_text[start:end]
                    ingredients = ast.literal_eval(list_str)
                    if isinstance(ingredients, list):
                        return [str(ingredient).strip() for ingredient in ingredients]
                delimiters = [',', ';', '\n', '•', '-']
                for delimiter in delimiters:
                    if delimiter in response_text:
                        ingredients = [item.strip() for item in response_text.split(delimiter) if item.strip()]
                        if len(ingredients) > 1:
                            return ingredients
                return [response_text.strip()]
            except (ValueError, SyntaxError):
                logging.warning(f"Parsing failed for '{dish_name}', returning raw response.")
                return [result.final_output.strip()]
        except Exception as e:
            logging.error(f"AI extraction failed for '{dish_name}': {e}")
            return [f"AI extraction failed for {dish_name}: {e}"]

def get_ingredient_extractor_agent() -> AIngredientExtractorAgent:
    return AIngredientExtractorAgent() 