import os
import time
import json
import base64
import random
from mimetypes import guess_type
import requests

# --- Capture Image (Demo Version) ---
def capture_image(filename="capture.jpg"):
    # In demo mode, download a random food image
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    file_path = os.path.join(images_dir, os.path.basename(filename))
    
    # Get a food type for the image
    food_items = [
        "apple", "banana", "orange", "mango", "strawberries",
        "broccoli", "carrots", "chicken", "salmon", 
        "rice", "pasta", "sweet+potato", "avocado"
    ]
    food_type = random.choice(food_items)
    
    try:
        # Try to download a food image
        response = requests.get(f"https://source.unsplash.com/100x100/?{food_type},food", 
                               stream=True, timeout=5)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Demo mode: Downloaded food image to {file_path}")
        else:
            # If download fails, create an empty file
            with open(file_path, "w") as f:
                f.write("")
            print(f"Demo mode: Created empty image at {file_path}")
    except Exception as e:
        print(f"Demo mode: Error downloading image: {e}")
        # Create empty file as fallback
        with open(file_path, "w") as f:
            f.write("")
        print(f"Demo mode: Created empty image at {file_path}")
    
    return file_path

# --- Identify Food (Demo Version) ---
def identify_food(image_path):
    # Return a random food item for demo purposes
    food_items = [
        "Apple", "Banana", "Orange", "Mango", "Strawberries",
        "Broccoli", "Carrots", "Chicken Breast", "Salmon Fillet", 
        "Rice", "Pasta", "Sweet Potato", "Avocado"
    ]
    
    # Wait a bit to simulate processing time
    time.sleep(1)
    
    food = random.choice(food_items)
    print(f"Demo mode: Identified as {food}")
    return food

# --- Get Weight (Demo Version) ---
def get_weight():
    # Return a random weight for demo purposes
    weight = round(random.uniform(50.0, 500.0), 1)
    
    # Wait a bit to simulate processing time
    time.sleep(0.5)
    
    return weight

# --- Main Process ---
def main():
    # Keep track of the current capture count
    capture_count = 0
    
    while True:
        try:
            user_input = input("\nPress 'y' then Enter to capture and analyze item (or 'q' to quit)...\n")
            
            if user_input.lower() == 'q':
                print("Exiting program.")
                break
                
            if user_input.lower() != 'y':
                print("Invalid input. Press 'y' to continue or 'q' to quit.")
                continue
            
            # Increment capture count for filename
            capture_count += 1
            
            # 1. Capture image with incrementing number
            image_filename = f"capture{capture_count}.jpg"
            image_path = capture_image(image_filename)
            
            # 2. Get weight
            print("Measuring weight...")
            weight = get_weight()
            print(f"Weight: {weight} g")
            
            # 3. Identify item
            print("Identifying item from image...")
            item_name = identify_food(image_path)
            print(f"Identified: {item_name}")
            
            # 4. Save to JSON
            output = {
                "image_path": f"images/{image_filename}",
                "item": item_name,
                "weight": weight
            }
            
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "item_log.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as file:
                    data = json.load(file)
            else:
                data = []
            
            data.append(output)
            with open(json_path, "w") as file:
                json.dump(data, file, indent=4)
            
            print(f"Saved to item_log.json (capture #{capture_count})")
            
            # If we've captured 7 items, exit automatically
            if capture_count >= 7:
                print("Captured 7 items. Exiting automatically.")
                break
                
        except EOFError:
            # Handle EOF (e.g., when stdin is closed)
            print("Input stream closed. Exiting.")
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\nProcess interrupted. Exiting.")
            break
        except Exception as e:
            print(f"Error during processing: {e}")
            # Continue to next iteration

if __name__ == "__main__":
    print("Running in DEMO mode - for Mac testing only!")
    print("This version doesn't use Raspberry Pi hardware.")
    main() 