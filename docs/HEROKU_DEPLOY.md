# Deploy to Heroku in 5 Minutes

## Prerequisites
- Heroku account (free tier available at https://www.heroku.com)
- Git installed
- Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli

## Step 1: Install Heroku CLI

```bash
# Windows
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku

# Or download directly: https://cli-assets.heroku.com/heroku-cli/channels/stable/heroku-cli-x64.exe (Windows)
```

## Step 2: Login to Heroku

```bash
heroku login
```

This opens a browser. Sign in or create a free Heroku account.

## Step 3: Create Heroku App

```bash
cd pinterest  # Navigate to repo
heroku create pinterest-quotes  # Replace with unique app name
```

This creates an app and adds `heroku` as a remote to git.

## Step 4: Set Environment Variables

```bash
# Generate encryption key first
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set all required env vars
heroku config:set ENCRYPTION_KEY="your_encryption_key_here"
heroku config:set SECRET_KEY="your_random_secret_key_here"
heroku config:set PINTEREST_CLIENT_ID="your_pinterest_client_id"
heroku config:set PINTEREST_CLIENT_SECRET="your_pinterest_client_secret"
heroku config:set PINTEREST_REDIRECT_URI="https://pinterest-quotes.herokuapp.com/auth/callback"
heroku config:set FLASK_ENV=production
```

**Note:** Replace `pinterest-quotes` with your actual app name.

## Step 5: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:hobby-dev

# This sets DATABASE_URL automatically
heroku config  # Verify it's set
```

## Step 6: Deploy Code

```bash
git push heroku main
```

Wait for deployment to finish. You'll see:
```
remote: Compiling Python app
remote: Installing dependencies
...
remote: -----> Launching...
remote:        Released v1
remote:        https://pinterest-quotes.herokuapp.com released to production
```

## Step 7: Verify Deployment

```bash
heroku open  # Opens your app in browser
heroku logs --tail  # Watch live logs
```

## Step 8: Setup Pinterest App (if not done already)

1. Go to https://developers.pinterest.com/
2. Register an app
3. Add Redirect URI: `https://your-app-name.herokuapp.com/auth/callback`
4. Copy Client ID and Client Secret
5. Add to Heroku config (see Step 4)

---

## Usage After Deployment

1. **Access your app**: `https://your-app-name.herokuapp.com`
2. **Login with Pinterest**: Click "Login with Pinterest" button
3. **Create posts** with affiliate links
4. **Post to Pinterest** immediately or schedule for later

---

## Troubleshooting

### "ENCRYPTION_KEY must be set"
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
heroku config:set ENCRYPTION_KEY="your_key_here"
```

### OAuth Callback Error
Verify redirect URI matches exactly:
```bash
heroku config:get PINTEREST_REDIRECT_URI
# Should match: https://your-app-name.herokuapp.com/auth/callback
```

### App Crashes
Check logs:
```bash
heroku logs --tail
```

### Clear Database
```bash
heroku pg:reset DATABASE  # WARNING: Deletes all data!
```

---

## Costs

**Free tier includes:**
- 1000 hours/month dyno time (always-on) ✓
- 5 MB PostgreSQL database ✓
- 1 free app ✓

**Pricing if you scale:**
- Standard dyno: $7/month (more reliable)
- PostgreSQL Standard: $50/month (for production)

For personal use, **free tier is perfectly fine** for this app.

---

## Next Steps

- Monitor your posts at: `https://your-app-name.herokuapp.com/auth/user`
- Manage affiliates in dashboard
- Track pins on Pinterest

Happy posting! 🎉
