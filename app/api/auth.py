from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import logging

from app.utils.database import get_db
from app.models.models import User, UserProfile, UserSubscription, UserSettings, SubscriptionTier
from app.models.user_schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    GoogleAuthRequest, UserProfileCreate, UserProfileResponse, UserProfileUpdate,
    CompleteUserProfile, UserSettingsResponse
)
from app.auth.dependencies import (
    hash_password, authenticate_user, create_access_token,
    get_current_user, get_current_active_user
)
from app.utils.config import settings
from app.services.google_oauth import google_oauth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/register", response_model=TokenResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create user profile
    profile = UserProfile(user_id=db_user.id)
    db.add(profile)
    
    # Create user subscription (free tier)
    subscription = UserSubscription(
        user_id=db_user.id,
        tier=SubscriptionTier.FREE
    )
    db.add(subscription)
    
    # Create user settings with defaults
    settings = UserSettings(user_id=db_user.id)
    db.add(settings)
    
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours in seconds
        user=UserResponse.from_orm(db_user)
    )

@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login a user."""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours in seconds
        user=UserResponse.from_orm(user)
    )

@router.post("/google", response_model=TokenResponse)
def google_auth(google_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth."""
    
    try:
        # Extract user information from request
        email = google_data.email
        name = google_data.name
        google_id = google_data.google_id
        picture = google_data.picture
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Update last login
            existing_user.last_login = datetime.utcnow()
            db.commit()
            user = existing_user
        else:
            # Create new user from Google account
            username = email.split('@')[0]  # Use email prefix as username
            
            # Ensure username is unique
            counter = 1
            original_username = username
            while db.query(User).filter(User.username == username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create new user
            db_user = User(
                email=email,
                username=username,
                full_name=name,
                hashed_password="",  # No password for Google users
                is_active=True,
                is_verified=True  # Google accounts are pre-verified
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Create user profile with Google info
            profile = UserProfile(
                user_id=db_user.id,
                avatar_url=picture if picture else None
            )
            db.add(profile)
            
            # Create user subscription (free tier)
            subscription = UserSubscription(
                user_id=db_user.id,
                tier=SubscriptionTier.FREE
            )
            db.add(subscription)
            
            # Create user settings with defaults
            user_settings = UserSettings(user_id=db_user.id)
            db.add(user_settings)
            
            db.commit()
            user = db_user
        
        # Create access token
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,  # 24 hours in seconds
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.get("/me", response_model=CompleteUserProfile)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the current user's complete profile."""
    # Load all related data
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == current_user.id).first()
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    # Create default records if they don't exist
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    if not subscription:
        subscription = UserSubscription(user_id=current_user.id, tier=SubscriptionTier.FREE)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return CompleteUserProfile(
        user=UserResponse.from_orm(current_user),
        profile=UserProfileResponse.from_orm(profile),
        subscription=subscription,
        progress=[],  # Will be populated when progress tracking is implemented
        recent_achievements=[],  # Will be populated when achievements are implemented
        settings=UserSettingsResponse.from_orm(settings),
        active_study_session=None  # Will be populated when study sessions are implemented
    )

@router.put("/profile", response_model=UserProfileResponse)
def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update profile fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    
    return UserProfileResponse.from_orm(profile)

@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout the current user."""
    # In a stateless JWT system, logout is typically handled client-side
    # by removing the token. This endpoint exists for completeness.
    return {"message": "Successfully logged out"}

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]

# Google OAuth Authorization Code Flow Endpoints

@router.get("/google")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.
    Redirects user to Google authorization page.
    """
    try:
        # Generate authorization URL with state parameter for CSRF protection
        auth_url, state = google_oauth_service.generate_auth_url()
        
        # Store state in session for CSRF protection
        request.session["oauth_state"] = state
        
        logger.info(f"Redirecting to Google OAuth with state: {state}")
        
        # Redirect user to Google authorization page
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate Google authentication")

@router.get("/google/callback")
async def google_callback(
    request: Request, 
    code: str = None, 
    state: str = None, 
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchanges authorization code for tokens and creates/updates user session.
    """
    try:
        # Check for OAuth errors from Google
        if error:
            logger.error(f"Google OAuth error: {error}")
            # Redirect to frontend with error parameter
            return RedirectResponse(url="http://localhost:5000/login?error=oauth_error")
        
        # Validate required parameters
        if not code or not state:
            logger.error("Missing code or state parameter in callback")
            return RedirectResponse(url="http://localhost:5000/login?error=missing_parameters")
        
        # Verify state parameter for CSRF protection
        stored_state = request.session.get("oauth_state")
        if not stored_state or stored_state != state:
            logger.error(f"State mismatch: stored={stored_state}, received={state}")
            return RedirectResponse(url="http://localhost:5000/login?error=invalid_state")
        
        # Clear state from session after verification
        request.session.pop("oauth_state", None)
        
        # Exchange authorization code for tokens using Google service
        logger.info("Exchanging authorization code for tokens")
        token_data = google_oauth_service.exchange_code_for_tokens(code)
        
        user_info = token_data["user_info"]
        
        # Find or create user in database
        user = await get_or_create_google_user(db, user_info)
        
        # Store user session data
        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        request.session["user_name"] = user.full_name
        request.session["user_picture"] = getattr(user.profile, 'avatar_url', None) if hasattr(user, 'profile') else None
        request.session["is_authenticated"] = True
        
        logger.info(f"User authenticated successfully: {user.email}")
        
        # Redirect to dashboard after successful authentication
        return RedirectResponse(url="http://localhost:5000/dashboard")
        
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        return RedirectResponse(url="http://localhost:5000/login?error=authentication_failed")

@router.post("/logout")
async def logout_session(request: Request):
    """
    Log out user by clearing session data (for session-based auth).
    """
    try:
        # Clear all session data
        request.session.clear()
        
        logger.info("User logged out successfully")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/session/me")
async def get_current_session_user(request: Request, db: Session = Depends(get_db)):
    """
    Get current authenticated user information from session.
    """
    try:
        # Check if user is authenticated via session
        if not request.session.get("is_authenticated"):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Load user profile for additional data
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "profile_picture": profile.avatar_url if profile else None,
            "google_id": user.google_id,
            "role": user.role,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "is_active": user.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current session user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

async def get_or_create_google_user(db: Session, user_info: dict) -> User:
    """
    Get existing user or create new user from Google OAuth data.
    
    Args:
        db: Database session
        user_info: User information from Google OAuth
        
    Returns:
        User object
    """
    try:
        google_id = user_info.get("google_id")
        email = user_info.get("email")
        
        # Try to find existing user by Google ID first
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Try to find by email (in case user registered with email before)
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Update existing user with Google ID
                user.google_id = google_id
                logger.info(f"Updated existing user {email} with Google ID")
            else:
                # Create new user from Google account
                username = email.split('@')[0]  # Use email prefix as username
                
                # Ensure username is unique
                counter = 1
                original_username = username
                while db.query(User).filter(User.username == username).first():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Create new user
                user = User(
                    email=email,
                    username=username,
                    full_name=user_info.get("name", ""),
                    google_id=google_id,
                    hashed_password="",  # No password for Google OAuth users
                    is_active=True,
                    is_verified=True,  # Google accounts are pre-verified
                    role="user"  # Default role
                )
                db.add(user)
                db.flush()  # Get user ID without committing
                
                # Create user profile with Google picture
                profile = UserProfile(
                    user_id=user.id,
                    avatar_url=user_info.get("picture")
                )
                db.add(profile)
                
                # Create user subscription (free tier)
                subscription = UserSubscription(
                    user_id=user.id,
                    tier=SubscriptionTier.FREE
                )
                db.add(subscription)
                
                # Create user settings with defaults
                user_settings = UserSettings(user_id=user.id)
                db.add(user_settings)
                
                logger.info(f"Created new Google user: {email}")
        else:
            # Update existing Google user info
            user.full_name = user_info.get("name", user.full_name)
            
            # Update profile picture if user has a profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            if profile:
                profile.avatar_url = user_info.get("picture")
            
            logger.info(f"Updated existing Google user: {email}")
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating/updating Google user: {str(e)}")
        raise Exception(f"Failed to create or update user: {str(e)}")