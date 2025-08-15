"""
Google OAuth service for handling authorization code flow.
Manages OAuth flow, token verification, and user data extraction.
"""

import requests
import secrets
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import logging

from app.utils.config import settings

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Handles Google OAuth 2.0 authorization code flow"""
    
    # Google OAuth endpoints
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    # OAuth scopes
    SCOPES = ["openid", "email", "profile"]
    
    def __init__(self):
        """Initialize Google OAuth service with configuration"""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth configuration missing. Check GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI")
    
    def generate_auth_url(self) -> Tuple[str, str]:
        """
        Generate Google OAuth authorization URL and state parameter.
        
        Returns:
            Tuple of (auth_url, state) where state is used for CSRF protection
        """
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL parameters
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "response_type": "code",
            "state": state,
            "access_type": "offline",  # Get refresh token
            "prompt": "select_account",  # Always show account selection
        }
        
        auth_url = f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
        logger.info(f"Generated auth URL for state: {state}")
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        """
        Exchange authorization code for access token and ID token.
        
        Args:
            code: Authorization code from Google callback
            
        Returns:
            Dictionary containing tokens and user info
            
        Raises:
            Exception: If token exchange fails
        """
        try:
            # Prepare token exchange request
            token_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }
            
            # Exchange code for tokens
            logger.info("Exchanging authorization code for tokens")
            response = requests.post(
                self.TOKEN_URL,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if not response.ok:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise Exception(f"Token exchange failed: {response.text}")
            
            tokens = response.json()
            logger.info("Successfully exchanged code for tokens")
            
            # Verify and extract user info from ID token
            user_info = self.verify_id_token(tokens.get("id_token"))
            
            return {
                "access_token": tokens.get("access_token"),
                "id_token": tokens.get("id_token"),
                "refresh_token": tokens.get("refresh_token"),
                "user_info": user_info
            }
            
        except Exception as e:
            logger.error(f"Error in token exchange: {str(e)}")
            raise
    
    def verify_id_token(self, id_token_str: str) -> Dict:
        """
        Verify Google ID token using Google's public keys and extract user info.
        
        Args:
            id_token_str: JWT ID token from Google
            
        Returns:
            Dictionary containing verified user information
            
        Raises:
            Exception: If token verification fails
        """
        try:
            # Verify ID token using Google's public keys
            logger.info("Verifying ID token with Google public keys")
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify token audience matches our client ID
            if idinfo.get('aud') != self.client_id:
                raise ValueError("Invalid audience in ID token")
            
            # Extract user information
            user_info = {
                "google_id": idinfo.get("sub"),
                "email": idinfo.get("email"),
                "email_verified": idinfo.get("email_verified", False),
                "name": idinfo.get("name"),
                "given_name": idinfo.get("given_name"),
                "family_name": idinfo.get("family_name"),
                "picture": idinfo.get("picture"),
                "locale": idinfo.get("locale"),
            }
            
            logger.info(f"Successfully verified ID token for user: {user_info.get('email')}")
            return user_info
            
        except ValueError as e:
            logger.error(f"ID token verification failed: {str(e)}")
            raise Exception(f"Invalid ID token: {str(e)}")
        except Exception as e:
            logger.error(f"Error verifying ID token: {str(e)}")
            raise
    
    def get_user_info_from_access_token(self, access_token: str) -> Dict:
        """
        Get user information using access token (alternative method).
        
        Args:
            access_token: Access token from Google
            
        Returns:
            Dictionary containing user information
            
        Raises:
            Exception: If user info retrieval fails
        """
        try:
            logger.info("Fetching user info using access token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = requests.get(self.USERINFO_URL, headers=headers)
            
            if not response.ok:
                logger.error(f"User info request failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to get user info: {response.text}")
            
            user_info = response.json()
            logger.info(f"Successfully retrieved user info for: {user_info.get('email')}")
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise

# Create singleton instance
google_oauth_service = GoogleOAuthService()