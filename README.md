# GrocerEase

A simple food logging system with frontend visualization.

## System Overview

GrocerEase consists of two main components:

1. **Backend**: A Python-based server and food logging script
2. **Frontend**: A React web application that displays the food log

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js and npm
- (Optional) Raspberry Pi with camera and HX711 scale

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the server (in one terminal):
   ```
   python server.py
   ```

4. Run the main logging script (in another terminal):
   ```
   python main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and go to:
   ```
   http://localhost:5173
   ```

## Usage

1. With the backend server and frontend running, open the frontend in your browser.
2. In the terminal running `main.py`, press 'y' and Enter to capture and log food items.
3. The script will:
   - Capture an image
   - Measure the weight using the scale
   - Identify the food in the image
   - Log the data to item_log.json

## How It Works

1. The `main.py` script:
   - Captures images using Raspberry Pi camera
   - Measures weight with HX711 load cell
   - Identifies food items with OpenAI Vision
   - Updates item_log.json

2. The `server.py` script:
   - Serves the item_log.json to the frontend
   - Serves captured images

3. The frontend:
   - Displays the food log in a table format
   - Shows food type, weight, and images

## Features

### Food Logging
- Records weight of food items using the HX711 load cell
- Captures images with the camera
- Uses OpenAI Vision API to identify food types
- Tracks all logs with timestamps and confidence levels

### Recipe Suggestions
- Suggests recipes based on available ingredients
- Recipes categorized into breakfast, lunch, and dinner
- Ensures there's enough of each ingredient for the suggested recipes
- Generates detailed recipes using OpenAI API
- Recipe generation includes ingredients, instructions, and nutritional information

## Project Structure

```
foodbot/
├── backend/
│   ├── hardware/          # Hardware interface modules
│   │   ├── button.py      # GPIO button handling
│   │   ├── camera.py      # Camera capture
│   │   └── scale.py       # HX711 load cell interface
│   ├── ai/
│   │   ├── vision.py      # OpenAI Vision API for food identification
│   │   └── recipe_generator.py  # OpenAI API for recipe generation
│   ├── storage/
│   │   └── log.py         # JSON-based data logging
│   ├── server/
│   │   └── api.py         # Flask API server
│   └── main.py            # Main application
├── frontend/              # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   │   ├── FoodLogTable.jsx       # Table for food logs
│   │   │   ├── RecipeSuggestions.jsx  # Recipe suggestion component
│   │   │   ├── Header.jsx             # App header
│   │   │   └── TabNavigation.jsx      # Tab navigation component
│   │   ├── App.jsx        # Main application component
│   │   └── main.jsx       # Entry point
│   └── dist/              # Built static files
├── data/                  # Data storage
│   ├── images/            # Captured images
│   └── food_log.json      # Log file
└── foodbot.service        # Systemd service file
```

## API Endpoints

### Food Log Endpoints
- GET `/api/log` - Get all food log entries
- GET `/api/log/latest` - Get the latest food log entry
- GET `/api/log/<entry_id>` - Get a specific food log entry
- GET `/api/images/<filename>` - Serve images from the data directory

### Recipe Endpoints
- GET `/api/recipe-ideas?meal_type=<type>` - Generate recipe ideas based on available ingredients
- POST `/api/recipe` - Generate a full recipe (requires recipe_name and ingredients in request body)

## Troubleshooting

### Camera Issues
- Make sure the camera is enabled in `raspi-config`
- Check that the camera is properly connected to the Raspberry Pi

### Scale Issues
- Recalibrate the scale if weights seem inaccurate
- Check wiring connections to HX711

### Web Interface Issues
- Ensure the Flask server is running (check systemctl status if using service)
- Verify that port 5000 is accessible (not blocked by firewall)

### Recipe Generation Issues
- Check that your OpenAI API key is valid and properly set in the environment
- Make sure you have sufficient credits on your OpenAI account

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the Vision API and GPT API
- The HX711 library contributors
- Raspberry Pi Foundation 