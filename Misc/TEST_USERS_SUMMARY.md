# Test Users Summary

## ✅ Test Users Successfully Created

**Total Users**: 11  
**Database**: PostgreSQL (desidb)  
**All users password**: `password123`

## 👤 User Categories

### Free Tier Users (5)
- **testuser1** - testuser1@example.com
- **testuser2** - testuser2@example.com  
- **testuser3** - testuser3@example.com
- **testuser4** - testuser4@example.com
- **testuser5** - testuser5@example.com

**Features:**
- Free subscription tier
- Daily goal: 15 minutes
- Learning goal: Travel
- Country: India
- Primary learning language: Telugu

### Premium Tier Users (5)
- **premiumuser1** - premiumuser1@example.com
- **premiumuser2** - premiumuser2@example.com
- **premiumuser3** - premiumuser3@example.com
- **premiumuser4** - premiumuser4@example.com
- **premiumuser5** - premiumuser5@example.com

**Features:**
- Premium subscription tier
- Daily goal: 30 minutes
- Learning goal: Business
- Country: United States
- Primary learning language: Telugu

### Admin Users (1)
- **admin** - admin@desiLanguage.com

**Features:**
- Admin role with full system access
- Premium subscription tier
- Can bypass lesson prerequisites
- Access to admin dashboard
- User management capabilities

## 🔑 Login Instructions

### For Testing
1. **Username/Email**: Use any username or email from the list above
2. **Password**: `password123` (same for all users)
3. **Authentication**: All users are active and verified

### API Authentication Example
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### Admin Dashboard Access
- **Username**: `admin`
- **Password**: `password123`
- **URL**: `http://localhost:8000/admin/dashboard`

## 📊 User Profiles Created

Each user has:
- ✅ **User account** with proper authentication
- ✅ **User profile** with learning preferences
- ✅ **Subscription** (Free/Premium) with active status
- ✅ **Settings** with default preferences
- ✅ **Progress tracking** ready for lesson completions

## 🧪 Testing Scenarios

### Free User Testing
- Use `testuser1` through `testuser5`
- Test lesson progression requirements
- Verify free tier limitations
- Test progress tracking

### Premium User Testing  
- Use `premiumuser1` through `premiumuser5`
- Test premium features access
- Verify enhanced lesson access
- Test advanced analytics

### Admin Testing
- Use `admin` account
- Test admin dashboard access
- Test user management features
- Test lesson bypass capabilities
- Test system statistics

## 🔒 Security Notes

- All passwords are hashed using proper bcrypt
- Users are marked as verified for testing
- Admin user has elevated privileges
- Authentication tokens expire in 24 hours (configurable)

## 🗃️ Database Schema

Users are stored across these tables:
- `users` - Main user accounts
- `user_profiles` - Learning preferences and goals
- `user_subscriptions` - Subscription tier and billing
- `user_settings` - UI and notification preferences
- `user_progress` - Learning progress tracking

## 🚀 Ready for Testing

The test users are now ready for:
- Authentication testing
- Role-based access testing
- Subscription feature testing
- Progress tracking testing
- Admin functionality testing

Start the application with `python run.py` and use any of the above credentials to test the system!