web: cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app
worker: cd backend && python -m scheduler:start_scheduler
release: cd backend && python -c "from app import app, db; app.app_context().push(); db.create_all()"
