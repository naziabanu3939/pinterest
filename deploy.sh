#!/bin/bash
# Automated Heroku Deployment Script for Pinterest Quotes
# Run this script after cloning the repo

set -e  # Exit on error

echo "🚀 Pinterest Quotes - Heroku Deployment Script"
echo "=============================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Install from: https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli-x64.exe"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install from: https://git-scm.com"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install from: https://www.python.org"
    exit 1
fi

echo "✓ Prerequisites found"
echo ""

# Step 1: Login to Heroku
echo "Step 1️⃣  Login to Heroku..."
heroku login
echo ""

# Step 2: Get app name
echo "Step 2️⃣  Create Heroku app"
read -p "Enter unique app name (e.g., pinterest-quotes-$(date +%s)): " APP_NAME

if [ -z "$APP_NAME" ]; then
    APP_NAME="pinterest-quotes-$(date +%s)"
fi

echo "Creating app: $APP_NAME..."
heroku create $APP_NAME
echo ""

# Step 3: Generate encryption key
echo "Step 3️⃣  Generate encryption key..."
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "✓ Encryption key generated"
echo ""

# Step 4: Get Pinterest credentials
echo "Step 4️⃣  Pinterest App Credentials"
echo "You need to register an app at: https://developers.pinterest.com"
echo ""
read -p "Enter Pinterest Client ID: " PINTEREST_CLIENT_ID
read -p "Enter Pinterest Client Secret: " PINTEREST_CLIENT_SECRET

if [ -z "$PINTEREST_CLIENT_ID" ] || [ -z "$PINTEREST_CLIENT_SECRET" ]; then
    echo "❌ Pinterest credentials required!"
    exit 1
fi

echo ""

# Step 5: Generate secret key
echo "Step 5️⃣  Generate Flask secret key..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "✓ Secret key generated"
echo ""

# Step 6: Set environment variables
echo "Step 6️⃣  Setting Heroku environment variables..."
REDIRECT_URI="https://${APP_NAME}.herokuapp.com/auth/callback"

heroku config:set \
    FLASK_ENV=production \
    SECRET_KEY="$SECRET_KEY" \
    ENCRYPTION_KEY="$ENCRYPTION_KEY" \
    PINTEREST_CLIENT_ID="$PINTEREST_CLIENT_ID" \
    PINTEREST_CLIENT_SECRET="$PINTEREST_CLIENT_SECRET" \
    PINTEREST_REDIRECT_URI="$REDIRECT_URI" \
    --app=$APP_NAME

echo "✓ Environment variables set"
echo ""

# Step 7: Add PostgreSQL database
echo "Step 7️⃣  Adding PostgreSQL database (hobby-dev - free)..."
heroku addons:create heroku-postgresql:hobby-dev --app=$APP_NAME
echo "✓ Database created"
echo ""

# Step 8: Deploy
echo "Step 8️⃣  Deploying code to Heroku..."
git push heroku main
echo "✓ Code deployed"
echo ""

# Step 9: Verify
echo "Step 9️⃣  Verifying deployment..."
heroku logs --tail --num=20 --app=$APP_NAME
echo ""

echo "✅ Deployment Complete!"
echo ""
echo "🎉 Your app is live at: https://${APP_NAME}.herokuapp.com"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Update Pinterest app with redirect URI:"
echo "   https://${APP_NAME}.herokuapp.com/auth/callback"
echo "2. Open app: heroku open --app=$APP_NAME"
echo "3. Click 'Login with Pinterest' to test"
echo ""
echo "💾 Save these for reference:"
echo "   App name: $APP_NAME"
echo "   Redirect URI: $REDIRECT_URI"
echo ""
