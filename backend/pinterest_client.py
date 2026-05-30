import os
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

PINTEREST_AUTH_URL = 'https://api.pinterest.com/oauth/'
PINTEREST_TOKEN_URL = 'https://api.pinterest.com/v5/oauth/token'
PINTEREST_API_BASE = 'https://api.pinterest.com/v5'

class PinterestOAuthClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state):
        """Generate the URL to redirect user to for authorization."""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'pins:read,pins:write,boards:read',
            'state': state
        }
        return f"{PINTEREST_AUTH_URL}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token and refresh token."""
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(PINTEREST_TOKEN_URL, data=payload)
        response.raise_for_status()
        
        data = response.json()
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_in': data.get('expires_in', 3600),
            'scope': data.get('scope'),
        }
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token."""
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(PINTEREST_TOKEN_URL, data=payload)
        response.raise_for_status()
        
        data = response.json()
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_in': data.get('expires_in', 3600),
        }
    
    def get_user_info(self, access_token):
        """Get authenticated user info from Pinterest."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            f'{PINTEREST_API_BASE}/user_account',
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_boards(self, access_token):
        """List user's Pinterest boards."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            f'{PINTEREST_API_BASE}/boards',
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_pin(self, access_token, board_id, image_url, description, title=None):
        """Create a pin on Pinterest."""
        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {
            'board_id': board_id,
            'media_source': {
                'source_type': 'image_url',
                'url': image_url
            },
            'description': description,
        }
        if title:
            payload['title'] = title
        
        response = requests.post(
            f'{PINTEREST_API_BASE}/pins',
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
