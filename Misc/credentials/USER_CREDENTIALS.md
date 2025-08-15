# DesiLanguage Test User Credentials

This document contains all test user accounts created for the DesiLanguage application with Oracle database.

## Database Information
- **Database**: Oracle Autonomous Database (GAE164F8549AE26_DESIDB) 
- **Total Users**: 13 complete user accounts
- **Connection**: Oracle wallet authentication via `desidb_high` TNS alias

## Test User Categories

### Regular Users (FREE Tier) - 5 Users
These users have basic free tier access with limited features:

| Username | Email | Password | Subscription | Role |
|----------|--------|----------|--------------|------|
| testuser1 | testuser1@example.com | password123 | FREE | USER |
| testuser2 | testuser2@example.com | password123 | FREE | USER |
| testuser3 | testuser3@example.com | password123 | FREE | USER |
| testuser4 | testuser4@example.com | password123 | FREE | USER |
| testuser5 | testuser5@example.com | password123 | FREE | USER |

**Free Tier Features:**
- Learning languages: ["Telugu"]
- Daily goal: 15 minutes
- Learning goal: "travel"
- Country: India

### Premium Users (PREMIUM Tier) - 5 Users
These users have premium subscription access with enhanced features:

| Username | Email | Password | Subscription | Role |
|----------|--------|----------|--------------|------|
| premiumuser1 | premiumuser1@example.com | password123 | PREMIUM | USER |
| premiumuser2 | premiumuser2@example.com | password123 | PREMIUM | USER |
| premiumuser3 | premiumuser3@example.com | password123 | PREMIUM | USER |
| premiumuser4 | premiumuser4@example.com | password123 | PREMIUM | USER |
| premiumuser5 | premiumuser5@example.com | password123 | PREMIUM | USER |

**Premium Tier Features:**
- Learning languages: ["Telugu", "Hindi"]  
- Daily goal: 30 minutes
- Learning goal: "business"
- Country: United States

### Administrative Users - 3 Users

#### System Administrator
- **Username**: `admin`
- **Email**: `admin@desilanguage.com`
- **Password**: `password123`
- **Role**: ADMIN
- **Subscription**: PREMIUM
- **Purpose**: Main system administration

#### Super Administrator  
- **Username**: `superadmin`
- **Email**: `superadmin@desilanguage.com`
- **Password**: `password123`
- **Role**: ADMIN
- **Subscription**: PRO
- **Purpose**: Full system control and management

#### Teacher Account
- **Username**: `teacher1`
- **Email**: `teacher1@desilanguage.com` 
- **Password**: `password123`
- **Role**: TEACHER
- **Subscription**: PRO
- **Purpose**: Content management and lesson administration

## Quick Test Accounts

For quick testing, use these recommended accounts:

### Basic Testing
```
Username: testuser1
Email: testuser1@example.com  
Password: password123
Access: Free tier user
```

### Premium Testing  
```
Username: premiumuser1
Email: premiumuser1@example.com
Password: password123
Access: Premium features
```

### Admin Testing
```
Username: admin
Email: admin@desilanguage.com
Password: password123
Access: Full admin privileges
```

## User Profile Details

All users have complete profiles including:
- ✅ User account (authenticated)
- ✅ User profile (bio, preferences, learning goals)
- ✅ Subscription details (tier, status, dates)
- ✅ User settings (notifications, audio, theme preferences)

## Authentication Features

All users support:
- Email/username login
- Password authentication (bcrypt hashed)
- JWT token-based sessions
- Role-based access control
- Subscription tier validation

## Database Tables Populated

The following Oracle tables contain user data:
- `USERS` - User accounts (13 records)
- `USER_PROFILES` - User profiles (13 records)
- `USER_SUBSCRIPTIONS` - Subscription data (13 records)
- `USER_SETTINGS` - User preferences (13 records)

## Security Notes

- All passwords are hashed using bcrypt
- JWT tokens expire based on configuration (24 hours default)
- Admin users have elevated privileges for lesson management
- Free tier users have restricted access to premium features

## API Testing

With these accounts, you can test:
- User registration/login flows
- Subscription tier restrictions  
- Admin panel access
- Lesson progression tracking
- User preference management
- Role-based API endpoints

---

**Database Status**: ✅ All users successfully created and verified in Oracle  
**Authentication**: ✅ Ready for testing  
**Last Updated**: August 11, 2025