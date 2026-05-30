import os
import secrets
from flask import Flask, request, jsonify, send_file, redirect, session
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from dotenv import load_dotenv
from models import db, User, Quote, Image as ImageModel, Post, Affiliate
from pinterest_client import PinterestOAuthClient
from image_processor import ImageComposer
from copyright_checker import CopyrightChecker

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

# ==================== AFFILIATE ENDPOINTS ====================

@app.route('/affiliates', methods=['GET'])
def get_affiliates():
    """List user's affiliate links."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    affiliates = Affiliate.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'url': a.url,
        'category': a.category,
        'created_at': a.created_at.isoformat()
    } for a in affiliates])

@app.route('/affiliates', methods=['POST'])
def add_affiliate():
    """Add a new affiliate link."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json or {}
    name = data.get('name')
    url = data.get('url')
    category = data.get('category')
    
    if not name or not url:
        return jsonify({'error': 'name and url required'}), 400
    
    affiliate = Affiliate(user_id=user_id, name=name, url=url, category=category)
    db.session.add(affiliate)
    db.session.commit()
    
    return jsonify({
        'id': affiliate.id,
        'name': affiliate.name,
        'url': affiliate.url,
        'category': affiliate.category
    }), 201

@app.route('/affiliates/<int:affiliate_id>', methods=['DELETE'])
def delete_affiliate(affiliate_id):
    """Deactivate an affiliate link."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    affiliate = Affiliate.query.filter_by(id=affiliate_id, user_id=user_id).first()
    if not affiliate:
        return jsonify({'error': 'Affiliate not found'}), 404
    
    affiliate.is_active = False
    db.session.commit()
    
    return jsonify({'status': 'deactivated'})

# ==================== IMAGE COMPOSITION ENDPOINTS ====================

@app.route('/compose', methods=['POST'])
def compose():
    """Create image with quote overlay."""
    data = request.json or {}
    quote = data.get('quote', 'Life is what happens when you\'re busy making other plans.')
    author = data.get('author', '')
    image_url = data.get('image_url', None)
    
    try:
        composer = ImageComposer()
        
        if image_url:
            img = composer.compose(image_url, quote, author)
        else:
            # Fallback: solid color background
            img = composer.compose(Image.new('RGB', (1000, 1000), (50, 50, 50)), quote, author)
        
        buf = composer.save_to_bytes(img)
        return send_file(buf, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': f'Image composition failed: {str(e)}'}), 400

# ==================== POST ENDPOINTS ====================

@app.route('/posts', methods=['GET'])
def get_posts():
    """List user's posts."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    posts = Post.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': p.id,
        'status': p.status,
        'scheduled_time': p.scheduled_time.isoformat() if p.scheduled_time else None,
        'created_at': p.created_at.isoformat()
    } for p in posts])

