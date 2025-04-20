import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add the parent directory to the path to import from adjacent directories
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import recipe-related functions (without hardware dependencies)
from ai.dish_generator import get_dish_ideas, load_ingredients_from_food_log
from ai.recipe_generator import get_full_recipe

# Create Flask app
app = Flask(__name__)

# Allow CORS for local development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# API Routes for Recipe Suggestions
@app.route('/api/recipe-ideas', methods=['GET'])
def recipe_ideas():
    try:
        meal_type = request.args.get('meal_type', 'any')
        print(f"Generating recipe ideas for {meal_type}")
        
        # Load ingredients from food log
        ingredients = load_ingredients_from_food_log()
        
        if not ingredients:
            return jsonify({"error": "No ingredients found in food log"}), 400
        
        # Generate dish ideas
        dishes = get_dish_ideas(ingredients, meal_type)
        
        return jsonify(dishes)
    except Exception as e:
        print(f"Error generating recipe ideas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recipe', methods=['POST'])
def generate_recipe():
    try:
        data = request.json
        recipe_name = data.get('recipe_name')
        ingredients = data.get('ingredients', {})
        
        if not recipe_name:
            return jsonify({"error": "Recipe name is required"}), 400
        
        # Generate full recipe
        recipe = get_full_recipe(recipe_name, ingredients)
        
        return jsonify(recipe)
    except Exception as e:
        print(f"Error generating recipe: {e}")
        return jsonify({"error": str(e)}), 500

# API Routes for Food Log
@app.route('/api/log', methods=['GET'])
def get_log():
    try:
        # Read from food_log.json
        data_dir = os.path.join(parent_dir, '..', 'data')
        log_path = os.path.join(data_dir, 'food_log.json')
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                food_log = json.load(f)
            return jsonify(food_log)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error reading food log: {e}")
        return jsonify({"error": str(e)}), 500

# Serve static images
@app.route('/api/images/<path:filename>')
def get_image(filename):
    data_dir = os.path.join(parent_dir, '..', 'data', 'images')
    return send_from_directory(data_dir, filename)

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 