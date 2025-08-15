# Google OAuth Setup Guide

This guide explains how to set up Google OAuth authentication for the DesiLanguage application.

## Prerequisites

1. A Google Cloud Platform (GCP) project
2. Google APIs & Services enabled
3. OAuth 2.0 credentials configured

## Step 1: Google Cloud Console Setup

### Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Enable Google+ API (if needed)

1. Go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "People API"
3. Enable the API

### Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client IDs**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type (for public apps)
   - Fill in required fields:
     - App name: "DesiLanguage"
     - User support email: your email
     - Developer contact information: your email
   - Add scopes: `email`, `profile`, `openid`
   - Add test users if in testing mode

4. Create OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Name: "DesiLanguage Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3000` (development)
     - `http://localhost:5173` (Vite dev server)
     - `https://yourdomain.com` (production)
   - Authorized redirect URIs:
     - `http://localhost:3000` (development)
     - `http://localhost:5173` (Vite dev server)  
     - `https://yourdomain.com` (production)

5. Download the JSON file or copy the **Client ID**

## Step 2: Backend Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### Dependencies

The required packages are already added to `requirements.txt`:

```
google-auth==2.40.3
google-auth-oauthlib==1.2.2
google-auth-httplib2==0.2.0
```

Install them:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Frontend Configuration

### Environment Variables

Create `.env` file in the frontend directory:

```bash
# Frontend environment file: frontend/replt-app/.env
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
VITE_API_URL=http://localhost:8000
```

### Dependencies

The Google Identity Services script is automatically loaded via the HTML file. No additional npm packages are needed.

## Step 4: Testing the Implementation

### Start the Backend

```bash
# From project root
source venv/bin/activate
python run.py
```

### Start the Frontend

```bash
# From frontend directory
cd frontend/replt-app
npm install
npm run dev
```

### Test Google Authentication

1. Open the application in your browser
2. Click on the authentication modal
3. Click "Sign in with Google"
4. Complete the Google OAuth flow
5. Verify you're redirected back and logged in

## How It Works

### Frontend Flow

1. User clicks "Sign in with Google"
2. Google Identity Services loads and shows OAuth popup
3. User authenticates with Google
4. Google returns a JWT ID token
5. Frontend sends the JWT token to backend `/api/auth/google`
6. Backend verifies token and creates/updates user
7. Backend returns access token for the application
8. User is logged in

### Backend Flow

1. Receives Google JWT token
2. Verifies token with Google's servers using the Client ID
3. Extracts user information (email, name, picture)
4. Creates new user or finds existing user by email
5. Creates user profile, subscription, and settings if new user
6. Returns application JWT token for future API calls

### Security Features

- Google JWT tokens are verified server-side
- User email verification is handled by Google
- No passwords stored for Google users
- Application uses its own JWT tokens for API access
- Google tokens are not stored, only used for verification

## Troubleshooting

### Common Issues

1. **"Google authentication not configured"**
   - Ensure `GOOGLE_CLIENT_ID` is set in backend `.env`
   - Restart the backend server

2. **"Invalid Google token"**
   - Check that frontend `VITE_GOOGLE_CLIENT_ID` matches backend `GOOGLE_CLIENT_ID`
   - Verify the Client ID is correct in Google Console
   - Ensure the domain is in authorized origins

3. **"This app isn't verified"** 
   - This is expected for new apps in development
   - Click "Advanced" → "Go to DesiLanguage (unsafe)" to continue
   - For production, submit for Google verification

4. **CORS errors**
   - Ensure your frontend domain is in "Authorized JavaScript origins"
   - Check that backend CORS settings allow your frontend domain

### Development vs Production

**Development:**
- Use `http://localhost:3000` and `http://localhost:5173` as origins
- App verification warning is expected

**Production:**
- Add your production domain to authorized origins
- Submit app for Google verification to remove warnings
- Use HTTPS for all production URLs

## Security Notes

- Keep your Client ID secure but note it's not secret (it's visible to browsers)
- Never expose Client Secret in frontend code
- The backend validates all Google tokens server-side
- Google handles user authentication and email verification
- User sessions are managed by your application's JWT tokens

## Additional Resources

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web/guides/overview)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)