#!/bin/bash
# Startup script for Render deployment

# Change to the gemini-backend directory
cd gemini-backend

# Run database migrations
alembic upgrade head

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port $PORT 