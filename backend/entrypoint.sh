#!/bin/bash

# If the project is not initialized yet
if [ ! -f /app/app/main.py ]; then
  echo "⚙️ Creating FastAPI project..."

  mkdir -p /app/app
  cat > /app/app/main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}
EOF

  cat > /app/app/__init__.py <<'EOF'
# package init
EOF

  echo "📦 Initializing requirements..."
  pip install --upgrade pip
  pip install fastapi uvicorn

  # Save dependencies (optional)
  pip freeze > /app/requirements.txt
fi

echo "🚀 Starting FastAPI"
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
