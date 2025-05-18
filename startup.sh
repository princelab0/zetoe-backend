#!/bin/bash

# Activate virtual environment if needed
# source venv/bin/activate

# Start your app (e.g., with uvicorn for FastAPI)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

