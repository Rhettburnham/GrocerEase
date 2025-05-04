import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add the parent directory to the path to import from adjacent directories
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import recipe-related functions (without hardware dependencies)
# Use the refactored suggestor and its helper function
from ai.dish_generator import get_recipe_suggestions, load_ingredients_from_food_log
# Removed import from recipe_generator

# Create Flask app
app = Flask(__name__)

# Allow CORS for local development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# API Route for Recipe Suggestions - Renamed and Updated
@app.route('/api/recipes', methods=['GET']) # Renamed route
def recipe_suggestions(): # Renamed function
    try:
        meal_type = request.args.get('meal_type', 'any')
        num_suggestions = request.args.get('num', 3, type=int) # Allow specifying number via query param
        print(f"Generating {num_suggestions} recipe suggestions for {meal_type}")
        
        # Load ingredients from food log
        ingredients = load_ingredients_from_food_log()
        
        if not ingredients:
            return jsonify({"error": "No ingredients found in food log"}), 400
        
        # Generate recipe suggestions using the refactored function
        recipes = get_recipe_suggestions(ingredients, meal_type, num_suggestions)
        
        # Check if the result indicates an error from the generator
        if isinstance(recipes, list) and len(recipes) > 0 and "error" in recipes[0]:
            return jsonify(recipes[0]), 500 # Return the error details
            
        return jsonify(recipes)
    except Exception as e:
        print(f"Error generating recipe suggestions: {e}")
        return jsonify({"error": str(e)}), 500

# Removed the old /api/recipe POST endpoint
# API Routes for Food Log
@app.route('/api/log', methods=['GET'])
def get_log():
    try:
        # Read from food_log.json
        # Construct path relative to this script's parent directory
        log_path = os.path.join(parent_dir, 'data', 'food_log.json')
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                food_log = json.load(f)
            return jsonify(food_log)
        else:
            # Return empty list if log doesn't exist yet
            return jsonify([])
    except Exception as e:
        print(f"Error reading food log: {e}")
        return jsonify({"error": str(e)}), 500

# Serve static images
@app.route('/api/images/<path:filename>')
def get_image(filename):
    # Construct path relative to this script's parent directory
    image_dir = os.path.join(parent_dir, 'data', 'images')
    try:
        return send_from_directory(image_dir, filename)
    except FileNotFoundError:
         return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        return jsonify({"error": "Error serving image"}), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting API server on port {port}")
    # Use host='0.0.0.0' to make it accessible on the network
    app.run(host='0.0.0.0', port=port, debug=True) 