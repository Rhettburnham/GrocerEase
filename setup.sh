#!/bin/bash

# Setup script for FoodBot project

# Ensure data directories exist
mkdir -p data/images

# Create empty food_log.json if it doesn't exist
if [ ! -f data/food_log.json ]; then
    echo '{"entries": []}' > data/food_log.json
    echo "Created empty food_log.json file"
fi

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example - please update your OpenAI API key"
fi

# Ensure proper directory for systemd service
echo "Note: You may need to update paths in foodbot.service to match your installation directory"

echo "Setup complete! Next steps:"
echo "1. Update your OpenAI API key in the .env file"
echo "2. Install dependencies with 'pip install -r requirements.txt'"
echo "3. Set up the frontend with 'cd frontend && npm install && npm run build'" 