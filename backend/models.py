from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import os

db = SQLAlchemy()

# Initialize encryption cipher from env or generate new key
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', None)
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY must be set in environment")

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_token(token):
    """Encrypt a token for storage."""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """Decrypt a token from storage."""
    return cipher_suite.decrypt(encrypted_token.encode()).decode()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    pinterest_user_id = db.Column(db.String(255), unique=True, nullable=False)
    encrypted_access_token = db.Column(db.Text, nullable=False)
    encrypted_refresh_token = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def set_tokens(self, access_token, refresh_token=None, expires_in=None):
        """Securely store access and refresh tokens."""
        self.encrypted_access_token = encrypt_token(access_token)
        if refresh_token:
            self.encrypted_refresh_token = encrypt_token(refresh_token)
        if expires_in:
            from datetime import datetime, timedelta
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    def get_access_token(self):
        """Retrieve and decrypt access token."""
        return decrypt_token(self.encrypted_access_token)
    
    def get_refresh_token(self):
        """Retrieve and decrypt refresh token."""
        if self.encrypted_refresh_token:
            return decrypt_token(self.encrypted_refresh_token)
        return None

class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(500), nullable=True)  # URL or 'user_input'
    license = db.Column(db.String(50), default='unknown')  # CC0, public_domain, copyrighted, unknown
    review_status = db.Column(db.String(20), default='pending_review')  # approved, pending_review, rejected
    created_at = db.Column(db.DateTime, default=db.func.now())

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    local_path = db.Column(db.String(500), nullable=True)
    license = db.Column(db.String(50), default='unknown')  # CC0, permissive_stock, user_uploaded, unknown
    review_status = db.Column(db.String(20), default='pending_review')
    created_at = db.Column(db.DateTime, default=db.func.now())

class Affiliate(db.Model):
    __tablename__ = 'affiliates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)  # e.g., "Amazon Associates", "ShareASale"
    url = db.Column(db.String(500), nullable=False)  # Affiliate link
    category = db.Column(db.String(100), nullable=True)  # e.g., "books", "wellness", "lifestyle"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliates.id'), nullable=True)  # Optional affiliate link
    pin_id = db.Column(db.String(255), nullable=True)  # Pinterest Pin ID after posting
    board_id = db.Column(db.String(255), nullable=True)  # Pinterest Board ID
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, posted, failed
    scheduled_time = db.Column(db.DateTime, nullable=True)
    posted_time = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
