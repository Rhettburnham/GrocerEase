import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RecipeGenerator:
    def __init__(self, api_key=None):
        """
        Initialize the recipe generator with the OpenAI API.
        
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
    
    def generate_full_recipe(self, recipe_name, ingredients):
        """
        Generate a full recipe with instructions based on a recipe name and ingredients.
        
        Args:
            recipe_name (str): Name of the recipe
            ingredients (dict): Dictionary of ingredients with their amounts in grams
            
        Returns:
            dict: Generated recipe with instructions
        """
        # Format the ingredients list for the prompt
        ingredient_text = '\n'.join([f"- {ing}: {amt}g" for ing, amt in ingredients.items()])
        
        # Create the prompt
        prompt = f"""Create a detailed recipe for "{recipe_name}" using these ingredients:

{ingredient_text}

Include the following sections:
1. Introduction: A brief description of the dish
2. Preparation time
3. Cooking time
4. Servings
5. Ingredients (with measurements)
6. Step-by-step instructions
7. Nutritional information (estimate)
8. Tips and variations

Return the result as a JSON object with the following structure:
{{
  "name": "{recipe_name}",
  "introduction": "Brief description of the dish",
  "prepTime": "XX minutes",
  "cookTime": "XX minutes",
  "servings": "X",
  "ingredients": ["Ingredient 1 with measurement", "Ingredient 2 with measurement", ...],
  "instructions": ["Step 1", "Step 2", ...],
  "nutritionalInfo": "Calories, protein, carbs, fat information",
  "tips": "Additional tips and variations"
}}
"""
        
        # Call the OpenAI API using the client
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional chef specialized in creating detailed recipes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract the result text
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Clean up potential non-JSON content around the JSON object
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    recipe = json.loads(json_match.group(0))
                else:
                    # Try parsing the entire response as JSON
                    try:
                        recipe = json.loads(result_text)
                    except:
                        raise ValueError("Could not extract JSON object from response")
                
                # Add the recipe name if it's not already there
                if 'name' not in recipe:
                    recipe['name'] = recipe_name
                
                return recipe
            except json.JSONDecodeError as je:
                print(f"Error decoding JSON from response: {result_text}")
                print(f"JSON error: {je}")
                return {
                    "error": "Failed to generate recipe",
                    "raw_response": result_text
                }
                
        except Exception as e:
            print(f"Error generating full recipe: {e}")
            return {"error": str(e)}

def get_full_recipe(recipe_name, ingredients):
    """
    Helper function to generate a full recipe
    
    Args:
        recipe_name (str): Name of the recipe
        ingredients (dict): Dictionary of ingredients with their amounts in grams
        
    Returns:
        dict: Generated recipe with instructions
    """
    try:
        generator = RecipeGenerator()
        return generator.generate_full_recipe(recipe_name, ingredients)
    except Exception as e:
        print(f"Error generating recipe: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate a full recipe with instructions')
    parser.add_argument('--recipe-name', required=True, help='Name of the recipe to generate')
    parser.add_argument('--ingredients', help='Path to JSON file with ingredients and amounts')
    parser.add_argument('--input-json', help='JSON string with ingredients and amounts')
    parser.add_argument('--output', help='Path to output JSON file')
    
    args = parser.parse_args()
    
    ingredients = {}
    
    # Read ingredients from file or input JSON
    if args.ingredients:
        try:
            with open(args.ingredients, 'r') as f:
                ingredients = json.load(f)
        except Exception as e:
            print(f"Error reading ingredients file: {e}")
            exit(1)
    elif args.input_json:
        try:
            ingredients = json.loads(args.input_json)
        except Exception as e:
            print(f"Error parsing input JSON: {e}")
            exit(1)
    else:
        print("Please provide either --ingredients or --input-json")
        exit(1)
    
    # Generate full recipe
    recipe = get_full_recipe(args.recipe_name, ingredients)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(recipe, f, indent=2)
    else:
        print(json.dumps(recipe, indent=2)) 