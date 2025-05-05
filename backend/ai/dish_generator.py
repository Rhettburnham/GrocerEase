import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Hardcoded API key for prototype
API_KEY = "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"

class RecipeSuggestor:
    def __init__(self, api_key=None):
        """
        Initialize the recipe suggestor with the OpenAI API.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, tries to get from environment.
        """
        # Hardcoded API key for prototype
        self.api_key = API_KEY
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Get model from environment or use default
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4")
    
    def generate_recipe_suggestions(self, ingredients, meal_type='any', num_suggestions=3):
        """
        Generate full recipe suggestions based on available ingredients and meal type.
        
        Args:
            ingredients (list): List of available ingredients with their weights (dict like {'food_type': 'apple', 'weight_grams': 150})
            meal_type (str): Type of meal (breakfast, lunch, dinner, or any)
            num_suggestions (int): Number of recipe suggestions to generate
            
        Returns:
            list: Generated full recipe suggestions (list of dicts)
        """
        # Format the ingredients list for the prompt
        ingredient_text = '\\n'.join([f"- {ing['food_type']}: {ing['weight_grams']}g" for ing in ingredients])
        
        # Create the prompt - Updated to ask for full recipes
        prompt = f"""Generate {num_suggestions} full recipe ideas suitable for {meal_type} using mainly these ingredients:

Available Ingredients:
{ingredient_text}

For each recipe, provide the following details:
- Name
- Introduction/Description
- Preparation time (e.g., "15 minutes")
- Cooking time (e.g., "30 minutes")
- Servings (e.g., "2")
- Ingredients list (including amounts needed - try to use available ingredients but mention if others are needed)
- Step-by-step instructions
- Estimated nutritional information (optional, if possible)
- Tips or variations (optional)

Return the result ONLY as a JSON array of objects, where each object represents a full recipe with the following structure:
[{{
  "name": "Recipe Name",
  "introduction": "Brief description of the dish",
  "prepTime": "XX minutes",
  "cookTime": "XX minutes",
  "servings": "X",
  "ingredients": ["Ingredient 1 with measurement", "Ingredient 2 with measurement", ...],
  "instructions": ["Step 1", "Step 2", ...],
  "nutritionalInfo": "Optional: Calories, protein, etc.",
  "tips": "Optional: Additional tips"
}}]

Ensure the output is ONLY the JSON array, nothing before or after. Use the available ingredients where possible.
"""
        
        # Call the OpenAI API using the client
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative chef specialized in generating detailed recipes based on available ingredients."}, # Updated system message
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8, # Slightly higher temp for more creative recipes
                max_tokens=2000 # Increased tokens for potentially longer full recipes
            )
            
            # Extract the result text
            result_text = response.choices[0].message.content
            
            # Try to extract JSON array from the response
            try:
                # Clean up potential markdown/text around the JSON array
                json_match = re.search(r'\[\s*\{.*\}\s*\]', result_text, re.DOTALL) # Look for array structure
                if json_match:
                    json_str = json_match.group(0)
                    recipe_suggestions = json.loads(json_str)
                else:
                    # Try parsing the entire response if it seems to be just the array
                    recipe_suggestions = json.loads(result_text)
                
                return recipe_suggestions
            except json.JSONDecodeError as je:
                print(f"Error decoding JSON from response: {result_text}")
                print(f"JSON error: {je}")
                # Attempt to find JSON objects within the text if array parsing failed
                try:
                    recipes = []
                    # Look for individual recipe objects
                    object_matches = re.finditer(r'\{\s*"name":.*?\}', result_text, re.DOTALL)
                    for match in object_matches:
                        try:
                            recipes.append(json.loads(match.group(0)))
                        except json.JSONDecodeError:
                            continue # Skip malformed objects
                    if recipes:
                        print("Warning: Parsed individual recipe objects, full array might be malformed.")
                        return recipes
                    else:
                        return [{"error": "Failed to parse recipe suggestions", "raw_response": result_text}]
                except Exception as inner_e:
                     print(f"Error during fallback parsing: {inner_e}")
                     return [{"error": "Failed to parse recipe suggestions", "raw_response": result_text}]

        except Exception as e:
            print(f"Error generating recipe suggestions: {e}")
            return [{"error": str(e)}]

def get_recipe_suggestions(ingredients, meal_type='any', num_suggestions=3):
    """
    Helper function to get full recipe suggestions
    
    Args:
        ingredients (list): List of available ingredients with their weights
        meal_type (str): Type of meal (breakfast, lunch, dinner, or any)
        num_suggestions (int): Number of suggestions to generate
        
    Returns:
        list: Generated recipe suggestions
    """
    try:
        generator = RecipeSuggestor()
        return generator.generate_recipe_suggestions(ingredients, meal_type, num_suggestions)
    except Exception as e:
        print(f"Error in recipe suggestion generation: {e}")
        return [{"error": str(e)}]

def load_ingredients_from_food_log():
    """
    Load ingredients from the food_log.json file
    
    Returns:
        list: List of ingredients with their weights
    """
    try:
        # Find the data directory relative to the current file's parent directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Corrected path finding
        data_path = os.path.join(current_dir, 'data', 'food_log.json')
        
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                log_data = json.load(f)
                # Ensure structure matches expected input format
                # The generator expects [{'food_type': 'apple', 'weight_grams': 150}, ...]
                # Let's assume food_log.json contains this structure directly
                if isinstance(log_data, list) and all(isinstance(item, dict) and 'food_type' in item and 'weight_grams' in item for item in log_data):
                     return log_data
                else:
                     print(f"Warning: food_log.json at {data_path} has unexpected format. Expected list of dicts with 'food_type' and 'weight_grams'.")
                     # Attempt conversion if possible, otherwise return empty
                     # This part might need adjustment based on actual food_log.json structure
                     return []
        else:
            print(f"Food log file not found at {data_path}")
            return []
    except Exception as e:
        print(f"Error loading food log: {e}")
        return []

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate full recipe suggestions from available ingredients')
    parser.add_argument('--meal-type', default='any', choices=['breakfast', 'lunch', 'dinner', 'any'], help='Type of meal')
    parser.add_argument('--num-suggestions', type=int, default=3, help='Number of recipes to suggest')
    parser.add_argument('--output', help='Path to output JSON file')
    
    args = parser.parse_args()
    
    # Load ingredients from food log
    ingredients = load_ingredients_from_food_log()
    
    if not ingredients:
        print("No ingredients found in food log or log format is incorrect. Please check data/food_log.json.")
        exit(1)
    
    print(f"Loaded {len(ingredients)} ingredient types from food log for suggestions.")
    
    # Generate recipe suggestions
    recipes = get_recipe_suggestions(ingredients, args.meal_type, args.num_suggestions)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(recipes, f, indent=2)
        print(f"Saved {len(recipes)} recipe suggestions to {args.output}")
    else:
        print(json.dumps(recipes, indent=2)) 