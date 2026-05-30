from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import db, Post, User, Quote, Image as ImageModel
from pinterest_client import PinterestOAuthClient
import os
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def post_scheduled_pins():
    """Background job to post any scheduled pins whose time has come."""
    from app import app
    
    with app.app_context():
        # Find all scheduled posts whose scheduled_time is now or in the past
        now = datetime.utcnow()
        scheduled_posts = Post.query.filter(
            Post.status == 'scheduled',
            Post.scheduled_time <= now
        ).all()
        
        pinterest_client = PinterestOAuthClient(
            client_id=os.getenv('PINTEREST_CLIENT_ID'),
            client_secret=os.getenv('PINTEREST_CLIENT_SECRET'),
            redirect_uri=os.getenv('PINTEREST_REDIRECT_URI', 'http://localhost:5000/auth/callback')
        )
        
        for post in scheduled_posts:
            try:
                user = User.query.get(post.user_id)
                access_token = user.get_access_token()
                
                quote = Quote.query.get(post.quote_id)
                image = ImageModel.query.get(post.image_id)
                
                # Compose image
                from image_processor import ImageComposer
                composer = ImageComposer()
                composed_img = composer.compose(image.source_url or image.local_path, quote.text, quote.author)
                
                # Prepare description
                pin_description = quote.text
                if quote.author:
                    pin_description += f"\n\n— {quote.author}"
                
                # Call Pinterest API
                pin_response = pinterest_client.create_pin(
                    access_token=access_token,
                    board_id=post.board_id,
                    image_url=image.source_url or image.local_path,
                    description=pin_description,
                    title=quote.text[:50]
                )
                
                # Update post
                post.pin_id = pin_response.get('id')
                post.status = 'posted'
                post.posted_time = now
                db.session.commit()
                
                logger.info(f"Posted scheduled pin {post.id} to Pinterest")
            
            except Exception as e:
                post.status = 'failed'
                post.error_message = str(e)
                db.session.commit()
                logger.error(f"Failed to post scheduled pin {post.id}: {str(e)}")

def start_scheduler(app):
    """Initialize and start the scheduler."""
    scheduler.add_job(
        post_scheduled_pins,
        'interval',
        minutes=5,  # Check every 5 minutes
        id='post_scheduled_pins',
        replace_existing=True
    )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
