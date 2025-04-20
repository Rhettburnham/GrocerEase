import os
import json
from dotenv import load_dotenv
from ai.dish_generator import get_dish_ideas, load_ingredients_from_food_log
from ai.recipe_generator import get_full_recipe

# Load environment variables
load_dotenv()

def test_dish_generator():
    print("=== Testing Dish Generator ===")
    
    # Load ingredients from food log
    print("Loading ingredients from food log...")
    ingredients = load_ingredients_from_food_log()
    
    if not ingredients:
        print("Error: No ingredients found in food log")
        return False
    
    print(f"Found {len(ingredients)} ingredients:")
    for item in ingredients:
        print(f"- {item['food_type']}: {item['weight_grams']}g")
    
    # Generate dish ideas for each meal type
    meal_types = ['breakfast', 'lunch', 'dinner']
    
    for meal_type in meal_types:
        print(f"\nGenerating {meal_type} dish ideas...")
        try:
            dishes = get_dish_ideas(ingredients, meal_type)
            
            if not dishes:
                print(f"No dish ideas generated for {meal_type}")
                continue
                
            print(f"Generated {len(dishes)} dish ideas for {meal_type}:")
            for i, dish in enumerate(dishes, 1):
                print(f"\nDish {i}: {dish['name']}")
                print(f"Description: {dish['description']}")
                print("Ingredients:")
                for ing in dish['ingredients']:
                    print(f"- {ing}: {dish['requiredAmounts'].get(ing, 'unknown')}g")
            
            # Save sample dish for recipe testing
            if meal_type == 'dinner':
                sample_dish = dishes[0]
                
        except Exception as e:
            print(f"Error generating dish ideas for {meal_type}: {e}")
            return False
    
    return True, sample_dish if 'sample_dish' in locals() else None

def test_recipe_generator(dish=None):
    print("\n=== Testing Recipe Generator ===")
    
    if not dish:
        print("No sample dish available, using test data")
        recipe_name = "Test Pasta Recipe"
        ingredients = {
            "Pasta": 100,
            "Tomato": 200,
            "Chicken": 150
        }
    else:
        recipe_name = dish['name']
        ingredients = dish['requiredAmounts']
    
    print(f"Generating full recipe for: {recipe_name}")
    print("With ingredients:")
    for ing, amount in ingredients.items():
        print(f"- {ing}: {amount}g")
    
    try:
        recipe = get_full_recipe(recipe_name, ingredients)
        
        if "error" in recipe:
            print(f"Error generating recipe: {recipe['error']}")
            return False
            
        print("\nGenerated Recipe:")
        print(f"Name: {recipe['name']}")
        
        if 'introduction' in recipe:
            print(f"\nIntroduction: {recipe['introduction']}")
            
        if 'prepTime' in recipe:
            print(f"Prep Time: {recipe['prepTime']}")
            
        if 'cookTime' in recipe:
            print(f"Cook Time: {recipe['cookTime']}")
            
        if 'servings' in recipe:
            print(f"Servings: {recipe['servings']}")
            
        if 'ingredients' in recipe and recipe['ingredients']:
            print("\nIngredients:")
            for ing in recipe['ingredients']:
                print(f"- {ing}")
            
        if 'instructions' in recipe and recipe['instructions']:
            print("\nInstructions:")
            for i, step in enumerate(recipe['instructions'], 1):
                print(f"{i}. {step}")
            
        if 'nutritionalInfo' in recipe:
            print(f"\nNutritional Info: {recipe['nutritionalInfo']}")
            
        if 'tips' in recipe:
            print(f"\nTips: {recipe['tips']}")
            
        # Save the recipe to a file for review
        with open('test_recipe_output.json', 'w') as f:
            json.dump(recipe, f, indent=2)
        print("\nRecipe saved to test_recipe_output.json")
            
        return True
            
    except Exception as e:
        print(f"Error generating recipe: {e}")
        return False

if __name__ == "__main__":
    print("Testing FoodBot AI Generators")
    print("Make sure you have set the OPENAI_API_KEY in your .env file")
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it in your terminal")
        exit(1)
    
    # Test dish generator
    dish_result = test_dish_generator()
    
    if isinstance(dish_result, tuple):
        dish_success, sample_dish = dish_result
    else:
        dish_success, sample_dish = dish_result, None
    
    # Test recipe generator
    recipe_success = test_recipe_generator(sample_dish)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Dish Generator: {'SUCCESS' if dish_success else 'FAILED'}")
    print(f"Recipe Generator: {'SUCCESS' if recipe_success else 'FAILED'}") 