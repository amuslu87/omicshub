#!/bin/bash

# OmicsHub - Day 4 Git Commit & Push
# This script commits all Docker-related changes and pushes to GitHub

echo "=========================================="
echo "🔄 OmicsHub - Day 4 Git Push"
echo "=========================================="
echo ""

cd ~/omicshub

# Check current status
echo "📋 Current git status:"
git status
echo ""

# Add all new files
echo "➕ Adding new files..."
git add .

echo ""
echo "📝 Files to be committed:"
git status --short
echo ""

# Create commit
echo "💾 Creating commit..."
git commit -m "feat: Day 4 - Docker containerization complete

- Added Dockerfile for API container
- Added docker-compose.yml for orchestration
- Added database initialization script
- Added quick_load.sql for data loading
- Docker containers running successfully
- PostgreSQL database populated with:
  * 10 cancer genes
  * 16 GO terms
  * 28 gene-GO annotations
- API accessible at http://localhost:8000
- All 9 endpoints tested and working"

echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "=========================================="
echo "✅ Push Complete!"
echo "=========================================="
echo ""
echo "View your repository at:"
echo "https://github.com/amuslu87/omicshub"
echo ""
