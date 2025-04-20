import os
import json
import time
from datetime import datetime
import threading

class FoodLog:
    def __init__(self, log_file=None):
        """
        Initialize the food log manager.
        
        Args:
            log_file (str, optional): Path to the log file. If None, uses default.
        """
        if log_file is None:
            # Use default location in data directory
            self.log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'data', 'food_log.json')
        else:
            self.log_file = log_file
        
        # Create parent directory if needed
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Create the log file if it doesn't exist
        if not os.path.exists(self.log_file):
            self._write_log([])
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def _read_log(self):
        """
        Read the log file.
        
        Returns:
            list: The contents of the log file as a list of entries
        """
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return an empty list
            return []
        except FileNotFoundError:
            # If the file doesn't exist, return an empty list
            return []
    
    def _write_log(self, entries):
        """
        Write entries to the log file.
        
        Args:
            entries (list): The entries to write to the log file
        """
        # Write to a temporary file first, then rename to ensure atomic write
        temp_file = f"{self.log_file}.tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(entries, f, indent=2)
            
            # Rename the temporary file to the actual file
            os.replace(temp_file, self.log_file)
        except Exception as e:
            print(f"Error writing log: {e}")
            # Clean up the temporary file if there was an error
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def add_entry(self, food_type, weight, image_path, confidence=None, metadata=None):
        """
        Add an entry to the log.
        
        Args:
            food_type (str): The type of food
            weight (float): The weight in grams
            image_path (str): Path to the image
            confidence (float, optional): Confidence in the food type identification
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: The added entry
        """
        # Create the entry
        entry = {
            "id": self._generate_id(),
            "timestamp": datetime.now().isoformat(),
            "food_type": food_type,
            "weight_grams": weight,
            "image_path": image_path
        }
        
        # Add optional fields
        if confidence is not None:
            entry["confidence"] = confidence
        
        if metadata is not None:
            entry["metadata"] = metadata
        
        # Add to the log in a thread-safe way
        with self.lock:
            entries = self._read_log()
            entries.append(entry)
            self._write_log(entries)
        
        return entry
    
    def get_entries(self, limit=None, reverse=True):
        """
        Get entries from the log.
        
        Args:
            limit (int, optional): Maximum number of entries to return
            reverse (bool): Whether to return entries in reverse order (newest first)
            
        Returns:
            list: The log entries
        """
        with self.lock:
            entries = self._read_log()
        
        # Sort entries by timestamp
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=reverse)
        
        # Limit the number of entries if requested
        if limit is not None:
            entries = entries[:limit]
        
        return entries
    
    def get_entry(self, entry_id):
        """
        Get a specific entry by ID.
        
        Args:
            entry_id (str): The ID of the entry to get
            
        Returns:
            dict: The entry, or None if not found
        """
        with self.lock:
            entries = self._read_log()
        
        for entry in entries:
            if entry.get("id") == entry_id:
                return entry
        
        return None
    
    def delete_entry(self, entry_id):
        """
        Delete an entry from the log.
        
        Args:
            entry_id (str): The ID of the entry to delete
            
        Returns:
            bool: True if the entry was deleted, False otherwise
        """
        with self.lock:
            entries = self._read_log()
            
            # Find the entry to delete
            for i, entry in enumerate(entries):
                if entry.get("id") == entry_id:
                    # Remove the entry
                    del entries[i]
                    self._write_log(entries)
                    return True
        
        return False
    
    def _generate_id(self):
        """
        Generate a unique ID for an entry.
        
        Returns:
            str: A unique ID
        """
        # Use timestamp and a random number for uniqueness
        return f"{int(time.time())}_{os.urandom(4).hex()}"

def test_food_log():
    """Test function for the food log module"""
    log = FoodLog()
    
    # Add a test entry
    entry = log.add_entry(
        food_type="Apple",
        weight=150.5,
        image_path="data/images/image_1.jpg",
        confidence=0.95,
        metadata={"color": "red"}
    )
    
    print("Added entry:")
    print(json.dumps(entry, indent=2))
    
    # Get all entries
    entries = log.get_entries()
    
    print("\nAll entries:")
    print(json.dumps(entries, indent=2))

if __name__ == "__main__":
    test_food_log() 