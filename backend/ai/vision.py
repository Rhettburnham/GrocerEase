import os
import base64
import json
import requests
from openai import OpenAI

class FoodVisionIdentifier:
    def __init__(self, api_key=None):
        """
        Initialize the OpenAI Vision API interface.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, tries to get from environment.
        """
        # Get API key from args or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass to constructor.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
    
    def identify_food(self, image_path):
        """
        Identify the food in the image using OpenAI Vision API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Result with food_type and confidence
        """
        try:
            # Read the image file
            with open(image_path, "rb") as image_file:
                # Encode image in base64
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Create the API request
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in food identification. Your task is to analyze the image and identify what food item is present. Return only a JSON object with 'food_type' and 'confidence' fields."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Identify the food in this image. Return JSON with format {\"food_type\": \"name of food\", \"confidence\": confidence level from 0-1}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                            ]
                        }
                    ],
                    max_tokens=100
                )
                
                # Extract the response text
                response_text = response.choices[0].message.content
                
                # Extract the JSON part from the response
                try:
                    # Try to parse the response directly
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON from the text
                    # This handles cases where the model might add explanatory text
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(0))
                    else:
                        # If no JSON found, create a default response
                        result = {
                            "food_type": "unknown",
                            "confidence": 0.0,
                            "error": "Failed to parse response"
                        }
                
                # Ensure the expected fields are present
                if "food_type" not in result:
                    result["food_type"] = "unknown"
                if "confidence" not in result:
                    result["confidence"] = 0.0
                
                return result
                
        except Exception as e:
            print(f"Error identifying food: {e}")
            return {"food_type": "unknown", "confidence": 0.0, "error": str(e)}

def test_vision_api():
    """Test function for the vision API module"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vision.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        sys.exit(1)
    
    try:
        identifier = FoodVisionIdentifier()
        result = identifier.identify_food(image_path)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_vision_api() 