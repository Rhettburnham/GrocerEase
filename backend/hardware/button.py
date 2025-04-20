import RPi.GPIO as GPIO
import time
from threading import Thread, Event

class Button:
    def __init__(self, pin, callback, debounce_time=0.3):
        """
        Initialize a button on the specified GPIO pin.
        
        Args:
            pin (int): GPIO pin number (BCM numbering)
            callback (function): Function to call when button is pressed
            debounce_time (float): Debounce time in seconds
        """
        self.pin = pin
        self.callback = callback
        self.debounce_time = debounce_time
        self.last_press_time = 0
        self.running = False
        self.stop_event = Event()
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def _button_callback(self, channel):
        """Internal callback for GPIO event detection"""
        current_time = time.time()
        if current_time - self.last_press_time > self.debounce_time:
            self.last_press_time = current_time
            self.callback()
    
    def start(self):
        """Start listening for button presses"""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            GPIO.add_event_detect(self.pin, GPIO.FALLING, 
                                 callback=self._button_callback, 
                                 bouncetime=int(self.debounce_time * 1000))
    
    def stop(self):
        """Stop listening for button presses"""
        if self.running:
            GPIO.remove_event_detect(self.pin)
            self.running = False
            self.stop_event.set()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop()
        # Don't call GPIO.cleanup() here to avoid affecting other components

def test_button():
    """Test function for the button module"""
    def on_button_press():
        print("Button pressed!")
    
    button = Button(pin=17, callback=on_button_press)
    button.start()
    
    try:
        print("Press the button (Ctrl+C to exit)...")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        button.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    test_button() 