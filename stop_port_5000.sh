#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking for processes using port 5000...${NC}"

# Find process using port 5000
PORT_PROCESS=$(lsof -i :5000 -sTCP:LISTEN -t)

if [ -z "$PORT_PROCESS" ]; then
    echo -e "${GREEN}Port 5000 is not in use. You're good to go!${NC}"
    exit 0
fi

echo -e "${RED}Found process(es) using port 5000:${NC}"
lsof -i :5000 -sTCP:LISTEN

# Check if running on macOS
if [ "$(uname)" == "Darwin" ]; then
    echo -e "\n${YELLOW}This appears to be macOS.${NC}"
    echo -e "${YELLOW}The AirPlay Receiver service might be using port 5000.${NC}"
    
    echo -e "\n${YELLOW}Try this to disable AirPlay Receiver:${NC}"
    echo -e "1. Open System Settings"
    echo -e "2. Navigate to 'General' -> 'AirDrop & Handoff'"
    echo -e "3. Turn off 'AirPlay Receiver'"
    
    echo -e "\n${YELLOW}Alternatively, to stop it temporarily:${NC}"
    echo -e "${RED}sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.AirPlayXPCHelper.plist${NC}"
    
    read -p "Do you want to try stopping AirPlay Receiver now? (y/n): " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        echo "Attempting to stop AirPlay Receiver..."
        sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.AirPlayXPCHelper.plist
        echo "Checking if port 5000 is now available..."
        sleep 2
        NEW_PORT_PROCESS=$(lsof -i :5000 -sTCP:LISTEN -t)
        if [ -z "$NEW_PORT_PROCESS" ]; then
            echo -e "${GREEN}Success! Port 5000 is now available.${NC}"
        else
            echo -e "${RED}Port 5000 is still in use by:${NC}"
            lsof -i :5000 -sTCP:LISTEN
        fi
    fi
else
    # For non-macOS systems
    echo -e "\n${YELLOW}To kill the process(es) using port 5000:${NC}"
    echo -e "${RED}sudo kill -9 $PORT_PROCESS${NC}"
    
    read -p "Do you want to kill these processes now? (y/n): " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        echo "Attempting to kill processes..."
        sudo kill -9 $PORT_PROCESS
        echo "Checking if port 5000 is now available..."
        sleep 2
        NEW_PORT_PROCESS=$(lsof -i :5000 -sTCP:LISTEN -t)
        if [ -z "$NEW_PORT_PROCESS" ]; then
            echo -e "${GREEN}Success! Port 5000 is now available.${NC}"
        else
            echo -e "${RED}Port 5000 is still in use by:${NC}"
            lsof -i :5000 -sTCP:LISTEN
        fi
    fi
fi

echo -e "\n${YELLOW}After freeing port 5000, you can run your server:${NC}"
echo -e "${GREEN}cd backend && python server.py${NC}" 