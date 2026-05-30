import os
import secrets
from flask import Flask, request, jsonify, send_file, redirect, session
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from dotenv import load_dotenv
from models import db, User
from pinterest_client import PinterestOAuthClient

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
db.init_app(app)

# Initialize Pinterest OAuth client
pinterest_client = PinterestOAuthClient(
    client_id=os.getenv('PINTEREST_CLIENT_ID'),
    client_secret=os.getenv('PINTEREST_CLIENT_SECRET'),
    redirect_uri=os.getenv('PINTEREST_REDIRECT_URI', 'http://localhost:5000/auth/callback')
)

@app.before_request
def create_tables():
    """Create tables if they don't exist."""
    with app.app_context():
        db.create_all()

# ==================== AUTH ENDPOINTS ====================

@app.route('/auth/login', methods=['GET'])
def login():
    """Start OAuth flow by redirecting to Pinterest."""
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    auth_url = pinterest_client.get_authorization_url(state)
    return redirect(auth_url)

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """Handle Pinterest OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': f'Authorization failed: {error}'}), 400
    
    if not code or state != session.get('oauth_state'):
        return jsonify({'error': 'Invalid state or missing code'}), 400
    
    try:
        # Exchange code for tokens
        token_data = pinterest_client.exchange_code_for_token(code)
        
        # Get user info
        user_info = pinterest_client.get_user_info(token_data['access_token'])
        pinterest_user_id = user_info.get('id')
        email = user_info.get('email', f"user_{pinterest_user_id}@pinterest.local")
        
        # Find or create user
        user = User.query.filter_by(pinterest_user_id=pinterest_user_id).first()
        if not user:
            user = User(pinterest_user_id=pinterest_user_id, email=email)
            db.session.add(user)
        
        # Store encrypted tokens
        user.set_tokens(
            token_data['access_token'],
            token_data.get('refresh_token'),
            token_data.get('expires_in')
        )
        db.session.commit()
        
        session['user_id'] = user.id
        
        # Redirect to frontend or dashboard
        return redirect(f"/dashboard?success=true&user_id={user.id}")
    
    except Exception as e:
        return jsonify({'error': f'Token exchange failed: {str(e)}'}), 500

@app.route('/auth/logout', methods=['POST'])
def logout():
    """Clear session and logout."""
    session.clear()
    return jsonify({'status': 'logged out'})

@app.route('/auth/user', methods=['GET'])
def get_user():
    """Get current authenticated user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'pinterest_user_id': user.pinterest_user_id,
        'created_at': user.created_at.isoformat()
    })

# ==================== IMAGE COMPOSITION ENDPOINTS ====================

@app.route('/compose', methods=['POST'])
def compose():
    """Create image with quote overlay."""
    data = request.json or {}
    quote = data.get('quote', 'Life is what happens when you\'re busy making other plans.')
    author = data.get('author', '')
    bg_color = data.get('bg_color', '#ffffff')

    img = Image.new('RGB', (1000, 1000), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('arial.ttf', 48)
    except Exception:
        font = ImageFont.load_default()

    text = f"\"{quote}\"\n\n{author}" if author else f"\"{quote}\""
    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(((1000-w)/2, (1000-h)/2), text, fill='black', font=font, align='center')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# ==================== POST ENDPOINTS ====================

@app.route('/posts', methods=['GET'])
def get_posts():
    """List user's posts."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    from models import Post
    posts = Post.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': p.id,
        'status': p.status,
        'scheduled_time': p.scheduled_time.isoformat() if p.scheduled_time else None,
        'created_at': p.created_at.isoformat()
    } for p in posts])

@app.route('/posts', methods=['POST'])
def create_post():
    """Create a new post (draft)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json or {}
    quote_text = data.get('quote')
    author = data.get('author')
    image_url = data.get('image_url')
    
    if not quote_text or not image_url:
        return jsonify({'error': 'quote and image_url required'}), 400
    
    from models import Quote, Image, Post
    
    # Create quote record
    quote = Quote(user_id=user_id, text=quote_text, author=author, source='user_input', license='unknown')
    db.session.add(quote)
    
    # Create image record
    image = Image(user_id=user_id, source_url=image_url, license='unknown')
    db.session.add(image)
    
    db.session.flush()  # Get IDs without committing
    
    # Create post (draft)
    post = Post(user_id=user_id, quote_id=quote.id, image_id=image.id, status='draft')
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'id': post.id,
        'status': post.status,
        'created_at': post.created_at.isoformat()
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
