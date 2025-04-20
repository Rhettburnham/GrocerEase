import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DishGenerator:
    def __init__(self, api_key=None):
        """
        Initialize the dish generator with the OpenAI API.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, tries to get from environment.
        """
        # Get API key from args or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass to constructor.")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Get model from environment or use default
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4")
    
    def generate_dish_ideas(self, ingredients, meal_type='any'):
        """
        Generate dish ideas based on available ingredients and meal type.
        
        Args:
            ingredients (list): List of available ingredients with their weights
            meal_type (str): Type of meal (breakfast, lunch, dinner, or any)
            
        Returns:
            list: Generated dish ideas
        """
        # Format the ingredients list for the prompt
        ingredient_text = '\n'.join([f"- {ing['food_type']}: {ing['weight_grams']}g" for ing in ingredients])
        
        # Create the prompt
        prompt = f"""Generate 3 dish ideas for {meal_type} using some or all of these ingredients:

{ingredient_text}

For each dish, suggest a name, a brief description, and which of the available ingredients are needed with their amounts in grams.
Return the result as a JSON array of objects with the following structure:
[{{
  "name": "Dish Name",
  "description": "Brief description",
  "ingredients": ["Ingredient1", "Ingredient2", ...],
  "requiredAmounts": {{"Ingredient1": amount_in_grams, "Ingredient2": amount_in_grams, ...}}
}}]
"""
        
        # Call the OpenAI API using the client
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a culinary expert specialized in creating dishes from available ingredients."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract the result text
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Clean up potential non-JSON content around the JSON array
                json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                if json_match:
                    # Fix common JSON formatting issues
                    json_str = json_match.group(0)
                    # Replace instances where g is directly after a number without quotes
                    json_str = re.sub(r'(\d+)g', r'\1"g"', json_str)
                    try:
                        dish_ideas = json.loads(json_str)
                    except json.JSONDecodeError:
                        # Try a more aggressive approach - replace all occurrences of "g" at the end of numbers
                        json_str = re.sub(r'(\d+)g([,}])', r'\1\2', json_str)
                        dish_ideas = json.loads(json_str)
                else:
                    # Try parsing the entire response as JSON
                    try:
                        dish_ideas = json.loads(result_text)
                    except:
                        # Fall back to a manual parsing approach
                        print("Attempting manual parsing of JSON structure")
                        # Look for dish objects with expected fields
                        dishes = []
                        dish_matches = re.finditer(r'\{\s*"name":\s*"([^"]+)".*?"requiredAmounts":\s*\{([^}]+)\}', 
                                                  result_text, re.DOTALL)
                        
                        for match in dish_matches:
                            try:
                                # Extract the full dish object text and fix common issues
                                dish_text = match.group(0)
                                # Clean up the text to make it valid JSON
                                dish_text = re.sub(r'(\d+)g([,}])', r'\1\2', dish_text)
                                # Try to parse this single dish
                                dish = json.loads(dish_text + '}')  # Add closing brace
                                dishes.append(dish)
                            except:
                                continue
                        
                        if dishes:
                            return dishes
                            
                        raise ValueError("Could not extract JSON array from response")
                
                return dish_ideas
            except json.JSONDecodeError as je:
                print(f"Error decoding JSON from response: {result_text}")
                print(f"JSON error: {je}")
                return []
                
        except Exception as e:
            print(f"Error generating dish ideas: {e}")
            return []

def get_dish_ideas(ingredients, meal_type='any'):
    """
    Helper function to get dish ideas for a specific meal type
    
    Args:
        ingredients (list): List of available ingredients with their weights
        meal_type (str): Type of meal (breakfast, lunch, dinner, or any)
        
    Returns:
        list: Generated dish ideas
    """
    try:
        generator = DishGenerator()
        return generator.generate_dish_ideas(ingredients, meal_type)
    except Exception as e:
        print(f"Error in dish generation: {e}")
        return []

def load_ingredients_from_food_log():
    """
    Load ingredients from the food_log.json file
    
    Returns:
        list: List of ingredients with their weights
    """
    try:
        # Find the data directory relative to the current file
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(current_dir, 'data', 'food_log.json')
        
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Food log file not found at {data_path}")
            return []
    except Exception as e:
        print(f"Error loading food log: {e}")
        return []

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate dish ideas from available ingredients')
    parser.add_argument('--meal-type', default='any', choices=['breakfast', 'lunch', 'dinner', 'any'], help='Type of meal')
    parser.add_argument('--output', help='Path to output JSON file')
    
    args = parser.parse_args()
    
    # Load ingredients from food log
    ingredients = load_ingredients_from_food_log()
    
    if not ingredients:
        print("No ingredients found in food log. Please add some ingredients first.")
        exit(1)
    
    print(f"Loaded {len(ingredients)} ingredients from food log")
    
    # Generate dish ideas
    dishes = get_dish_ideas(ingredients, args.meal_type)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(dishes, f, indent=2)
    else:
        print(json.dumps(dishes, indent=2)) 