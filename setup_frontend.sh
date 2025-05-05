#!/bin/bash

# Create .env.local file for frontend
echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env.local
echo "Frontend environment configured to use API at http://localhost:8000"

# Start frontend development server
cd frontend
npm run dev -- --host 