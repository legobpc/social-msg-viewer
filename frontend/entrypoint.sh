#!/bin/bash

# If the project has not yet been initialized
if [ ! -f /app/package.json ]; then
  echo "⚙️ Creating a new Next.js project..."

  # Use npx with full CLI flags to avoid interactive prompts
  npx create-next-app@latest /tmp/tmp-app \
    --typescript \
    --no-eslint \
    --no-tailwind \
    --import-source react \
    --app \
    --no-src \
    --use-npm \
    --yes

  echo "📁 Copying project files into /app..."
  cp -r /tmp/tmp-app/* /app/
  cp -r /tmp/tmp-app/.* /app/ 2>/dev/null || true
  rm -rf /tmp/tmp-app

  echo "📦 Installing dependencies..."
  cd /app
  yarn install
fi

echo "🚀 Starting Next.js"
cd /app
yarn dev
