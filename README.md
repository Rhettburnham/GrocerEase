# FoodBot: Raspberry Pi Food-Weighing & Identification Robot

A smart device that captures photos, weighs food items, identifies them using AI vision, and logs everything in a web interface. Also suggests recipes based on available ingredients.

## Overview

FoodBot uses a Raspberry Pi with a camera, load cell, and a button to create a seamless food logging experience. Each time you press the button, the system:

1. Weighs the food item on the scale
2. Takes a photo using the camera
3. Analyzes the image using OpenAI Vision API to identify the food
4. Logs the timestamp, food type, weight, and image
5. Displays all entries in a responsive web interface
6. Suggests recipes based on available ingredients

## Hardware Requirements

- Raspberry Pi 4 (Model B, 2GB+ RAM) running Raspberry Pi OS
- Momentary push-button (connected to GPIO pin 17)
- 5MP Arducam for Raspberry Pi (manual-focus M12 mount)
- HX711 24-bit ADC + 20kg load cell kit
- Solderless breadboard & jumper wires
- Power supply for Raspberry Pi

## Wiring Diagram

Connect your hardware components as follows:

### HX711 Load Cell Connections:
- HX711 VCC → Raspberry Pi 3.3V
- HX711 GND → Raspberry Pi GND
- HX711 DT → Raspberry Pi GPIO 5
- HX711 SCK → Raspberry Pi GPIO 6
- Load Cell connections to HX711:
  - Red → E+
  - Black → E-
  - Green → A+
  - White → A-

### Button Connection:
- One terminal → Raspberry Pi GPIO 17
- Other terminal → Raspberry Pi GND

### Camera Connection:
- Connect the camera module to the Raspberry Pi camera port

## Software Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/foodbot.git
cd foodbot
```

### 2. Run the setup script (creates necessary directories and files)

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Set up Python environment

```bash
# Install required system packages
sudo apt update
sudo apt install -y python3-venv python3-dev libcamera-dev python3-libcamera

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install RPi.GPIO hx711py openai flask flask-cors
```

### 4. Set up OpenAI API Key

```bash
# Set your OpenAI API key in the environment
export OPENAI_API_KEY=your_api_key_here

# For permanent setup, add to /etc/environment or .bashrc
echo 'OPENAI_API_KEY=your_api_key_here' | sudo tee -a /etc/environment
```

### 5. Build the frontend

```bash
# Install Node.js and npm if not already installed
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Install frontend dependencies and build
cd frontend
npm install
npm run build
```

### 6. Set up as a system service (optional)

```bash
# Edit the service file to update paths and API key
nano foodbot.service

# Copy the service file to systemd directory
sudo cp foodbot.service /etc/systemd/system/

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable foodbot
sudo systemctl start foodbot
```

## Important Configuration Files

This project includes several important configuration files that must be properly set up:

- `.env`: Contains environment variables for OpenAI API keys and hardware configuration. A sample is provided in `.env.example`.
- `foodbot.service`: The systemd service file for auto-starting the application. Update the paths to match your installation.
- `requirements.txt`: Lists all Python dependencies.
- The `data` directory structure with `images` subdirectory: Created automatically by the setup script.

## Usage

### Calibrating the Scale

Before first use, you need to calibrate the scale with a known weight:

```bash
cd backend
python -m hardware.scale --calibrate
```

Follow the on-screen instructions to place a known weight on the scale and enter its weight in grams.

### Running Manually

If you haven't set up the systemd service, you can run the application manually:

```bash
cd backend
python main.py
```

### Using the FoodBot

1. Place an item on the scale
2. Press the button
3. Wait for the processing (weight measurement, image capture, and AI identification)
4. View the results in the web interface at `http://[raspberry-pi-ip]:5000`
5. Browse recipe suggestions based on available ingredients

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