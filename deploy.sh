#!/bin/bash

# CSV Merge Wizard - Vercel Deployment Script

echo "🚀 Preparing CSV Merge Wizard for Vercel deployment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if all required files exist
required_files=("main.py" "requirements.txt" "vercel.json" "index.html")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ All required files found"

# Test the application
echo "🧪 Testing application..."
python -c "import main; print('✅ Application imports successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Application test passed"
else
    echo "❌ Application test failed"
    exit 1
fi

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your application should now be live on Vercel" 