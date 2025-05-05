#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if the script is run with root privileges on Raspberry Pi
if [ "$(uname -n)" = "raspberrypi" ] && [ "$(id -u)" -ne 0 ]; then
  echo -e "${RED}Warning: You may need to run this script with sudo on Raspberry Pi${NC}"
  echo "to access GPIO pins. Press Enter to continue or Ctrl+C to exit."
  read -r
fi

# Create images directory if it doesn't exist
mkdir -p data/images

# Check if item_log.json exists, create if it doesn't
if [ ! -f "item_log.json" ]; then
  echo "Creating empty item_log.json file"
  echo "[]" > item_log.json
fi

# Kill any existing Python processes running server.py
echo -e "${RED}Killing any existing server processes...${NC}"
pkill -f "python.*server.py" || true
sleep 2  # Give time for ports to be released

# Export OpenAI API key if provided
if [ -n "$1" ]; then
  export OPENAI_API_KEY="$1"
  echo "Using provided OpenAI API key"
else
  echo "No OpenAI API key provided. Vision identification may not work."
fi

# Try starting server on port 8000 (high port to avoid system service conflicts)
echo -e "${GREEN}Starting server on port 8000...${NC}"
cd backend || exit
export PORT=8000
python server.py > server_log.txt 2>&1 &
SERVER_PID=$!

# Wait to see if it starts successfully
sleep 5

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
  echo -e "${GREEN}Server started successfully on port 8000${NC}"
  SERVER_PORT=8000
else
  # Try port 8001 instead
  echo -e "${YELLOW}Failed to start on port 8000, trying port 8001...${NC}"
  export PORT=8001
  python server.py > server_log.txt 2>&1 &
  SERVER_PID=$!
  sleep 5
  
  if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}Server started successfully on port 8001${NC}"
    SERVER_PORT=8001
  else
    echo -e "${RED}Failed to start server. Check server_log.txt for details.${NC}"
    exit 1
  fi
fi

# Create temporary .env file for frontend with API URL
echo -e "${GREEN}Setting up frontend with API on port $SERVER_PORT${NC}"
cd ..
echo "VITE_API_BASE_URL=http://localhost:$SERVER_PORT" > frontend/.env.local

# Start main script
echo -e "${GREEN}Starting main logging script...${NC}"
echo "Press 'y' and Enter to capture and log food items"
echo "Press Ctrl+C to exit"
cd backend
python main.py

# Clean up server process when main script exits
kill $SERVER_PID || true

echo -e "${YELLOW}GrocerEase has been shut down.${NC}" 