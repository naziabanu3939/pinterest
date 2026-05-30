# Pinterest Life-Quotes Uploader with Affiliate Marketing

Automatically create and post aesthetic life quote images to Pinterest with affiliate links. Earn commissions while sharing inspiration.

**Features:**
- 📌 Post quotes & images directly to Pinterest
- 💰 Include affiliate links (Amazon Associates, ShareASale, etc.)
- 🔒 Copyright-safe: Validates all content before posting
- ⏰ Schedule posts for later
- 🎨 Auto-compose beautiful quote images
- 👤 OAuth2 authentication with Pinterest
- ☁️ Deploy to Heroku in 5 minutes

## Quick Start (Local)

```bash
git clone https://github.com/naziabanu3939/pinterest.git
cd pinterest

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Create .env file
cat > backend/.env << EOF
FLASK_ENV=development
SECRET_KEY=your_random_secret_key
ENCRYPTION_KEY=your_encryption_key_from_above
PINTEREST_CLIENT_ID=your_pinterest_client_id
PINTEREST_CLIENT_SECRET=your_pinterest_client_secret
PINTEREST_REDIRECT_URI=http://localhost:5000/auth/callback
DATABASE_URL=sqlite:///app.db
EOF

# Run
cd backend
python app.py
```

Then open: http://localhost:5000

## Deploy to Heroku (Free!)

See **docs/HEROKU_DEPLOY.md** for step-by-step instructions.

**5-minute deployment:**
```bash
heroku login
heroku create your-app-name
heroku config:set ENCRYPTION_KEY="your_key" ...  # Set env vars
git push heroku main
heroku open
```

## How to Use

1. **Login**: Click "Login with Pinterest" → Authorize app
2. **Add Affiliate Links**: Go to "Affiliate Links" tab and add your:
   - Amazon Associates link
   - ShareASale links
   - Any commission-based URL
3. **Create Posts**:
   - Enter quote + author
   - Select image from CC0 sources (Unsplash, Pexels, etc.)
   - Select affiliate link (optional)
   - Choose Pinterest board
   - Post immediately or schedule for later
4. **Track**: Monitor posts in "My Posts" tab

## Affiliate Link Examples

- **Amazon Associates**: `https://amazon.com?tag=yourcode-20`
- **ShareASale**: `https://www.shareasale.com/r.cfm?u=USERID&i=ITEMID`
- **Bluehost**: Your referral link
- **Skillshare**: Your referral link

## Copyright Safety

- ✓ **Approved**: User uploads, CC0 images (Unsplash, Pexels, Pixabay)
- ✓ **Approved**: Public-domain quotes (Shakespeare, Aristotle, etc.)
- ⚠️ **Flagged**: Unknown sources → Manual review required
- ❌ **Rejected**: Known copyrighted sources (Getty, Shutterstock)

## Technology Stack

- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **Frontend**: HTML/CSS/JavaScript (single-page app)
- **Authentication**: OAuth 2.0 (Pinterest)
- **Image Processing**: Pillow
- **Scheduling**: APScheduler
- **Hosting**: Heroku (free tier available)

## Documentation

- **DESIGN.md** — Architecture & system design
- **docs/HEROKU_DEPLOY.md** — Deploy to Heroku
- **docs/DEPLOYMENT.md** — Other deployment options
- **docs/PINTEREST_SETUP.md** — Register Pinterest app

## Environment Variables

```
FLASK_ENV=production
SECRET_KEY=random_key_here
ENCRYPTION_KEY=fernet_key_from_cryptography
DATABASE_URL=postgresql://...  # Heroku sets this
PINTEREST_CLIENT_ID=your_client_id
PINTEREST_CLIENT_SECRET=your_client_secret
PINTEREST_REDIRECT_URI=https://your-app.herokuapp.com/auth/callback
```

## API Endpoints

- `GET /auth/user` — Current user
- `POST /auth/login` — Start OAuth
- `POST /auth/logout` — Logout
- `GET /affiliates` — List affiliate links
- `POST /affiliates` — Add affiliate link
- `POST /posts` — Create new post
- `POST /posts/{id}/post` — Post to Pinterest
- `GET /boards` — List Pinterest boards

## Testing

```bash
cd backend
python -m unittest tests.py -v
```

## Troubleshooting

**ENCRYPTION_KEY not set?**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
export ENCRYPTION_KEY="your_key_here"
```

**Pinterest OAuth callback fails?**
- Verify redirect URI matches exactly (http vs https, domain, port)
- Check app registered on https://developers.pinterest.com

**Posts not posting?**
- Check content is approved (no pending review)
- Verify board_id exists
- Check logs: `heroku logs --tail`

## License

MIT License — Feel free to fork and customize!

## Support

- Issues: GitHub Issues tab
- Docs: See docs/ folder
- Questions: Submit an issue with [QUESTION] tag

---

**Made with ❤️ for content creators and affiliate marketers**

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
