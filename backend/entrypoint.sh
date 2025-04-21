#!/bin/bash

echo "📦 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗃️ Initializing database schema..."
python -m app.init_db

echo "🚀 Starting FastAPI"
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
