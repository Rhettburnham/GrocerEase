import os
import sys
import json
import time
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import necessary modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.ai.dish_generator import get_dish_ideas
from backend.ai.recipe_generator import get_full_recipe
from backend.server.api import FoodLogAPI

def load_sample_data():
    """Load sample food log data for demo purposes"""
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'food_log.json')
    
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sample data: {e}")
            return []
    else:
        print(f"Sample data file not found at {data_path}")
        return []

def test_dish_generation(ingredients):
    """Test the dish generation functionality with sample data"""
    print("\n--- Testing Dish Generation ---")
    
    if not ingredients:
        print("No ingredients available for dish generation")
        return
    
    try:
        # Generate dish ideas for each meal type
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            print(f"\nGenerating {meal_type} dish ideas...")
            dishes = get_dish_ideas(ingredients, meal_type)
            
            if dishes:
                print(f"Generated {len(dishes)} dish ideas for {meal_type}:")
                for i, dish in enumerate(dishes):
                    print(f"Dish {i+1}: {dish.get('name')}")
                    print(f"  Description: {dish.get('description')}")
                    print(f"  Ingredients: {', '.join(dish.get('ingredients', []))}")
                    print("  Required amounts:")
                    for ing, amount in dish.get('requiredAmounts', {}).items():
                        print(f"    - {ing}: {amount}g")
                    print()
                
                # Test full recipe generation for the first dish
                if dishes and args.full_recipe:
                    dish = dishes[0]
                    print(f"\nGenerating full recipe for: {dish.get('name')}")
                    
                    full_recipe = get_full_recipe(
                        dish.get('name'),
                        dish.get('requiredAmounts', {})
                    )
                    
                    print("Full recipe generated:")
                    print(json.dumps(full_recipe, indent=2))
            else:
                print("No dishes generated")
    except Exception as e:
        print(f"Error in dish generation: {e}")

def run_api_server():
    """Run the API server for demo purposes"""
    print("\n--- Starting API Server with OpenAI Integration ---")
    
    # Get the frontend build directory
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'frontend', 'dist')
    
    # Initialize and run the API server
    api = FoodLogAPI(static_folder=frontend_dir if os.path.exists(frontend_dir) else None)
    api.run(debug=True, port=int(os.environ.get('PORT', 5000)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FoodBot Demo')
    parser.add_argument('--test-dishes', action='store_true', help='Test dish generation with sample data')
    parser.add_argument('--run-server', action='store_true', help='Run the API server with OpenAI integration')
    parser.add_argument('--full-recipe', action='store_true', help='Generate a full recipe for the first suggestion')
    args = parser.parse_args()
    
    # Load sample data
    print("Loading sample data...")
    ingredients = load_sample_data()
    print(f"Loaded {len(ingredients)} ingredients")
    
    # Test dish generation if requested
    if args.test_dishes:
        test_dish_generation(ingredients)
    
    # Run API server if requested
    if args.run_server:
        run_api_server()
    
    # If no arguments provided, just show help
    if not (args.test_dishes or args.run_server):
        parser.print_help() 