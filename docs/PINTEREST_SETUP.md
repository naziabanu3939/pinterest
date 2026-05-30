# Pinterest App Registration Guide

## Steps to Register Your Pinterest App

1. **Go to Pinterest Developer Portal**
   - Visit: https://developers.pinterest.com/
   - Sign in with your Pinterest business account

2. **Create New App**
   - Click "Create app"
   - App name: e.g., "Life Quotes Uploader"
   - App purpose: Select "I am a developer building an app for a business"
   - Use case: Content creation tool
   - Accept terms and continue

3. **Configure App Details**
   - **Redirect URI**: `http://localhost:5000/auth/callback` (dev) or your production domain
   - **Permissions**: Request `pins:write`, `pins:read`, `boards:read`

4. **Get Credentials**
   - Copy **Client ID**
   - Copy **Client Secret** (keep safe!)

5. **Store in Environment**
   ```bash
   export PINTEREST_CLIENT_ID="your_client_id_here"
   export PINTEREST_CLIENT_SECRET="your_client_secret_here"
   export PINTEREST_REDIRECT_URI="http://localhost:5000/auth/callback"
   ```

## Important Notes

- **Client Secret is sensitive**: Never commit to version control or share publicly
- **Redirect URI must match exactly**: Including protocol (http/https) and path
- Production: Use HTTPS for redirect URI
- Test app first in development before deploying

## Verification

Once registered, you can verify by visiting:
```
https://api.pinterest.com/oauth/?
  client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &response_type=code
  &scope=pins:read,pins:write,boards:read
```

This should show Pinterest login/authorize screen.
