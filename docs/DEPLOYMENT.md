# Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- Pinterest Business Account (for OAuth)
- Git

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/naziabanu3939/pinterest.git
   cd pinterest
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Generate Encryption Key**
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

5. **Create .env File**
   ```
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   ENCRYPTION_KEY=your_encryption_key_from_step_4
   PINTEREST_CLIENT_ID=your_client_id
   PINTEREST_CLIENT_SECRET=your_client_secret
   PINTEREST_REDIRECT_URI=http://localhost:5000/auth/callback
   DATABASE_URL=sqlite:///app.db
   ```

6. **Run Flask App**
   ```bash
   cd backend
   python app.py
   ```
   
   App will be available at: http://localhost:5000

7. **Open Frontend**
   - Copy `frontend/index.html` path or serve it via a simple HTTP server
   - Or use: `python -m http.server 8000` in the frontend directory

### Running Tests

```bash
cd backend
python -m unittest tests.py -v
```

---

## Production Deployment

### Option 1: Heroku

1. **Install Heroku CLI**
   ```bash
   curl https://cli.heroku.com/install.sh | sh
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set ENCRYPTION_KEY=your_key
   heroku config:set SECRET_KEY=your_secret
   heroku config:set PINTEREST_CLIENT_ID=your_id
   heroku config:set PINTEREST_CLIENT_SECRET=your_secret
   heroku config:set PINTEREST_REDIRECT_URI=https://your-app-name.herokuapp.com/auth/callback
   ```

4. **Add Procfile** (already in repo)
   ```
   web: cd backend && python app.py
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 2: AWS

1. **Create Elastic Beanstalk Application**
   - Use Python 3.9 runtime
   - Set environment variables in EB console

2. **Deploy**
   ```bash
   eb init
   eb create pinterest-env
   eb deploy
   ```

### Option 3: Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "backend/app.py"]
   ```

2. **Build and Run**
   ```bash
   docker build -t pinterest .
   docker run -p 5000:5000 --env-file .env pinterest
   ```

---

## Database Migration

### Create Tables

The app auto-creates tables on first run. To manually initialize:

```python
from app import app, db
with app.app_context():
    db.create_all()
```

### Backup Database

```bash
# SQLite
cp app.db app.db.backup

# PostgreSQL (production)
pg_dump $DATABASE_URL > backup.sql
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use HTTPS in production
- [ ] Store `ENCRYPTION_KEY` and `PINTEREST_CLIENT_SECRET` in a secrets manager
- [ ] Enable CORS only for trusted domains
- [ ] Use environment-specific database URLs
- [ ] Set `FLASK_ENV=production`
- [ ] Enable rate limiting on all endpoints
- [ ] Regular security audits and dependency updates

---

## Monitoring & Logs

### Local Logs
```bash
tail -f app.log
```

### Heroku Logs
```bash
heroku logs --tail
```

### Key Metrics to Monitor
- Failed Pinterest API calls
- Scheduler job execution status
- User authentication failures
- Database performance

---

## Troubleshooting

### "ENCRYPTION_KEY must be set"
- Generate key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- Set in .env: `ENCRYPTION_KEY=your_key_here`

### OAuth Callback Error
- Verify `PINTEREST_REDIRECT_URI` matches in:
  - Pinterest Developer App settings
  - .env file
  - Actual redirect URL (http vs https, domain, port)

### Image Composition Fails
- Ensure font files are available
- Check file permissions
- Verify image URL is accessible

### Database Locked
- Restart Flask app
- If using SQLite in production, migrate to PostgreSQL

---

## Support

- Check DESIGN.md for architecture details
- Review docs/PINTEREST_SETUP.md for OAuth setup
- See README.md for quickstart
