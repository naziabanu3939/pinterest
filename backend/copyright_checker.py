from datetime import datetime
from urllib.parse import urlparse

# List of CC0/permissive stock image sources
APPROVED_IMAGE_SOURCES = [
    'unsplash.com',
    'pexels.com',
    'pixabay.com',
    'freeimages.com',
    'stocksnap.io'
]

# Known copyrighted image sources (rejected)
REJECTED_IMAGE_SOURCES = [
    'getty.com',
    'shutterstock.com',
    'istock.com',
    'alamy.com',
    'dreamstime.com'
]

class CopyrightChecker:
    """Validate quotes and images for copyright compliance."""
    
    @staticmethod
    def check_image_license(source_url, is_user_uploaded=False):
        """Check image source for license and copyright compliance.
        
        Returns:
            {
                'status': 'approved' | 'pending_review' | 'rejected',
                'license': 'CC0' | 'user_uploaded' | 'unknown' | 'copyrighted',
                'reason': explanation string
            }
        """
        if is_user_uploaded:
            return {
                'status': 'approved',
                'license': 'user_uploaded',
                'reason': 'User-uploaded image (explicit ownership claim)'
            }
        
        if not source_url:
            return {
                'status': 'pending_review',
                'license': 'unknown',
                'reason': 'No source URL provided'
            }
        
        domain = urlparse(source_url).netloc.lower()
        
        # Check rejected list first
        for rejected_domain in REJECTED_IMAGE_SOURCES:
            if rejected_domain in domain:
                return {
                    'status': 'rejected',
                    'license': 'copyrighted',
                    'reason': f'Image source {rejected_domain} is known to have strict copyright restrictions'
                }
        
        # Check approved list
        for approved_domain in APPROVED_IMAGE_SOURCES:
            if approved_domain in domain:
                return {
                    'status': 'approved',
                    'license': 'CC0',
                    'reason': f'Image from {approved_domain} (CC0/Public Domain)'
                }
        
        # Unknown source
        return {
            'status': 'pending_review',
            'license': 'unknown',
            'reason': 'Image source is not recognized. Manual review required.'
        }
    
    @staticmethod
    def check_quote_license(quote_text, author=None, source_url=None):
        """Check quote for copyright compliance.
        
        Returns:
            {
                'status': 'approved' | 'pending_review' | 'rejected',
                'license': 'public_domain' | 'user_input' | 'unknown',
                'reason': explanation string,
                'suggestion': optional suggestion for user
            }
        """
        # If quote is attributed to user directly, assume user input
        if author and author.lower() == 'anonymous':
            return {
                'status': 'approved',
                'license': 'user_input',
                'reason': 'Anonymous quote (treated as user-originated)',
                'suggestion': None
            }
        
        # Check if source is provided and reliable
        if source_url:
            domain = urlparse(source_url).netloc.lower()
            
            # Approved quote sources
            if 'goodreads.com' in domain or 'brainyquote.com' in domain:
                return {
                    'status': 'pending_review',
                    'license': 'unknown',
                    'reason': 'Quote from aggregator site (may have copyright restrictions)',
                    'suggestion': 'Verify original source before posting'
                }
        
        # Known public domain authors (very basic list)
        public_domain_authors = [
            'shakespeare',
            'aristotle',
            'plato',
            'confucius',
            'oscar wilde',
            'mark twain',
            'jane austen',
            'charles dickens',
            'emily dickinson'
        ]
        
        if author:
            author_lower = author.lower()
            for pd_author in public_domain_authors:
                if pd_author in author_lower:
                    return {
                        'status': 'approved',
                        'license': 'public_domain',
                        'reason': f'Quote from {author} (public domain author)',
                        'suggestion': None
                    }
        
        # Default: flag for manual review
        return {
            'status': 'pending_review',
            'license': 'unknown',
            'reason': 'Quote source/license cannot be automatically verified',
            'suggestion': 'Ensure you have permission to use this quote or it is in the public domain'
        }
    
    @staticmethod
    def validate_post(quote_text, author=None, quote_source=None, 
                      image_url=None, is_user_image=False):
        """Validate entire post (quote + image) for copyright compliance.
        
        Returns:
            {
                'can_post': bool,
                'quote_check': {...},
                'image_check': {...},
                'overall_status': 'approved' | 'pending_review' | 'rejected',
                'messages': [list of warnings/errors]
            }
        """
        messages = []
        
        # Check quote
        quote_check = CopyrightChecker.check_quote_license(quote_text, author, quote_source)
        if quote_check['status'] == 'rejected':
            messages.append(f"❌ Quote: {quote_check['reason']}")
        elif quote_check['status'] == 'pending_review':
            messages.append(f"⚠️ Quote: {quote_check['reason']}")
        else:
            messages.append(f"✓ Quote: {quote_check['reason']}")
        
        # Check image
        image_check = CopyrightChecker.check_image_license(image_url, is_user_image)
        if image_check['status'] == 'rejected':
            messages.append(f"❌ Image: {image_check['reason']}")
        elif image_check['status'] == 'pending_review':
            messages.append(f"⚠️ Image: {image_check['reason']}")
        else:
            messages.append(f"✓ Image: {image_check['reason']}")
        
        # Determine overall status
        overall_statuses = [quote_check['status'], image_check['status']]
        
        if 'rejected' in overall_statuses:
            overall_status = 'rejected'
            can_post = False
        elif 'pending_review' in overall_statuses:
            overall_status = 'pending_review'
            can_post = False  # Require user to confirm before posting
        else:
            overall_status = 'approved'
            can_post = True
        
        return {
            'can_post': can_post,
            'quote_check': quote_check,
            'image_check': image_check,
            'overall_status': overall_status,
            'messages': messages
        }
