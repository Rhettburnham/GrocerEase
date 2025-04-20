import time
import json
import os
import RPi.GPIO as GPIO
from hx711 import HX711

class Scale:
    def __init__(self, dout_pin=5, sck_pin=6, calibration_file='scale_calibration.json'):
        """
        Initialize the scale with HX711 interface.
        
        Args:
            dout_pin (int): HX711 data output pin (BCM numbering)
            sck_pin (int): HX711 serial clock pin (BCM numbering)
            calibration_file (str): Path to calibration data file
        """
        self.dout_pin = dout_pin
        self.sck_pin = sck_pin
        self.calibration_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                          'data', calibration_file)
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Initialize HX711
        self.hx = HX711(dout_pin=self.dout_pin, pd_sck_pin=self.sck_pin)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.reset()
        
        # Load calibration data if available
        self.reference_unit = self._load_calibration()
        if self.reference_unit:
            self.hx.set_reference_unit(self.reference_unit)
        
    def _load_calibration(self):
        """Load calibration data from file"""
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    calibration_data = json.load(f)
                    return calibration_data.get('reference_unit', 1)
            return None
        except Exception as e:
            print(f"Error loading calibration data: {e}")
            return None
    
    def _save_calibration(self, reference_unit):
        """Save calibration data to file"""
        os.makedirs(os.path.dirname(self.calibration_file), exist_ok=True)
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump({'reference_unit': reference_unit}, f)
        except Exception as e:
            print(f"Error saving calibration data: {e}")
    
    def tare(self, times=10):
        """
        Tare the scale (set current weight as zero).
        
        Args:
            times (int): Number of readings to average
        """
        self.hx.reset()
        self.hx.tare(times)
        print("Scale tared")
    
    def calibrate(self, known_weight_grams):
        """
        Calibrate the scale with a known weight.
        
        Args:
            known_weight_grams (float): Weight in grams that's placed on the scale
        """
        print("Please remove all weight from the scale...")
        time.sleep(2)
        
        # Tare first
        self.tare()
        
        print(f"Please place the {known_weight_grams}g weight on the scale...")
        time.sleep(3)
        
        # Get multiple readings and average them
        readings = []
        for _ in range(10):
            reading = self.hx.get_value()
            readings.append(reading)
            time.sleep(0.1)
        
        # Calculate the average reading
        average_reading = sum(readings) / len(readings)
        
        # Calculate the reference unit
        self.reference_unit = average_reading / known_weight_grams
        
        # Set and save the reference unit
        self.hx.set_reference_unit(self.reference_unit)
        self._save_calibration(self.reference_unit)
        
        print(f"Calibration complete. Reference unit: {self.reference_unit}")
    
    def get_weight(self, times=10):
        """
        Get the current weight in grams.
        
        Args:
            times (int): Number of readings to average
        
        Returns:
            float: Weight in grams, rounded to 1 decimal place
        """
        if not self.reference_unit:
            print("Scale not calibrated. Returning raw value.")
            return self.hx.get_value() / 10.0
        
        total = 0
        for _ in range(times):
            total += self.hx.get_weight(times=1)
        
        weight = total / times
        return round(weight, 1)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.hx.power_down()
        # Don't call GPIO.cleanup() here to avoid affecting other components

def test_scale():
    """Test function for the scale module"""
    scale = Scale()
    
    # Check if calibration needed
    if not scale.reference_unit:
        print("Scale needs calibration.")
        cal_weight = float(input("Enter the weight (in grams) of your calibration object: "))
        scale.calibrate(cal_weight)
    
    try:
        print("Scale testing. Press Ctrl+C to exit...")
        while True:
            weight = scale.get_weight()
            print(f"Current weight: {weight}g")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        scale.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scale testing and calibration')
    parser.add_argument('--calibrate', action='store_true', help='Run calibration routine')
    args = parser.parse_args()
    
    scale = Scale()
    
    if args.calibrate:
        cal_weight = float(input("Enter the weight (in grams) of your calibration object: "))
        scale.calibrate(cal_weight)
    else:
        test_scale() 