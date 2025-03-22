#!/bin/bash

# Get port from environment variable or use default
PORT="${PORT:-8000}"

# Start the application
exec python -c "import os; from uvicorn import run; port = int(os.getenv('PORT', '8000')); run('main:app', host='0.0.0.0', port=port)"