#!/bin/bash

echo "📦 Installing dependencies..."
cd /app
yarn install

echo "🚀 Starting Next.js"
yarn dev