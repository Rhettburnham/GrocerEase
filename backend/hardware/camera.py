import os
import time
import subprocess
from datetime import datetime

class Camera:
    def __init__(self, save_dir=None):
        """
        Initialize the camera module.
        
        Args:
            save_dir (str): Directory to save captured images
        """
        # Create data directory for images if not specified
        if save_dir is None:
            self.save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'images')
        else:
            self.save_dir = save_dir
            
        # Ensure the directory exists
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Get the next image number
        self.next_image_num = self._get_next_image_number()
    
    def _get_next_image_number(self):
        """Get the next sequential image number based on existing files"""
        # List all files that match the pattern image_X.jpg
        files = [f for f in os.listdir(self.save_dir) if f.startswith('image_') and f.endswith('.jpg')]
        
        if not files:
            return 1
            
        # Extract numbers and find the max
        try:
            numbers = [int(f.split('_')[1].split('.')[0]) for f in files]
            return max(numbers) + 1
        except (ValueError, IndexError):
            # If parsing fails, start from 1
            return 1
    
    def capture(self):
        """
        Capture an image using libcamera.
        
        Returns:
            str: Path to the captured image file
        """
        # Generate filename with the next sequential number
        filename = f"image_{self.next_image_num}.jpg"
        filepath = os.path.join(self.save_dir, filename)
        
        # Use libcamera-still to capture the image
        try:
            cmd = [
                "libcamera-still",
                "--width", "1920",
                "--height", "1080",
                "--output", filepath,
                "--nopreview"
            ]
            
            subprocess.run(cmd, check=True)
            
            # Increment the image number for next capture
            self.next_image_num += 1
            
            print(f"Image captured: {filepath}")
            return filepath
            
        except subprocess.CalledProcessError as e:
            print(f"Error capturing image: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

def test_camera():
    """Test function for the camera module"""
    camera = Camera()
    
    print("Capturing image...")
    image_path = camera.capture()
    
    if image_path:
        print(f"Image saved to: {image_path}")
    else:
        print("Failed to capture image")

if __name__ == "__main__":
    test_camera() 