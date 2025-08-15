#!/usr/bin/env python3
"""
Fix existing users by adding missing profiles, subscriptions, and settings
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.models import User, UserProfile, UserSubscription, UserSettings, SubscriptionTier, UserRole
from datetime import datetime, timezone

def fix_existing_users():
    """Add missing profiles, subscriptions, and settings for existing users"""
    
    db = next(get_db())
    
    print("Fixing existing users with missing profiles/subscriptions/settings...")
    
    # User tier mapping based on usernames
    user_tier_map = {
        "testuser1": SubscriptionTier.FREE,
        "testuser2": SubscriptionTier.FREE,
        "testuser3": SubscriptionTier.FREE,
        "testuser4": SubscriptionTier.FREE,
        "testuser5": SubscriptionTier.FREE,
        "premiumuser1": SubscriptionTier.PREMIUM,
        "premiumuser2": SubscriptionTier.PREMIUM,
        "premiumuser3": SubscriptionTier.PREMIUM,
        "premiumuser4": SubscriptionTier.PREMIUM,
        "premiumuser5": SubscriptionTier.PREMIUM,
        "admin": SubscriptionTier.PREMIUM,
        "teacher1": SubscriptionTier.PRO,
        "superadmin": SubscriptionTier.PRO,
    }
    
    # Get all users
    users = db.query(User).all()
    fixed_count = 0
    
    for user in users:
        try:
            print(f"\nProcessing user: {user.username}")
            
            # Get expected subscription tier
            expected_tier = user_tier_map.get(user.username, SubscriptionTier.FREE)
            
            # Check and create missing profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            if not profile:
                learning_languages_json = json.dumps(["Telugu", "Hindi"] if expected_tier != SubscriptionTier.FREE else ["Telugu"])
                
                profile = UserProfile(
                    user_id=user.id,
                    bio=f"Test profile for {user.full_name}",
                    country="India" if "premium" not in user.username and user.role != UserRole.ADMIN else "United States",
                    native_language="English",
                    learning_languages=learning_languages_json,
                    primary_learning_language="Telugu",
                    learning_goal="travel" if expected_tier == SubscriptionTier.FREE else "business",
                    daily_goal_minutes=15 if expected_tier == SubscriptionTier.FREE else 30,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(profile)
                print(f"  ✓ Created profile")
            else:
                print(f"  • Profile already exists")
            
            # Check and create missing subscription
            subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user.id).first()
            if not subscription:
                subscription = UserSubscription(
                    user_id=user.id,
                    tier=expected_tier,
                    status="active",
                    start_date=datetime.now(timezone.utc),
                    auto_renew=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(subscription)
                print(f"  ✓ Created subscription ({expected_tier.value})")
            else:
                print(f"  • Subscription already exists")
            
            # Check and create missing settings
            settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
            if not settings:
                settings = UserSettings(
                    user_id=user.id,
                    email_notifications=True,
                    push_notifications=True,
                    audio_enabled=True,
                    show_transliteration=True,
                    show_pronunciation=True,
                    theme="light",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(settings)
                print(f"  ✓ Created settings")
            else:
                print(f"  • Settings already exist")
            
            # Commit changes for this user
            db.commit()
            fixed_count += 1
            print(f"  ✅ Fixed user: {user.username}")
            
        except Exception as e:
            print(f"  ✗ Failed to fix user {user.username}: {str(e)}")
            db.rollback()
            continue
    
    db.close()
    
    # Final summary
    print(f"\n{'='*50}")
    print("USER FIX SUMMARY")
    print(f"{'='*50}")
    print(f"Total users processed: {len(users)}")
    print(f"Users fixed successfully: {fixed_count}")
    
    print(f"\n{'='*50}")
    print("RECOMMENDED TEST ACCOUNTS")
    print(f"{'='*50}")
    print("All users have the password: password123")
    print("")
    print("  Regular User: testuser1 / password123")
    print("  Premium User: premiumuser1 / password123")
    print("  Admin User: admin / password123")
    print("  Teacher User: teacher1 / password123") 
    print("  Super Admin: superadmin / password123")

if __name__ == "__main__":
    fix_existing_users()
    print("\nUser fix completed!")