@app.route('/posts', methods=['POST'])
def create_post():
    """Create a new post (draft) with copyright validation."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json or {}
    quote_text = data.get('quote')
    author = data.get('author')
    image_url = data.get('image_url')
    affiliate_id = data.get('affiliate_id')
    is_user_image = data.get('is_user_image', False)
    
    if not quote_text or not image_url:
        return jsonify({'error': 'quote and image_url required'}), 400
    
    # Validate affiliate exists if provided
    if affiliate_id:
        affiliate = Affiliate.query.filter_by(id=affiliate_id, user_id=user_id).first()
        if not affiliate:
            return jsonify({'error': 'Affiliate not found'}), 404
    
    # Validate copyright
    validation = CopyrightChecker.validate_post(
        quote_text, author, image_url, image_url, is_user_image
    )
    
    # Create quote record
    quote = Quote(
        user_id=user_id,
        text=quote_text,
        author=author,
        source=image_url if not is_user_image else 'user_input',
        license=validation['quote_check']['license'],
        review_status=validation['quote_check']['status']
    )
    db.session.add(quote)
    
    # Create image record
    image = ImageModel(
        user_id=user_id,
        source_url=image_url if not is_user_image else None,
        local_path=image_url if is_user_image else None,
        license=validation['image_check']['license'],
        review_status=validation['image_check']['status']
    )
    db.session.add(image)
    
    db.session.flush()  # Get IDs without committing
    
    # Create post (draft)
    post = Post(user_id=user_id, quote_id=quote.id, image_id=image.id, status='draft', affiliate_id=affiliate_id)
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'id': post.id,
        'status': post.status,
        'created_at': post.created_at.isoformat(),
        'validation': {
            'can_post': validation['can_post'],
            'overall_status': validation['overall_status'],
            'messages': validation['messages']
        }
    }), 201

@app.route('/posts/<int:post_id>/post', methods=['POST'])
def post_to_pinterest(post_id):
    """Post to Pinterest immediately."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    post = Post.query.filter_by(id=post_id, user_id=user_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    if post.status != 'draft':
        return jsonify({'error': f'Can only post from draft status, current: {post.status}'}), 400
    
    data = request.json or {}
    board_id = data.get('board_id')
    
    if not board_id:
        return jsonify({'error': 'board_id required'}), 400
    
    try:
        # Get user and refresh token if needed
        user = User.query.get(user_id)
        access_token = user.get_access_token()
        
        # Get quote and image
        quote = Quote.query.get(post.quote_id)
        image = ImageModel.query.get(post.image_id)
        
        # Check if content is approved
        if quote.review_status != 'approved' or image.review_status != 'approved':
            return jsonify({
                'error': 'Content requires manual review before posting',
                'quote_status': quote.review_status,
                'image_status': image.review_status
            }), 403
        
        # Compose image
        composer = ImageComposer()
        composed_img = composer.compose(image.source_url or image.local_path, quote.text, quote.author)
        
        # Build description with affiliate link
        pin_description = quote.text
        if quote.author:
            pin_description += f"\n\n— {quote.author}"
        
        if post.affiliate_id:
            affiliate = Affiliate.query.get(post.affiliate_id)
            if affiliate:
                pin_description += f"\n\n🔗 Learn more: {affiliate.url}"
        
        # Call Pinterest API
        pin_response = pinterest_client.create_pin(
            access_token=access_token,
            board_id=board_id,
            image_url=image.source_url or image.local_path,
            description=pin_description,
            title=quote.text[:50]
        )
        
        # Update post record
        from datetime import datetime
        post.pin_id = pin_response.get('id')
        post.board_id = board_id
        post.status = 'posted'
        post.posted_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'posted',
            'pin_id': pin_response.get('id'),
            'pin_url': pin_response.get('url'),
            'post_id': post.id
        }), 200
    
    except Exception as e:
        post.status = 'failed'
        post.error_message = str(e)
        db.session.commit()
        return jsonify({'error': f'Failed to post: {str(e)}'}), 500

@app.route('/boards', methods=['GET'])
def get_boards():
    """List user's Pinterest boards."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user = User.query.get(user_id)
        access_token = user.get_access_token()
        boards = pinterest_client.get_boards(access_token)
        return jsonify(boards)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch boards: {str(e)}'}), 500

# ==================== ADMIN REVIEW ENDPOINTS ====================

@app.route('/admin/flagged', methods=['GET'])
def get_flagged_posts():
    """List flagged posts pending review."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    flagged_quotes = Quote.query.filter_by(user_id=user_id, review_status='pending_review').all()
    flagged_images = ImageModel.query.filter_by(user_id=user_id, review_status='pending_review').all()
    
    return jsonify({
        'flagged_quotes': [{
            'id': q.id,
            'text': q.text,
            'author': q.author,
            'source': q.source,
            'license': q.license
        } for q in flagged_quotes],
        'flagged_images': [{
            'id': i.id,
            'source_url': i.source_url,
            'license': i.license
        } for i in flagged_images]
    })

@app.route('/admin/quotes/<int:quote_id>/approve', methods=['POST'])
def approve_quote(quote_id):
    """Approve a flagged quote."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    quote = Quote.query.filter_by(id=quote_id, user_id=user_id).first()
    if not quote:
        return jsonify({'error': 'Quote not found'}), 404
    
    quote.review_status = 'approved'
    db.session.commit()
    return jsonify({'status': 'approved'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
