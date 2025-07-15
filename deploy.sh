#!/bin/bash

echo "🚀 PersonaForge AI - Vercel Deployment Script"
echo "=============================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Installing dependencies..."
npm install

echo "✅ Building for production..."
npm run build

echo "✅ Deploying to Vercel..."
vercel --prod

echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set up environment variables in Vercel dashboard:"
echo "   - GROQ_API_KEY=your_groq_api_key"
echo "   - GEMINI_API_KEY=your_gemini_api_key"
echo "2. Test your deployment"
echo "3. Monitor logs for any issues"
echo ""
echo "🔗 Your app will be available at the URL provided by Vercel" 