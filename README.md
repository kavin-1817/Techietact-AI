# Techietact AI Tutor - AI-Based Learning Platform

A modern, Django-based AI learning platform inspired by StudySphere. Techietact AI Tutor provides free, high-quality online tutoring services using advanced AI technology.

## 🚀 Features

- **User Authentication**: Sign up, login, and logout functionality
- **AI Chat Interface**: ChatGPT-like interface for interactive learning
- **Dashboard**: Personalized dashboard with recent sessions and suggested topics
- **Course Suggestions**: AI-driven topic recommendations
- **Modern UI**: Beautiful, responsive design using Bootstrap 5
- **Chat History**: Store and view past learning sessions

## 🛠️ Tech Stack

- **Backend**: Django 5.x
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **AI Integration**: Integrated with Google Gemini API

## 📦 Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd Techietact-AI
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create an admin user** (for course management):
   ```bash
   python manage.py create_admin
   ```
   This will prompt you to enter username, email, and password for the admin account.
   Alternatively, you can use Django's admin panel:
   ```bash
   python manage.py createsuperuser
   ```
   Then create an AdminProfile in Django admin or use the create_admin command.

6. **Load sample data** (optional):
   ```bash
   python manage.py seed_data
   ```
   This will create sample courses for the dashboard.

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Open your browser and navigate to `http://127.0.0.1:8000/`
   - Sign up for a new account or use the admin panel to create users

## 🔧 Configuration

### Gemini API Integration

The application is configured to use Google's Gemini API. To enable AI-powered responses:

1. **Get your Gemini API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key or use an existing one

2. **Set the API key** (choose one method):

   **Method 1: Environment Variable (Recommended)**
   ```bash
   # On Windows (PowerShell)
   $env:GEMINI_API_KEY="your-gemini-api-key-here"
   
   # On Linux/Mac
   export GEMINI_API_KEY="your-gemini-api-key-here"
   ```

   **Method 2: Django Settings**
   Add to `techietact_ai/settings.py`:
   ```python
   GEMINI_API_KEY = "your-gemini-api-key-here"
   ```
   ⚠️ **Note**: For production, always use environment variables for security.

3. **The code is already configured!** The `ask_ai()` function in `learning/views.py` will automatically:
   - Use the Gemini API if the key is configured
   - Fall back to placeholder responses if the key is missing
   - Use the `gemini-pro` model for text generation

4. **Test the integration:**
   - Start the server: `python manage.py runserver`
   - Log in and go to the Chat page
   - Ask a question to test the AI response

## 📁 Project Structure

```
Techietact-AI/
├── techietact_ai/     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── learning/          # Main application
│   ├── models.py     # Database models
│   ├── views.py      # View functions
│   ├── urls.py       # URL routing
│   ├── admin.py      # Admin configuration
│   └── templates/    # HTML templates
│       └── learning/
│           ├── base.html
│           ├── home.html
│           ├── login.html
│           ├── signup.html
│           ├── dashboard.html
│           ├── chat.html
│           └── about.html
├── static/           # Static files
│   └── css/
│       └── style.css
├── manage.py
├── requirements.txt
└── README.md
```

## 🎯 Usage

### For Learners:
1. **Home Page** (`/`): Landing page with app introduction
2. **Sign Up** (`/signup/`): Create a new learner account
3. **Login** (`/login/`): Sign in to your account
4. **Dashboard** (`/dashboard/`): View your learning dashboard
5. **AI Chat** (`/chat/`): Start chatting with the AI tutor
6. **About** (`/about/`): Learn more about the platform

### For Admins:
1. **Admin Login** (`/admin/login/`): Login to admin dashboard
2. **Admin Dashboard** (`/admin/dashboard/`): Manage courses and content
3. **Create Course** (`/admin/courses/create/`): Add new courses
4. **Edit Course** (`/admin/courses/<id>/edit/`): Update existing courses
5. **Delete Course**: Remove courses from the dashboard

## 🔐 Authentication

- **Two user roles**: **Learner** and **Admin**
- Uses Django's built-in authentication system
- Automatic profile creation on signup (LearnerProfile for learners, AdminProfile for admins)
- Session-based authentication
- Admin users can manage courses through the admin dashboard

## 🗄️ Database Models

- **LearnerProfile**: Extended user profile with join date
- **Course**: Course/topic suggestions with categories
- **ChatSession**: Stores chat history (question, response, timestamp)

## 🎨 Customization

### Styling
- Custom CSS: `static/css/style.css`
- Bootstrap 5: CDN-based (can be downloaded locally)
- Color scheme: Easily customizable via CSS variables

### Adding New Features
- Models: Add to `learning/models.py`
- Views: Add to `learning/views.py`
- URLs: Add to `learning/urls.py`
- Templates: Add to `learning/templates/learning/`

## 🚀 Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL recommended)
4. Set up static file serving (WhiteNoise or CDN)
5. Use environment variables for sensitive data
6. Enable HTTPS

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on the repository.

---

**Built with ❤️ using Django and Bootstrap**

