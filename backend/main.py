import os
import sys
import time
import signal
import threading
from datetime import datetime

# Import our modules
from hardware.button import Button
from hardware.scale import Scale
from hardware.camera import Camera
from ai.vision import FoodVisionIdentifier
from ai.recipe_generator import RecipeGenerator
from storage.log import FoodLog
from server.api import FoodLogAPI

class FoodBot:
    def __init__(self, button_pin=17, debug=False):
        """
        Initialize the FoodBot with all components.
        
        Args:
            button_pin (int): GPIO pin for the button
            debug (bool): Whether to run in debug mode
        """
        self.debug = debug
        self.running = False
        self.processing = False
        self._shutdown = False
        
        # Initialize components
        self.log = FoodLog()
        self.scale = Scale()
        self.camera = Camera()
        self.vision = FoodVisionIdentifier()
        self.button = Button(pin=button_pin, callback=self._on_button_press)
        
        # Initialize the recipe generator (optional)
        try:
            self.recipe_generator = RecipeGenerator()
            print("Recipe generator initialized")
        except ValueError as e:
            print(f"Warning: Recipe generator not initialized: {e}")
            self.recipe_generator = None
        
        # Initialize the API server
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'frontend', 'dist')
        self.api = FoodLogAPI(static_folder=frontend_dir if os.path.exists(frontend_dir) else None)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\nShutting down gracefully...")
        self._shutdown = True
        self.stop()
    
    def _on_button_press(self):
        """
        Handle button press event.
        This triggers the food weighing and identification process.
        """
        if self.processing:
            print("Already processing a sample, please wait.")
            return
        
        self._process_food_sample()
    
    def _process_food_sample(self):
        """Process a food sample by weighing, capturing, and identifying"""
        # Set the processing flag to prevent multiple concurrent processes
        self.processing = True
        
        try:
            print("\n--- Processing new food sample ---")
            
            # 1. Get the weight
            print("Reading weight...")
            weight = self.scale.get_weight()
            print(f"Weight: {weight}g")
            
            # 2. Capture an image
            print("Capturing image...")
            image_path = self.camera.capture()
            if not image_path:
                print("Failed to capture image!")
                self.processing = False
                return
            
            print(f"Image saved: {image_path}")
            
            # 3. Identify the food
            print("Identifying food type...")
            result = self.vision.identify_food(image_path)
            
            food_type = result.get("food_type", "unknown")
            confidence = result.get("confidence", 0.0)
            
            print(f"Identified as: {food_type} (confidence: {confidence:.2f})")
            
            # 4. Log the data
            relative_image_path = os.path.relpath(
                image_path, 
                os.path.join(os.path.dirname(os.path.dirname(__file__)))
            )
            
            self.log.add_entry(
                food_type=food_type,
                weight=weight,
                image_path=relative_image_path,
                confidence=confidence
            )
            
            print("Entry added to log")
            
            # 5. Generate recipe suggestions (optional, for testing purposes)
            if self.recipe_generator and self.debug:
                self._test_recipe_generation()
            
        except Exception as e:
            print(f"Error processing food sample: {e}")
        finally:
            self.processing = False
    
    def _test_recipe_generation(self):
        """Test recipe generation functionality (for debugging)"""
        try:
            print("\n--- Testing Recipe Generation ---")
            
            # Get all ingredients from the log
            ingredients = self.log.get_entries()
            
            if not ingredients:
                print("No ingredients available for recipe generation")
                return
            
            # Generate recipe ideas for breakfast
            print("Generating breakfast recipe ideas...")
            recipes = self.recipe_generator.generate_recipe_ideas(ingredients, "breakfast")
            
            if recipes:
                print(f"Generated {len(recipes)} recipe ideas")
                for i, recipe in enumerate(recipes):
                    print(f"Recipe {i+1}: {recipe.get('name')}")
            else:
                print("No recipes generated")
                
        except Exception as e:
            print(f"Error testing recipe generation: {e}")
    
    def start(self):
        """Start the FoodBot"""
        if self.running:
            return
        
        self.running = True
        print("Starting FoodBot...")
        
        # Start the button listener
        self.button.start()
        print("Button listener started (GPIO pin {})".format(self.button.pin))
        
        # Start the API server in a separate thread
        self.api_thread = threading.Thread(target=self._run_api_server)
        self.api_thread.daemon = True
        self.api_thread.start()
        
        print("\nFoodBot ready! Press the button to weigh and identify food.")
        print("API server running at http://0.0.0.0:5000/")
        
        # Keep the main thread alive
        try:
            while not self._shutdown:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._shutdown = True
            self.stop()
    
    def _run_api_server(self):
        """Run the API server in a separate thread"""
        self.api.run(debug=self.debug)
    
    def stop(self):
        """Stop the FoodBot and cleanup resources"""
        if not self.running:
            return
        
        print("Stopping FoodBot...")
        
        # Stop the button listener
        self.button.stop()
        
        # Cleanup hardware resources
        self.scale.cleanup()
        self.button.cleanup()
        
        self.running = False
        print("FoodBot stopped")

def main():
    """Main entry point for the application"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FoodBot - Food Weighing and Identification Robot')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--button-pin', type=int, default=17, help='GPIO pin for the button (BCM numbering)')
    parser.add_argument('--test-recipes', action='store_true', help='Test recipe generation on startup')
    args = parser.parse_args()
    
    # Create and start the FoodBot
    foodbot = FoodBot(button_pin=args.button_pin, debug=args.debug)
    
    # Test recipe generation if requested
    if args.test_recipes and foodbot.recipe_generator:
        foodbot._test_recipe_generation()
    
    try:
        foodbot.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        foodbot.stop()

if __name__ == "__main__":
    main() 