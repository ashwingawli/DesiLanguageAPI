#!/usr/bin/env python3
"""
Script to create test user accounts with Free/Premium subscriptions and admin users.
Creates 10 test users (5 Free, 5 Premium) + 1 admin user.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.models import User, UserProfile, UserSubscription, UserSettings, SubscriptionTier, UserRole
from app.auth.dependencies import hash_password
from datetime import datetime, timezone

def create_test_users():
    """Create test users with different subscription tiers and one admin."""
    
    # Get database session
    db = next(get_db())
    
    # Test user data
    test_users = [
        # Free tier users (5)
        {"username": "testuser1", "email": "testuser1@example.com", "full_name": "Test User One", "tier": SubscriptionTier.FREE, "role": UserRole.USER},
        {"username": "testuser2", "email": "testuser2@example.com", "full_name": "Test User Two", "tier": SubscriptionTier.FREE, "role": UserRole.USER},
        {"username": "testuser3", "email": "testuser3@example.com", "full_name": "Test User Three", "tier": SubscriptionTier.FREE, "role": UserRole.USER},
        {"username": "testuser4", "email": "testuser4@example.com", "full_name": "Test User Four", "tier": SubscriptionTier.FREE, "role": UserRole.USER},
        {"username": "testuser5", "email": "testuser5@example.com", "full_name": "Test User Five", "tier": SubscriptionTier.FREE, "role": UserRole.USER},
        
        # Premium tier users (5)
        {"username": "premiumuser1", "email": "premiumuser1@example.com", "full_name": "Premium User One", "tier": SubscriptionTier.PREMIUM, "role": UserRole.USER},
        {"username": "premiumuser2", "email": "premiumuser2@example.com", "full_name": "Premium User Two", "tier": SubscriptionTier.PREMIUM, "role": UserRole.USER},
        {"username": "premiumuser3", "email": "premiumuser3@example.com", "full_name": "Premium User Three", "tier": SubscriptionTier.PREMIUM, "role": UserRole.USER},
        {"username": "premiumuser4", "email": "premiumuser4@example.com", "full_name": "Premium User Four", "tier": SubscriptionTier.PREMIUM, "role": UserRole.USER},
        {"username": "premiumuser5", "email": "premiumuser5@example.com", "full_name": "Premium User Five", "tier": SubscriptionTier.PREMIUM, "role": UserRole.USER},
        
        # Admin user (1)
        {"username": "admin", "email": "admin@desiLanguage.com", "full_name": "System Administrator", "tier": SubscriptionTier.PREMIUM, "role": UserRole.ADMIN},
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                continue
            
            # Create user with default password "password123"
            hashed_password = hash_password("password123")
            
            # Create user
            db_user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,  # Set to True for test users
                role=user_data["role"],
                created_at=datetime.now(timezone.utc)
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Create basic user profile
            profile = UserProfile(
                user_id=db_user.id,
                bio=f"Test profile for {user_data['full_name']}",
                country="India" if "premium" not in user_data["username"] else "United States",
                native_language="English",
                primary_learning_language="Telugu",
                learning_goal="travel" if user_data["tier"] == SubscriptionTier.FREE else "business",
                daily_goal_minutes=15 if user_data["tier"] == SubscriptionTier.FREE else 30
            )
            db.add(profile)
            
            # Create user subscription
            subscription = UserSubscription(
                user_id=db_user.id,
                tier=user_data["tier"],
                status="active",
                start_date=datetime.now(timezone.utc),
                auto_renew=True
            )
            db.add(subscription)
            
            # Create user settings with defaults
            settings = UserSettings(
                user_id=db_user.id,
                email_notifications=True,
                push_notifications=True,
                audio_enabled=True,
                show_transliteration=True,
                show_pronunciation=True,
                theme="light"
            )
            db.add(settings)
            
            db.commit()
            
            created_users.append({
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role.value,
                "subscription_tier": user_data["tier"].value
            })
            
            print(f"✓ Created user: {user_data['username']} ({user_data['tier'].value}, {user_data['role'].value})")
            
        except Exception as e:
            print(f"✗ Failed to create user {user_data['username']}: {str(e)}")
            db.rollback()
            continue
    
    db.close()
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST USERS CREATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total users created: {len(created_users)}")
    
    # Group by subscription tier
    free_users = [u for u in created_users if u["subscription_tier"] == "free"]
    premium_users = [u for u in created_users if u["subscription_tier"] == "premium"]
    admin_users = [u for u in created_users if u["role"] == "admin"]
    
    print(f"\nFree tier users: {len(free_users)}")
    for user in free_users:
        print(f"  - {user['username']} ({user['email']})")
    
    print(f"\nPremium tier users: {len(premium_users)}")
    for user in premium_users:
        print(f"  - {user['username']} ({user['email']})")
    
    print(f"\nAdmin users: {len(admin_users)}")
    for user in admin_users:
        print(f"  - {user['username']} ({user['email']})")
    
    print(f"\n{'='*50}")
    print("LOGIN CREDENTIALS")
    print(f"{'='*50}")
    print("All test users have the password: password123")
    print("\nYou can login with any of the following:")
    for user in created_users:
        print(f"  Username: {user['username']} | Email: {user['email']}")

if __name__ == "__main__":
    print("Creating test user accounts...")
    create_test_users()
    print("\nTest user creation completed!")