import unittest
from app import app, db
from models import User, Quote, Image, Post
from copyright_checker import CopyrightChecker
import os

class TestApp(unittest.TestCase):
    def setUp(self):
        """Set up test database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        
        with app.app_context():
            db.create_all()
            self.client = app.test_client()
    
    def tearDown(self):
        """Cleanup after tests."""
        with app.app_context():
            db.drop_all()
    
    def test_compose_endpoint(self):
        """Test image composition endpoint."""
        with app.app_context():
            response = self.client.post('/compose', json={
                'quote': 'Test quote',
                'author': 'Test Author',
                'bg_color': '#ffffff'
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'image/png')
    
    def test_copyright_checker_public_domain(self):
        """Test copyright checker with public domain author."""
        result = CopyrightChecker.check_quote_license('To be or not to be', 'Shakespeare')
        self.assertEqual(result['status'], 'approved')
        self.assertEqual(result['license'], 'public_domain')
    
    def test_copyright_checker_approved_image_source(self):
        """Test copyright checker with approved image source."""
        result = CopyrightChecker.check_image_license('https://unsplash.com/photos/test')
        self.assertEqual(result['status'], 'approved')
        self.assertEqual(result['license'], 'CC0')
    
    def test_copyright_checker_rejected_image_source(self):
        """Test copyright checker with rejected image source."""
        result = CopyrightChecker.check_image_license('https://getty.com/photos/test')
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['license'], 'copyrighted')
    
    def test_copyright_checker_user_uploaded_image(self):
        """Test copyright checker with user-uploaded image."""
        result = CopyrightChecker.check_image_license('', is_user_uploaded=True)
        self.assertEqual(result['status'], 'approved')
        self.assertEqual(result['license'], 'user_uploaded')
    
    def test_validate_post_approved(self):
        """Test full post validation (both approved)."""
        result = CopyrightChecker.validate_post(
            'To be or not to be',
            'Shakespeare',
            'https://unsplash.com/photos/test'
        )
        self.assertEqual(result['overall_status'], 'approved')
        self.assertTrue(result['can_post'])
    
    def test_validate_post_rejected(self):
        """Test full post validation with rejected content."""
        result = CopyrightChecker.validate_post(
            'Modern copyrighted quote',
            'Some Author',
            'https://getty.com/photos/test'
        )
        self.assertEqual(result['overall_status'], 'rejected')
        self.assertFalse(result['can_post'])

if __name__ == '__main__':
    unittest.main()
