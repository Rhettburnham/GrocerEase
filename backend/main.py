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
# Removed import for RecipeGenerator
# We might import the suggestor if needed directly here, but for now API handles it
from storage.log import FoodLog
from server.api import FoodLogAPI # Corrected class name potentially

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
        
        # Removed initialization of recipe_generator
        # Initialize the API server
        # The API server now handles recipe generation logic internally
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'frontend', 'dist')
        # Check if api.py defines FoodLogAPI or just the app instance
        # Assuming FoodLogAPI is a class wrapper, otherwise adjust
        self.api = FoodLogAPI(static_folder=frontend_dir if os.path.exists(frontend_dir) else None)
        # If api.py just has `app`, we might need to import `app` and run it differently.
        # Let's assume FoodLogAPI class exists for now.
        
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
        
        # Run processing in a separate thread to keep button responsive
        process_thread = threading.Thread(target=self._process_food_sample)
        process_thread.start()
    
    def _process_food_sample(self):
        """Process a food sample by weighing, capturing, and identifying"""
        # Set the processing flag to prevent multiple concurrent processes
        self.processing = True
        
        try:
            print("\n--- Processing new food sample ---")
            
            # 1. Get the weight
            print("Reading weight...")
            weight = self.scale.get_weight()
            if weight is None:
                print("Error: Failed to read weight.")
                self.processing = False
                return
            print(f"Weight: {weight}g")
            
            # 2. Capture an image
            print("Capturing image...")
            image_path = self.camera.capture()
            if not image_path:
                print("Error: Failed to capture image!")
                self.processing = False
                return
            
            print(f"Image saved: {image_path}")
            
            # 3. Identify the food
            print("Identifying food type...")
            result = self.vision.identify_food(image_path)
            
            food_type = result.get("food_type", "unknown")
            confidence = result.get("confidence", 0.0)
            timestamp = datetime.now().isoformat() # Add timestamp
            
            print(f"Identified as: {food_type} (confidence: {confidence:.2f})")
            
            # 4. Log the data
            # Use relative path for storage, consistent with API serving
            relative_image_path = os.path.relpath(
                image_path, 
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            )
            # Prepend 'images/' to match the API route structure
            api_image_path = os.path.join('images', os.path.basename(relative_image_path)).replace('\\', '/')

            # Ensure weight is stored as number
            try:
                weight_grams = float(weight)
            except (ValueError, TypeError):
                print(f"Warning: Invalid weight value '{weight}', storing as 0.")
                weight_grams = 0.0
            
            entry_data = {
                "timestamp": timestamp,
                "food_type": food_type,
                "weight_grams": weight_grams, # Ensure key matches expected format
                "image_path": api_image_path, # Store path accessible by API
                "confidence": confidence
            }
            
            self.log.add_entry(entry_data) # Pass dict to add_entry
            
            print("Entry added to log")
            
            # Removed the call to _test_recipe_generation
            
        except Exception as e:
            # Log the exception traceback for better debugging
            import traceback
            print(f"Error processing food sample: {e}")
            traceback.print_exc()
        finally:
            # Ensure processing flag is always reset
            self.processing = False
            print("--- Finished processing sample ---")
    
    # Removed _test_recipe_generation method
    
    def start(self):
        """Start the FoodBot"""
        if self.running:
            return
        
        self.running = True
        print("Starting FoodBot...")
        
        # Initialize Scale here to ensure it's ready
        try:
            self.scale.setup()
        except Exception as e:
            print(f"Warning: Scale setup failed: {e}. Weight reading might not work.")
            
        # Start the button listener
        try:
            self.button.start()
            print("Button listener started (GPIO pin {})".format(self.button.pin))
        except Exception as e:
            print(f"Error starting button listener: {e}")
            # Decide if this is critical - perhaps proceed without button?
            # For now, let's stop if the button fails.
            self.running = False 
            return
        
        # Start the API server in a separate thread
        self.api_thread = threading.Thread(target=self._run_api_server, name="APIServerThread")
        self.api_thread.daemon = True # Allows main program to exit even if thread is running
        self.api_thread.start()
        
        # Wait briefly for server to start
        time.sleep(1)
        print(f"API server thread started. Check logs for http://0.0.0.0:5000/ status.")
        
        print("\nFoodBot ready! Press the button to weigh and identify food.")
        
        # Keep the main thread alive and wait for shutdown signal
        try:
            while not self._shutdown:
                time.sleep(0.5) # Reduced sleep time for faster shutdown response
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected.")
            self._shutdown = True
        finally:
            print("Initiating shutdown process from main loop...")
            self.stop()
    
    def _run_api_server(self):
        """Run the API server.
        Note: Flask's development server might not be ideal for production.
        Consider using a production-ready WSGI server like Gunicorn or Waitress.
        """
        try:
            print("Starting Flask development server...")
            # Import the app instance from api.py
            from server.api import app 
            port = int(os.environ.get('PORT', 5000))
            # Use waitress or another production server if not in debug mode
            if not self.debug:
                try:
                    from waitress import serve
                    print(f"Starting Waitress server on port {port}...")
                    serve(app, host='0.0.0.0', port=port)
                except ImportError:
                    print("Waitress not found. Falling back to Flask development server.")
                    print("Install waitress for a production-ready server: pip install waitress")
                    app.run(host='0.0.0.0', port=port, debug=False)
            else:
                print(f"Starting Flask development server (DEBUG MODE) on port {port}...")
                # debug=True enables auto-reloading, which can be problematic with threads/hardware
                # Use use_reloader=False for more stability during development with hardware
                app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
        except Exception as e:
            print(f"Error running API server: {e}")
            # Optionally trigger shutdown if API fails critically
            # self._shutdown = True 
    
    def stop(self):
        """Stop the FoodBot and cleanup resources"""
        if not self.running and not self._shutdown: # Check if already stopped or stopping
             # Allow stop to be called even if start failed partially
             pass 
        elif not self.running:
             return # Already stopped

        print("Stopping FoodBot components...")
        self._shutdown = True # Ensure shutdown flag is set
        
        # Stop the button listener
        if hasattr(self, 'button') and self.button:
             try:
                 self.button.stop()
                 print("Button listener stopped.")
             except Exception as e:
                 print(f"Error stopping button listener: {e}")
        
        # No explicit stop needed for the API thread if it's daemonized or server handles SIGTERM
        # However, attempting a clean shutdown of the server is good practice if possible.
        # This is complex with Flask dev server/Waitress running in a thread.
        # Relying on SIGINT/SIGTERM for now.

        # Cleanup hardware resources
        if hasattr(self, 'scale') and self.scale:
            try:
                self.scale.cleanup()
                print("Scale cleaned up.")
            except Exception as e:
                print(f"Error cleaning up scale: {e}")
        if hasattr(self, 'button') and self.button: # Check again in case stop failed
             try:
                 self.button.cleanup()
                 print("Button cleaned up.")
             except Exception as e:
                 print(f"Error cleaning up button: {e}")
        
        self.running = False
        print("FoodBot stopped")

def main():
    """Main entry point for the application"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FoodBot - Food Weighing and Identification Robot')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (uses Flask dev server)')
    parser.add_argument('--button-pin', type=int, default=17, help='GPIO pin for the button (BCM numbering)')
    # Removed --test-recipes argument
    args = parser.parse_args()
    
    foodbot = None # Initialize foodbot variable
    try:
        # Create the FoodBot
        foodbot = FoodBot(button_pin=args.button_pin, debug=args.debug)
        # Start the main loop
        foodbot.start()
    except Exception as e:
        print(f"Critical error during initialization or startup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure stop is called even if start fails
        if foodbot is not None:
            print("Ensuring FoodBot is stopped in finally block...")
            foodbot.stop()
        else:
            print("FoodBot instance was not created. Exiting.")

if __name__ == "__main__":
    main() 