# Complete Heroku Deployment Checklist

Follow these steps in order. Each step is required.

---

## ✅ Pre-Deployment Checklist (Do these first!)

### 1. Install Heroku CLI
- **Windows**: Download from https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli-x64.exe
- **macOS**: `brew tap heroku/brew && brew install heroku`
- **Linux**: `curl https://cli-heroku.com/install.sh | sh`

Verify installation:
```bash
heroku --version
```

### 2. Create Heroku Account
- Go to https://www.heroku.com
- Sign up (free account)
- Verify email

### 3. Create Pinterest Business Account
- Go to https://www.pinterest.com/business/create/
- Or use existing Pinterest account

### 4. Register Pinterest App
- Go to https://developers.pinterest.com/apps
- Click "Create App"
- Fill in details:
  - **App Name**: pinterest-quotes-uploader
  - **App Description**: Automated quote poster
  - **Purpose**: Create and manage pins
- Accept terms
- **Copy and save**:
  - Client ID
  - Client Secret
  - (You'll need these later!)

---

## 🚀 Deployment Steps (Do in order)

### Step 1️⃣: Clone Repository
```bash
git clone https://github.com/naziabanu3939/pinterest.git
cd pinterest
```

### Step 2️⃣: Login to Heroku
```bash
heroku login
```
This opens a browser. Sign in with your Heroku account.

### Step 3️⃣: Create Heroku App
```bash
heroku create pinterest-quotes-YOUR-NAME
```
Replace `YOUR-NAME` with your name or a unique identifier.

**Example:**
```bash
heroku create pinterest-quotes-abhi
```

**Save this name** - you'll need it later!

### Step 4️⃣: Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Copy the output** (looks like: `Fernet...`)

### Step 5️⃣: Set Environment Variables

Replace placeholders with your actual values:

```bash
# Set all at once:
heroku config:set \
    FLASK_ENV=production \
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") \
    ENCRYPTION_KEY="paste_your_encryption_key_here" \
    PINTEREST_CLIENT_ID="paste_your_client_id_here" \
    PINTEREST_CLIENT_SECRET="paste_your_client_secret_here" \
    PINTEREST_REDIRECT_URI="https://pinterest-quotes-YOUR-NAME.herokuapp.com/auth/callback"
```

**Example with real values:**
```bash
heroku config:set \
    FLASK_ENV=production \
    SECRET_KEY="abc123def456..." \
    ENCRYPTION_KEY="gAAAAABm..." \
    PINTEREST_CLIENT_ID="123456789" \
    PINTEREST_CLIENT_SECRET="mysecretkey" \
    PINTEREST_REDIRECT_URI="https://pinterest-quotes-abhi.herokuapp.com/auth/callback"
```

**Verify all variables were set:**
```bash
heroku config
```

You should see all your variables listed.

### Step 6️⃣: Add PostgreSQL Database (Free)
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

Wait for it to complete. This creates a free database automatically.

**Verify database was created:**
```bash
heroku addons
```

You should see: `heroku-postgresql (hobby-dev)`

### Step 7️⃣: Deploy Code to Heroku
```bash
git push heroku main
```

**This will:**
- Upload your code
- Install dependencies
- Create database tables
- Start the app

**Wait for it to finish.** You should see:
```
remote: -----> Launching...
remote:        Released v1
remote:        https://pinterest-quotes-YOUR-NAME.herokuapp.com released to production
```

### Step 8️⃣: View Logs (Optional)
```bash
heroku logs --tail
```

This shows live logs. Press `Ctrl+C` to exit.

### Step 9️⃣: Open Your App
```bash
heroku open
```

Your app opens in browser at:
```
https://pinterest-quotes-YOUR-NAME.herokuapp.com
```

---

## ✅ Post-Deployment Steps

### Update Pinterest App Settings

1. Go to https://developers.pinterest.com/apps
2. Select your app
3. Go to "App Settings"
4. Update **Redirect URI** to:
   ```
   https://pinterest-quotes-YOUR-NAME.herokuapp.com/auth/callback
   ```
5. **Save changes**

### Test Your App

1. Open: `https://pinterest-quotes-YOUR-NAME.herokuapp.com`
2. Click **"Login with Pinterest"**
3. Authorize the app
4. You should see the dashboard

### Add Affiliate Links (in app)

1. Click **"Affiliate Links"** tab
2. Add your affiliate links:
   - Amazon Associates
   - ShareASale
   - Any other program

### Create Your First Post

1. Click **"Create Post"** tab
2. Enter quote text
3. Paste image URL (from Unsplash, Pexels, etc.)
4. Select affiliate link (optional)
5. Click **"Create Post"**
6. Go to **"My Posts"** to see it

---

## 🔧 Troubleshooting

### "Heroku CLI not found"
Download and install: https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli-x64.exe

### "Permission denied" when running commands
Use a terminal with admin privileges (cmd or PowerShell as Administrator)

### "OAuth callback failed"
- Make sure redirect URI in Heroku config **exactly matches** Pinterest app settings
- Include `https://` (not `http://`)
- No trailing slash

### App crashes on login
Check logs:
```bash
heroku logs --tail
```

Look for error messages and fix them.

### Database not working
Recreate database:
```bash
heroku pg:reset DATABASE
# Confirm when prompted
heroku restart
```

### Need to view/modify environment variables
```bash
# View all
heroku config

# View one
heroku config:get ENCRYPTION_KEY

# Change one
heroku config:set ENCRYPTION_KEY="new_value"

# Delete one
heroku config:unset ENCRYPTION_KEY
```

### Want to restart app
```bash
heroku restart
```

### Want to check app status
```bash
heroku status
```

---

## 📊 Monitoring

### View live logs
```bash
heroku logs --tail
```

### View recent logs (last 50 lines)
```bash
heroku logs --num=50
```

### View logs from specific timeframe
```bash
heroku logs --since 10m  # Last 10 minutes
heroku logs --since 1h   # Last 1 hour
```

### Check dyno status
```bash
heroku ps
```

---

## 💰 Costs

**Free tier includes:**
- ✓ 1000 dyno hours/month (always-on web dyno)
- ✓ 5 MB PostgreSQL database
- ✓ Free SSL/HTTPS
- ✓ Custom domain support

**Total cost: $0/month** ✅

(Scales up only if you upgrade to paid tiers)

---

## 🎉 You're Done!

Your Pinterest Quote Uploader is now live and ready to:
- Post quotes to Pinterest
- Include affiliate links
- Earn commissions
- Schedule posts
- Validate copyright

**Share your app:** `https://pinterest-quotes-YOUR-NAME.herokuapp.com`

---

## Quick Reference

```bash
# Login
heroku login

# Create app
heroku create pinterest-quotes-YOUR-NAME

# Set config
heroku config:set KEY=value

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Open app
heroku open

# Restart
heroku restart

# View config
heroku config
```

---

## Support

If stuck:
1. Check logs: `heroku logs --tail`
2. Read error message carefully
3. Google the error
4. Check docs/HEROKU_DEPLOY.md
5. Submit issue on GitHub

**Happy posting! 🚀📌**
