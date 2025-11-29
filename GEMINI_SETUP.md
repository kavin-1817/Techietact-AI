# Gemini API Key Setup Guide

## Quick Setup Steps

### 1. Install Required Package
```bash
pip install python-dotenv
```

### 2. Get Your Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or use an existing key
4. Copy your API key

### 3. Create .env File
Create a file named `.env` in the project root (same directory as `manage.py`) with the following content:

```
GEMINI_API_KEY=your-actual-api-key-here
```

**Important:** Replace `your-actual-api-key-here` with your actual API key from step 2.

### 4. Restart Your Django Server
After creating the `.env` file, restart your Django development server:
```bash
python manage.py runserver
```

## Alternative: Environment Variable (Windows PowerShell)
If you prefer not to use a .env file, you can set it as an environment variable:

```powershell
$env:GEMINI_API_KEY="your-actual-api-key-here"
python manage.py runserver
```

## Verify It's Working
1. Log in to your application
2. Navigate to any module
3. Ask a question like "What is print?"
4. You should now get AI-powered responses instead of the configuration message

## Troubleshooting

- **Still seeing the configuration message?**
  - Make sure the `.env` file is in the project root (same folder as `manage.py`)
  - Check that the API key doesn't have extra spaces or quotes
  - Restart your Django server after creating/updating the `.env` file

- **Getting API errors?**
  - Verify your API key is correct at [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Check that your API key hasn't been revoked
  - Ensure you have internet connectivity

## Security Note
- Never commit your `.env` file to version control (it's already in `.gitignore`)
- Keep your API key secret and don't share it publicly

