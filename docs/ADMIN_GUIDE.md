# Admin Panel User Guide

## Overview

The DesiLanguage Admin Panel provides comprehensive administrative controls for managing users, lessons, and system analytics. This guide explains how to access and use the admin functionality.

## Getting Started

### 1. Prerequisites

- Admin role assigned to your user account
- Active authentication session
- Access to the DesiLanguage application

### 2. Creating Admin Users

To create admin users for testing or initial setup:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the test user creation script
python scripts/create_test_users.py
```

This script creates test users including an admin user with:
- **Username**: `admin_user`
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Role**: Admin

### 3. Accessing the Admin Panel

1. **Via Navigation**: If you're logged in as an admin, you'll see an "Admin" link in the main navigation
2. **Via User Menu**: Click your profile icon and select "Admin Panel" from the dropdown
3. **Direct URL**: Navigate to `/admin` in your browser

## Admin Panel Features

### Dashboard Overview

The admin dashboard provides key metrics at a glance:

- **Total Users**: Complete user count across all roles
- **Active Users**: Users active today and this week
- **Lessons Completed**: Total lesson completions across all users
- **Study Time**: Total hours studied by all users

### User Management

#### Viewing Users

- **Search**: Find users by email, username, or full name
- **Filter by Role**: Show only users, teachers, or admins
- **Filter by Status**: Show only active or inactive users
- **Pagination**: Navigate through large user lists

#### User Actions

1. **Change Role**
   - Select new role from dropdown (User, Teacher, Admin)
   - Changes take effect immediately
   - Cannot demote your own admin account

2. **Activate/Deactivate Users**
   - Toggle user active status
   - Inactive users cannot log in
   - Cannot deactivate your own account

3. **Delete Users**
   - Permanently remove user accounts
   - Deletes all associated data
   - Cannot delete your own account
   - Requires confirmation dialog

#### User Details

Click on any user to view:
- Complete profile information
- Subscription details
- Learning progress by language
- Recent achievements
- Account settings

### Lesson Management

#### Viewing Lessons

- **Language Filter**: Show lessons for specific languages
- **Content Overview**: See vocabulary, sentences, quiz counts
- **Creation Date**: When lessons were generated

#### Lesson Actions

1. **View Lesson Details**
   - Full lesson content preview
   - All vocabulary items
   - Example sentences
   - Quiz questions
   - Short story (if present)

2. **Delete Lessons**
   - Remove lessons from the system
   - Requires confirmation dialog
   - Cannot be undone

### Analytics

#### Top Languages
- Most popular languages by user count
- Total lessons completed per language
- Learning trend insights

#### Subscription Breakdown
- User distribution across subscription tiers
- Free vs. Premium user ratios
- Revenue insights

## API Endpoints

The admin panel uses the following API endpoints:

### Dashboard Stats
```
GET /admin/dashboard/stats
```
Returns comprehensive dashboard statistics.

### User Management
```
GET /admin/users                    # List all users with filters
GET /admin/users/{user_id}          # Get user details
PUT /admin/users/{user_id}/role     # Update user role
PUT /admin/users/{user_id}/status   # Activate/deactivate user
DELETE /admin/users/{user_id}       # Delete user
```

### Lesson Management
```
GET /admin/lessons                  # List all lessons
DELETE /admin/lessons/{lesson_id}   # Delete lesson
```

### User Progress
```
GET /admin/users/{user_id}/progress # Get detailed user progress
```

## Security Features

### Access Control
- All admin endpoints require admin role authentication
- JWT token validation on every request
- Role-based permission checking

### Self-Protection
- Admins cannot demote their own admin role
- Admins cannot deactivate their own account
- Admins cannot delete their own account

### Audit Trail
- All admin actions are logged with timestamps
- User changes tracked in database
- Session management and timeout handling

## Testing Admin Functionality

### 1. API Testing

Use the provided test script:

```bash
# Set your admin token
export ADMIN_TOKEN="your_jwt_token_here"

# Run API tests
./scripts/test_admin_api.sh
```

### 2. Frontend Testing

1. Log in as admin user
2. Navigate to `/admin`
3. Test all tab functionality:
   - User Management filters and actions
   - Lesson Management viewing and deletion
   - Analytics data display

### 3. Permission Testing

1. Log in as regular user
2. Try accessing `/admin` (should be denied)
3. Test API endpoints without admin role (should return 403)

## Common Tasks

### Adding New Admin Users

1. Navigate to User Management
2. Find the target user
3. Change their role to "Admin"
4. User will have admin access on next login

### Managing Inactive Users

1. Use Status filter to show inactive users
2. Review accounts for reactivation or deletion
3. Bulk actions for user management

### Content Moderation

1. Review recently created lessons
2. Check for inappropriate content
3. Delete problematic lessons if necessary

### System Monitoring

1. Monitor dashboard stats for trends
2. Check user activity patterns
3. Analyze subscription conversion rates

## Troubleshooting

### Access Denied Errors
- Verify admin role assignment
- Check authentication token validity
- Ensure session hasn't expired

### API Errors
- Check server logs for detailed error messages
- Verify database connectivity
- Confirm proper CORS configuration

### Frontend Issues
- Clear browser cache
- Check browser console for JavaScript errors
- Verify API endpoints are reachable

## Best Practices

### Security
- Regularly review admin user list
- Monitor for suspicious activity
- Use strong passwords for admin accounts
- Enable two-factor authentication when available

### Data Management
- Regular database backups before major operations
- Document all significant admin actions
- Test changes in development environment first

### User Support
- Use admin tools to assist users with account issues
- Monitor user feedback for system improvements
- Maintain user privacy during support activities

## Support

For technical issues or questions about admin functionality:
1. Check server logs for error details
2. Review API documentation for endpoint specifics
3. Test with the provided scripts for troubleshooting
4. Contact development team for advanced support needs