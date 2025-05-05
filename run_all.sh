#!/bin/bash

echo "========= KILLING ALL RUNNING PROCESSES ========="
# Kill all python server processes
pkill -f "python.*server.py" || true
# Kill all frontend dev servers
pkill -f "npm run dev" || true
# Kill any other npm processes that might be running
pkill -f "vite" || true
# Sleep to make sure processes are killed
sleep 2

echo "========= CHECKING IF ITEM_LOG.JSON EXISTS ========="
# Make sure item_log.json exists
if [ ! -f "item_log.json" ]; then
  echo "Creating item_log.json"
  echo "[]" > item_log.json
fi

echo "========= CHECKING IF IMAGES DIRECTORY EXISTS ========="
# Make sure images directory exists
mkdir -p images

echo "========= DOWNLOADING SAMPLE IMAGES ========="
# Function to download a sample image for a food item
download_image() {
  local food=$1
  local filename=$2
  
  # Replace spaces with + for URL
  local search_term=$(echo $food | tr ' ' '+')
  
  # Download image from Unsplash
  echo "Downloading image for $food..."
  curl -s "https://source.unsplash.com/100x100/?${search_term},food" > images/$filename
  
  # Check if download was successful
  if [ -s "images/$filename" ]; then
    echo "Downloaded image for $food to images/$filename"
  else
    echo "Failed to download image for $food"
  fi
}

# Download images for the sample items if item_log.json exists but images are empty
if [ -f "item_log.json" ]; then
  # Check if the images are empty
  all_empty=true
  for img in images/capture*.jpg; do
    if [ -s "$img" ]; then
      all_empty=false
      break
    fi
  done
  
  if $all_empty; then
    echo "Images are empty, downloading new samples..."
    # Parse the food items from item_log.json and download images
    items=($(grep -o '"item": "[^"]*"' item_log.json | cut -d'"' -f4))
    filenames=($(grep -o '"image_path": "[^"]*"' item_log.json | cut -d'"' -f4 | awk -F'/' '{print $NF}'))
    
    for i in "${!items[@]}"; do
      if [ -n "${items[$i]}" ] && [ -n "${filenames[$i]}" ]; then
        download_image "${items[$i]}" "${filenames[$i]}"
        # Add a small delay between downloads
        sleep 0.5
      fi
    done
  else
    echo "Images already exist, skipping download"
  fi
fi

echo "========= SETTING UP DATA DIRECTORY FOR RECIPE GENERATION ========="
# Make sure the data directory exists for the recipe generator
mkdir -p backend/data

# Copy item_log.json to backend/data/food_log.json (with format conversion)
if [ -f "item_log.json" ]; then
  echo "Copying and converting item_log.json to backend/data/food_log.json"
  # Use jq to convert the format if it's installed
  if command -v jq >/dev/null 2>&1; then
    jq 'map({food_type: .item, weight_grams: .weight})' item_log.json > backend/data/food_log.json
  else
    # Simple conversion without jq (less reliable)
    cat item_log.json | sed 's/"item"/"food_type"/g' | sed 's/"weight"/"weight_grams"/g' > backend/data/food_log.json
  fi
  echo "Food log data prepared for recipe generation"
fi

echo "========= STARTING SERVER ========="
# Start server in background
cd backend
python server.py > /dev/null 2>&1 &
SERVER_PID=$!
cd ..

# Wait for server to start
sleep 3

echo "========= SERVER STARTED ========="
echo "Server running on http://localhost:8000"

echo "========= SETTING UP FRONTEND ========="
# Create .env file for frontend
echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env.local

echo "========= STARTING FRONTEND ========="
# Start frontend in background
cd frontend
echo "Frontend starting at http://localhost:5173"
npm run dev -- --host > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

echo "========= SETUP COMPLETE ========="
echo "Frontend: http://localhost:5173"
echo "Server API: http://localhost:8000"
echo "Press any key to shut down all processes"
read -n 1

echo "========= SHUTTING DOWN ========="
kill $SERVER_PID || true
kill $FRONTEND_PID || true
pkill -f "python.*server.py" || true
pkill -f "npm run dev" || true
pkill -f "vite" || true

echo "========= ALL PROCESSES STOPPED =========" 