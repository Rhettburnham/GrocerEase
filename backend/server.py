import os
import sys
import json
import socket
import subprocess
import time
import platform
import threading
import signal
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Function to kill processes using a specific port
def kill_process_on_port(port):
    try:
        # Get the PID of process using the port
        if platform.system() == 'Darwin':  # macOS
            cmd = f"lsof -ti tcp:{port}"
        else:  # Linux/Windows
            cmd = f"lsof -ti :{port}"
            
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"Killing process {pid} using port {port}")
                    # Kill the process
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process already gone
            print(f"Killed processes using port {port}")
            # Give OS time to release the port
            time.sleep(1)
            return True
        else:
            print(f"No process found using port {port}")
            return True
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")
        return False

# Global variable to track if capture process is running
capture_process = None
capture_running = False

# Function to run the capture process
def run_capture_process(num_items=7):
    global capture_running
    
    capture_running = True
    
    # Clear or initialize the item_log.json file
    item_log_path = os.path.join(base_dir, 'item_log.json')
    with open(item_log_path, 'w') as f:
        json.dump([], f)
    
    try:
        # Determine which script to run based on platform
        if platform.system() == 'Darwin':
            # On Mac, use the demo script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_demo.py')
        else:
            # On Raspberry Pi, use the real script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        
        # Run the script and capture output
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        # Simulate pressing 'y' num_items times
        for _ in range(num_items):
            process.stdin.write('y\n')
            process.stdin.flush()
            # Wait a bit between captures
            time.sleep(3)
        
        # Send 'q' to quit
        process.stdin.write('q\n')
        process.stdin.flush()
        
        # Wait for process to finish
        process.wait()
        
    except Exception as e:
        print(f"Error running capture process: {e}")
    finally:
        capture_running = False

# Create Flask app
app = Flask(__name__)

# Allow CORS for local development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Get the base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API Routes for Food Log
@app.route('/api/log', methods=['GET'])
@app.route('/api/item-log', methods=['GET'])  # Add alternative endpoint name
def get_item_log():
    try:
        # Path to item_log.json (in the same directory as main.py)
        log_path = os.path.join(base_dir, 'item_log.json')
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                item_log = json.load(f)
            return jsonify(item_log)
        else:
            # Return empty list if log doesn't exist yet
            return jsonify([])
    except Exception as e:
        print(f"Error reading item log: {e}")
        return jsonify({"error": str(e)}), 500

# API Route to start food capture process
@app.route('/api/start-capture', methods=['POST'])
def start_capture():
    global capture_process, capture_running
    
    # Check if capture is already running
    if capture_running:
        return jsonify({"error": "Capture process already running"}), 400
        
    # Start capture process in a new thread
    capture_thread = threading.Thread(
        target=run_capture_process,
        kwargs={"num_items": 7}
    )
    capture_thread.daemon = True
    capture_thread.start()
    
    return jsonify({"status": "started", "message": "Food capture process started"})

# API Route to check capture status
@app.route('/api/capture-status', methods=['GET'])
def check_capture_status():
    global capture_running
    
    # Return current status
    return jsonify({
        "running": capture_running
    })

# Serve static images
@app.route('/api/images/<path:filename>')
def get_image(filename):
    try:
        # Look for images in the images directory at the project root
        image_dir = os.path.join(base_dir, 'images')
        return send_from_directory(image_dir, filename)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        return jsonify({"error": "Error serving image"}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"}), 200

# Simple placeholder for recipes API
@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    try:
        # Hardcoded API key for prototype
        os.environ["OPENAI_API_KEY"] = "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"
        # Import the recipe generator
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai'))
        from dish_generator import load_ingredients_from_food_log, get_recipe_suggestions
        
        # Get meal type from request query parameters (default to 'any')
        meal_type = request.args.get('meal_type', 'any')
        # Get number of suggestions from request (default to 3)
        num_suggestions = int(request.args.get('num_suggestions', 3))
        
        # Log the request for debugging
        print(f"Recipe request: meal_type={meal_type}, num_suggestions={num_suggestions}")
        
        # Load ingredients from food_log.json
        log_path = os.path.join(base_dir, 'item_log.json')
        
        if os.path.exists(log_path):
            # Load the food log data
            with open(log_path, 'r') as f:
                food_log = json.load(f)
            
            # Convert to the format expected by dish_generator
            # dish_generator expects: [{'food_type': 'apple', 'weight_grams': 150}, ...]
            ingredients = []
            for item in food_log:
                ingredients.append({
                    'food_type': item.get('item', ''),
                    'weight_grams': item.get('weight', 0)
                })
            
            # If we have ingredients, generate recipes
            if ingredients:
                print(f"Generating recipes with {len(ingredients)} ingredients for meal type: {meal_type}")
                recipes = get_recipe_suggestions(ingredients, meal_type, num_suggestions)
                print(f"Generated {len(recipes)} recipes")
                return jsonify(recipes)
        
        # If food log doesn't exist or is empty, return placeholders
        placeholder_recipes = [
            {
                "name": "Simple Fruit Salad",
                "introduction": "A refreshing fruit salad made with items from your food log.",
                "ingredients": ["Apple", "Banana", "Orange"],
                "instructions": ["Wash all fruits", "Cut into bite-sized pieces", "Mix in a bowl and serve"]
            }
        ]
        return jsonify(placeholder_recipes)
        
    except Exception as e:
        print(f"Error generating recipes: {e}")
        return jsonify([{"error": str(e)}]), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8000))
    
    # Try to kill any process using our target port
    kill_process_on_port(port)
    
    print(f"Starting API server on port {port}")
    print(f"Serving item log from: {os.path.join(base_dir, 'item_log.json')}")
    
    try:
        # Make the server accessible on the network but NOT in debug mode
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} still in use. Please try a different port.")
            sys.exit(1)
        raise 