"""
Management command to seed Django course with complete modules and topics
Run with: python manage.py seed_django_course
"""
import random
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Django course, modules, and quizzes'

    def handle(self, *args, **options):
        # Create or get Django course
        course, created = Course.objects.get_or_create(
            title='Django Web Framework Course',
            defaults={
                'description': 'Complete Django web framework course covering all fundamental and advanced concepts. Learn from basics to advanced topics including models, views, templates, forms, authentication, ORM, middleware, and more.',
                'category': 'programming',
                'is_featured': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Course already exists: {course.title}. Updating modules...'))
        
        # Define modules with their content
        modules_data = self.get_modules_data()
        
        total_questions = 0
        for module_data in modules_data:
            module, module_created = Module.objects.update_or_create(
                course=course,
                order=module_data['order'],
                defaults={
                    'title': module_data['title'],
                    'summary': module_data['summary'],
                    'learning_objectives': module_data['learning_objectives'],
                    'topics': module_data['topics'],
                }
            )
            
            if module_created:
                self.stdout.write(self.style.SUCCESS(f'  Created module {module_data["order"]}: {module.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Updated module {module_data["order"]}: {module.title}'))
            
            # Create quiz for the module
            quiz, quiz_created = Quiz.objects.update_or_create(
                module=module,
                defaults={
                    'title': f'{module.title} - Quiz',
                    'description': f'Assessment quiz for {module.title}',
                    'passing_score': 70,
                    'time_limit': 30,
                }
            )
            
            if quiz_created:
                self.stdout.write(self.style.SUCCESS(f'    Created quiz: {quiz.title}'))
            else:
                # Delete existing questions to recreate them
                quiz.questions.all().delete()
                self.stdout.write(self.style.WARNING(f'    Updated quiz: {quiz.title}'))
            
            # Create questions for the quiz
            questions_count = self.create_quiz_questions(quiz, module_data['questions'])
            total_questions += questions_count
            self.stdout.write(self.style.SUCCESS(f'    Created {questions_count} questions'))
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created/updated Django course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Introduction to Django',
                'summary': 'Get started with Django web framework. Learn what Django is, why to use it, understand its architecture (MTV), and set up your development environment.',
                'learning_objectives': 'Understand what Django is and why use it\nLearn Django\'s architecture (MTV - Model-Template-View)\nSet up Python, virtual environment, and install Django\nCreate a Django project using django-admin startproject\nUnderstand project structure (settings, urls, wsgi/asgi, apps)\nRun development server and test basic request-response',
                'topics': 'What is Django and why use it\nDjango\'s architecture (MTV — Model-Template-View)\nSetting up Python, virtual environment, installing Django\nCreating a Django project (django-admin startproject, manage.py)\nProject structure overview (settings, urls, wsgi/asgi, apps)\nRunning development server (runserver), basic request-response check',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Django Web Framework',
                'summary': 'Explore Django as a web framework. Learn about installed apps, project settings, directory structure, Django lifecycle, and manage commands.',
                'learning_objectives': 'Understand Django as a web framework\nLearn about installed apps and project settings\nExplore directory structure and Django project/app conventions\nUnderstand Django lifecycle: request → URL routing → view → response/template\nMaster Django CLI / manage commands',
                'topics': 'Overview of Django as a web framework\nInstalled apps and project settings\nDirectory structure and Django project/app conventions\nDjango lifecycle: request → URL routing → view → response/template\nUsing Django CLI / manage commands (creating apps, migrations, runserver etc.)',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'URLs and Views',
                'summary': 'Master URL routing and views in Django. Learn to configure URLs, connect them to views, and create function-based views that handle requests and return responses.',
                'learning_objectives': 'Configure urls.py using path() and re_path()\nUnderstand URL patterns and urlpatterns\nConnect URLs to views\nCreate function-based views\nHandle request data (GET/POST) and understand request object\nUse URL names and reverse URLs',
                'topics': 'Configuring urls.py, using path() / re_path(), URL patterns and urlpatterns\nConnecting URLs to views\nFunction-based views: writing views that return HttpResponse, rendering templates, redirects\nHandling request data (GET/POST), request object basics, URL names & reversing URLs',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Django Templates',
                'summary': 'Learn Django Template Language (DTL) to create dynamic web pages. Master template inheritance, variables, tags, filters, and template organization.',
                'learning_objectives': 'Understand Django Template Language (DTL)\nUse variables, tags, and filters in templates\nImplement template inheritance with base templates and blocks\nRender dynamic data using templates\nOrganize templates with includes and partial templates\nUnderstand escaping, autoescape, and safe output',
                'topics': 'Django Template Language (DTL): variables, tags, filters\nTemplate inheritance (base template + blocks)\nUsing templates to render dynamic data\nIncluding partial templates, template organization\nEscaping, autoescape, safe output (sanitization basics)',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Static Files',
                'summary': 'Learn to manage static files (CSS, JavaScript, images) in Django. Configure static files settings and serve them during development and production.',
                'learning_objectives': 'Understand what static files are in Django\nConfigure static files (STATICFILES_DIRS, STATIC_URL, collectstatic)\nReference static files in templates using {% static %} tag\nServe static files during development\nLearn basics of deploying static files for production',
                'topics': 'What are static files (CSS / JS / images) in Django\nConfiguring static files (STATICFILES_DIRS, STATIC_URL, collectstatic)\nReferencing static files in templates via {% static %} tag\nServing static files during development\n(Optional) Basics of deploying static files for production',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Django Model',
                'summary': 'Master Django models to define your database schema. Learn field types, model metadata, and how to create and apply migrations.',
                'learning_objectives': 'Define models using classes inheriting models.Model\nUnderstand field types and options (CharField, IntegerField, DateTimeField, etc.)\nConfigure model metadata options (__str__, ordering, verbose names)\nCreate and apply migrations (makemigrations, migrate)\nUnderstand model vs database table mapping',
                'topics': 'Defining models (classes inheriting models.Model)\nField types and options (CharField, IntegerField, DateTimeField, BooleanField etc.)\nModel metadata options (like __str__, ordering, verbose names)\nCreating and applying migrations (makemigrations, migrate)\nUnderstanding model vs database table mapping',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Django Forms / Model Forms',
                'summary': 'Create and handle forms in Django. Learn to build Form classes, ModelForm classes, render forms in templates, and process form submissions.',
                'learning_objectives': 'Understand why use forms in Django\nCreate Form classes in forms.py\nCreate ModelForm classes bound to models\nRender forms in templates (manual or {{ form.as_... }})\nHandle form submission (POST), request data, and save form data to models',
                'topics': 'Understanding forms in Django (why use forms)\nCreating Form classes in forms.py\nCreating ModelForm classes bound to models\nRendering forms in templates (manual or {{ form.as_… }})\nHandling form submission (POST), request data, saving form data to models (via ModelForm)',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Form Validation',
                'summary': 'Implement form validation in Django. Learn built-in validation, custom validation methods, error handling, and CSRF protection.',
                'learning_objectives': 'Use built-in validation (required fields, data types, field-level validation)\nImplement custom validation (overriding clean_field() and clean())\nDisplay validation errors in templates\nHandle invalid form submission gracefully\nUnderstand and implement CSRF protection',
                'topics': 'Built-in validation (required fields, data types, field-level validation)\nCustom validation (overriding clean_field() and clean())\nDisplaying validation errors in templates\nHandling invalid form submission gracefully\nCSRF protection — using {% csrf_token %} in forms',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Django CRUD Operations',
                'summary': 'Implement Create, Read, Update, Delete functionality for your models. Build views and templates for listing, detail views, and data manipulation.',
                'learning_objectives': 'Implement Create, Read, Update, Delete functionality for models\nCreate views and templates for listing data (Read)\nBuild detail views for individual records\nCreate forms for Create and Update operations\nImplement Delete functionality with confirmation\nAdd pagination and simple search/filter if needed',
                'topics': 'Implementing Create, Read, Update, Delete functionality for models\nViews and templates for listing data (Read), detail views\nForms for Create and Update operations; handling POST requests\nDelete functionality (confirmation, deletion)\nPossibly pagination and simple search/filter (if included)',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Django ORM (Object Relational Mapper)',
                'summary': 'Master Django ORM to query your database efficiently. Learn QuerySet methods, relationships, aggregations, and advanced queries.',
                'learning_objectives': 'Query database using Django ORM: .all(), .filter(), .get(), .exclude(), .order_by()\nUnderstand QuerySet chaining, slicing, and evaluation\nWork with relationships: ForeignKey, OneToOneField, ManyToManyField\nQuery related data across relationships\nUse aggregation, annotation, and advanced queries\nManage migrations and schema changes',
                'topics': 'Querying database using Django ORM: .all(), .filter(), .get(), .exclude(), .order_by()\nQuerySet chaining, slicing, evaluation\nRelationships: ForeignKey, OneToOneField, ManyToManyField — defining and querying related data\nAggregation, annotation, advanced queries (if covered)\nMigrations management and best practices for schema changes',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'User Authentication',
                'summary': 'Implement user authentication in Django. Learn to use built-in authentication system, create registration and login forms, and manage user sessions.',
                'learning_objectives': 'Use built-in authentication system: User model, login/logout\nCreate user registration (sign up) and login forms\nHandle sessions and user authentication\nUnderstand password hashing and security basics\nImplement access control using login_required decorator\nLearn permission/authorization basics',
                'topics': 'Built-in authentication system: User model, login/logout\nUser registration (sign up), login forms, handling sessions\nPassword hashing and security basics\nAccess control: using login required decorator, limiting views\n(Optionally) Permission/Authorization basics if discussed',
                'questions': self.get_module11_questions(),
            },
            {
                'order': 12,
                'title': 'CSV',
                'summary': 'Handle CSV files in Django. Learn to import and export data, parse CSV files, validate data, and handle errors during CSV operations.',
                'learning_objectives': 'Handle CSV files in Django (import/export)\nExport QuerySet data to CSV for download\nImport CSV data: file upload, parsing with Python\'s csv module\nValidate CSV data before saving to database\nHandle exceptions and errors during CSV import/export',
                'topics': 'Handling CSV files in Django (import/export)\nExporting QuerySet data to CSV for download\nImporting CSV data: file upload, parsing with Python\'s csv module\nValidating CSV data before saving to database\nHandling exceptions and errors during CSV import/export',
                'questions': self.get_module12_questions(),
            },
            {
                'order': 13,
                'title': 'Session Management',
                'summary': 'Understand and implement session management in Django. Learn to store and retrieve session data, configure session settings, and use sessions for user-specific features.',
                'learning_objectives': 'Understand sessions in Django: purpose and working\nUse request.session to store/retrieve data\nConfigure session settings and expiry\nUnderstand differences between sessions and cookies\nUse sessions for features like "remember me", user-specific data, flash messages',
                'topics': 'Understanding sessions in Django: purpose and working\nUsing request.session to store/retrieve data\nSession configuration and expiry\nDifferences between sessions and cookies (brief)\nUsing sessions for features like "remember me", user-specific data, flash messages',
                'questions': self.get_module13_questions(),
            },
            {
                'order': 14,
                'title': 'Django Middleware',
                'summary': 'Learn about Django middleware and how it processes requests and responses. Understand built-in middleware and create custom middleware.',
                'learning_objectives': 'Understand what middleware is and how Django processes requests/responses\nLearn about built-in middleware examples\nConfigure middleware in settings\nWrite simple custom middleware\nUnderstand use-cases: logging, security headers, request/response processing',
                'topics': 'What middleware is and how Django processes requests/responses via middleware chain\nBuilt-in middleware examples (security, sessions, auth, common etc.)\nConfiguring middleware in settings\nWriting simple custom middleware (request or response modification)\nUse-cases: logging, security headers, request/response processing',
                'questions': self.get_module14_questions(),
            },
            {
                'order': 15,
                'title': 'Database',
                'summary': 'Configure and manage databases in Django. Learn database setup, connection settings, migrations, and database management best practices.',
                'learning_objectives': 'Set up and configure database in Django settings (SQLite, MySQL, Postgres)\nConnect Django models to actual database\nApply migrations and manage DB schema changes\nUnderstand database management basics (backup/restore, migration strategy)\nConfigure Django database settings: ENGINE, NAME, USER, PASSWORD, HOST, PORT',
                'topics': 'Database setup/configuration in Django settings (SQLite, MySQL, Postgres etc.)\nConnecting Django models to actual database\nApplying migrations; managing DB schema changes\nDatabase management basics (backup/restore concept, migration strategy)\nUnderstanding Django database settings: ENGINE, NAME, USER, PASSWORD, HOST, PORT etc.',
                'questions': self.get_module15_questions(),
            },
        ]

    def create_quiz_questions(self, quiz, questions_data):
        """Create quiz questions with options"""
        count = 0
        for order, question_data in enumerate(questions_data, start=1):
            question = QuizQuestion.objects.create(
                quiz=quiz,
                question_text=question_data['question'],
                question_type='multiple_choice',
                points=1,
                order=order
            )
            
            # Shuffle options to randomize correct answer position
            options = question_data['options'].copy()
            correct_index = question_data['correct_answer'] - 1  # Convert to 0-based index
            correct_option_text = options[correct_index]
            
            # Create list of (index, option_text) tuples and shuffle
            option_pairs = list(enumerate(options))
            random.shuffle(option_pairs)
            
            # Find new position of correct answer
            new_correct_position = None
            for new_pos, (old_index, option_text) in enumerate(option_pairs, start=1):
                if option_text == correct_option_text:
                    new_correct_position = new_pos
                    break
            
            # Create options in shuffled order
            for opt_order, (old_index, option_text) in enumerate(option_pairs, start=1):
                is_correct = (opt_order == new_correct_position)
                QuizOption.objects.create(
                    question=question,
                    option_text=option_text,
                    is_correct=is_correct,
                    order=opt_order
                )
            count += 1
        return count

    # Module 1 Questions - Introduction to Django
    def get_module1_questions(self):
        return [
            {
                'question': 'What does MTV stand for in Django architecture?',
                'options': [
                    'Model-Template-View',
                    'Model-View-Template',
                    'Message-Template-View',
                    'Model-Template-Validation'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command is used to create a new Django project?',
                'options': [
                    'django-admin startproject projectname',
                    'django startproject projectname',
                    'python django-admin startproject projectname',
                    'django-admin create projectname'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the default port for Django development server?',
                'options': [
                    '8000',
                    '8080',
                    '3000',
                    '5000'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which file contains the main URL configuration in a Django project?',
                'options': [
                    'urls.py',
                    'routes.py',
                    'urls.py in the project root',
                    'settings.py'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is manage.py used for in Django?',
                'options': [
                    'A command-line utility for Django projects',
                    'A Python package manager',
                    'A database migration tool',
                    'A template engine'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is NOT a core component of Django architecture?',
                'options': [
                    'Model',
                    'Template',
                    'View',
                    'Controller'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What command is used to run the Django development server?',
                'options': [
                    'python manage.py runserver',
                    'django runserver',
                    'python runserver',
                    'manage.py server'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which file contains Django project settings?',
                'options': [
                    'settings.py',
                    'config.py',
                    'django_settings.py',
                    'project_settings.py'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of wsgi.py in a Django project?',
                'options': [
                    'Web Server Gateway Interface configuration',
                    'Web Socket Gateway Interface',
                    'Web Service Gateway Interface',
                    'Web Server Gateway Integration'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command creates a new Django app?',
                'options': [
                    'python manage.py startapp appname',
                    'django-admin startapp appname',
                    'python startapp appname',
                    'manage.py createapp appname'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - Django Web Framework
    def get_module2_questions(self):
        return [
            {
                'question': 'What is the purpose of INSTALLED_APPS in settings.py?',
                'options': [
                    'List of Django applications enabled for this project',
                    'List of Python packages to install',
                    'List of database tables',
                    'List of URL patterns'
                ],
                'correct_answer': 1
            },
            {
                'question': 'In Django, what is the correct order of request processing?',
                'options': [
                    'Request → URL routing → View → Response/Template',
                    'Request → View → URL routing → Template',
                    'Request → Template → View → Response',
                    'Request → Model → View → Template'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command is used to create database migrations?',
                'options': [
                    'python manage.py makemigrations',
                    'python manage.py migrate',
                    'python manage.py create_migrations',
                    'django-admin makemigrations'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of the apps.py file in a Django app?',
                'options': [
                    'App configuration and metadata',
                    'Application routing',
                    'Database models',
                    'Template definitions'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which directory typically contains static files in a Django project?',
                'options': [
                    'static/',
                    'assets/',
                    'public/',
                    'resources/'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the SECRET_KEY in settings.py do?',
                'options': [
                    'Used for cryptographic signing and security features',
                    'Database connection password',
                    'API authentication key',
                    'Session encryption key'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command applies migrations to the database?',
                'options': [
                    'python manage.py migrate',
                    'python manage.py makemigrations',
                    'python manage.py apply_migrations',
                    'django-admin migrate'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of the __init__.py file in a Django app?',
                'options': [
                    'Makes the directory a Python package',
                    'Initializes the database',
                    'Configures URL routing',
                    'Sets up middleware'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which setting controls the time zone for the Django project?',
                'options': [
                    'TIME_ZONE',
                    'TIMEZONE',
                    'TZ',
                    'LOCAL_TIMEZONE'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of the admin.py file in a Django app?',
                'options': [
                    'Register models with Django admin interface',
                    'Define admin user accounts',
                    'Configure admin URLs',
                    'Set admin permissions'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions - URLs and Views
    def get_module3_questions(self):
        return [
            {
                'question': 'Which function is used to define URL patterns in Django?',
                'options': [
                    'path()',
                    'url()',
                    'route()',
                    'Both path() and re_path()'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the name parameter in path() do?',
                'options': [
                    'Allows reversing URLs using reverse() or {% url %}',
                    'Sets the view function name',
                    'Defines the template name',
                    'Names the URL pattern'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method is used to get GET parameters from a request?',
                'options': [
                    'request.GET.get()',
                    'request.get()',
                    'request.GET()',
                    'request.parameters.get()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does HttpResponse return?',
                'options': [
                    'An HTTP response object',
                    'A template',
                    'A JSON object',
                    'A redirect'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which decorator is used to require login for a view?',
                'options': [
                    '@login_required',
                    '@require_login',
                    '@authenticated',
                    '@login'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of reverse() function in Django?',
                'options': [
                    'Generate URLs from URL names',
                    'Reverse a string',
                    'Reverse database query',
                    'Reverse template rendering'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method handles POST requests in a view?',
                'options': [
                    'if request.method == "POST"',
                    'request.is_post()',
                    'request.POST',
                    'handle_post()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does redirect() function do?',
                'options': [
                    'Redirects to another URL',
                    'Renders a template',
                    'Returns JSON response',
                    'Loads a view'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is a valid URL pattern?',
                'options': [
                    "path('users/<int:id>/', views.user_detail)",
                    "path('users/<id>/', views.user_detail)",
                    "path('users/{id}/', views.user_detail)",
                    "path('users/[id]/', views.user_detail)"
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of include() in urls.py?',
                'options': [
                    'Include URL patterns from another URLconf',
                    'Include templates',
                    'Include static files',
                    'Include middleware'
                ],
                'correct_answer': 1
            },
        ]

    # Module 4 Questions - Django Templates
    def get_module4_questions(self):
        return [
            {
                'question': 'Which tag is used for template inheritance?',
                'options': [
                    '{% extends %}',
                    '{% inherit %}',
                    '{% include %}',
                    '{% block %}'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you display a variable in a Django template?',
                'options': [
                    '{{ variable }}',
                    '{% variable %}',
                    '{ variable }',
                    '{{% variable %}}'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag defines a block in a template?',
                'options': [
                    '{% block blockname %}',
                    '{% define blockname %}',
                    '{% section blockname %}',
                    '{% content blockname %}'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the {% for %} tag do?',
                'options': [
                    'Loops through an iterable',
                    'Defines a function',
                    'Creates a form',
                    'Includes a template'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which filter capitalizes the first letter of a string?',
                'options': [
                    '|capfirst',
                    '|capitalize',
                    '|upper',
                    '|title'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does {% include %} tag do?',
                'options': [
                    'Includes another template',
                    'Includes a CSS file',
                    'Includes JavaScript',
                    'Includes a view'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag is used for conditional statements?',
                'options': [
                    '{% if %}',
                    '{% when %}',
                    '{% condition %}',
                    '{% check %}'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the |safe filter do?',
                'options': [
                    'Marks content as safe, preventing auto-escaping',
                    'Makes content secure',
                    'Encrypts the content',
                    'Validates the content'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which filter returns the length of a list?',
                'options': [
                    '|length',
                    '|count',
                    '|size',
                    '|len'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of {% csrf_token %}?',
                'options': [
                    'Protects against Cross-Site Request Forgery',
                    'Creates a session token',
                    'Generates a random token',
                    'Validates form data'
                ],
                'correct_answer': 1
            },
        ]

    # Module 5 Questions - Static Files
    def get_module5_questions(self):
        return [
            {
                'question': 'Which setting defines the URL prefix for static files?',
                'options': [
                    'STATIC_ROOT',
                    'STATIC_URL',
                    'STATICFILES_DIRS',
                    'STATIC_PREFIX'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which tag is used to reference static files in templates?',
                'options': [
                    '{% static "path/to/file.css" %}',
                    '{% load static %}{% static "path/to/file.css" %}',
                    '{{ static "path/to/file.css" }}',
                    '{% include static "path/to/file.css" %}'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does collectstatic command do?',
                'options': [
                    'Creates static file directories',
                    'Collects all static files into STATIC_ROOT',
                    'Compiles static files',
                    'Validates static files'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which setting lists directories where Django will look for static files?',
                'options': [
                    'STATIC_DIRS',
                    'STATICFILES_DIRS',
                    'STATIC_URL',
                    'STATIC_ROOT'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is STATIC_ROOT used for?',
                'options': [
                    'URL prefix for static files',
                    'Directory where collectstatic collects static files for deployment',
                    'List of static file directories',
                    'Static file storage backend'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which app must be in INSTALLED_APPS to use static files?',
                'options': [
                    'django.staticfiles',
                    'django.contrib.staticfiles',
                    'staticfiles',
                    'django.contrib.static'
                ],
                'correct_answer': 2
            },
            {
                'question': 'In development, how are static files served?',
                'options': [
                    'Manually configured',
                    'Automatically by Django when DEBUG=True',
                    'Through a web server',
                    'Via CDN'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default STATIC_URL value?',
                'options': [
                    '/assets/',
                    '/static/',
                    '/public/',
                    '/resources/'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which command collects static files for production?',
                'options': [
                    'python manage.py gatherstatic',
                    'python manage.py collectstatic',
                    'python manage.py staticfiles',
                    'django-admin collectstatic'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Where should you place app-specific static files?',
                'options': [
                    'In the project root',
                    'In a static/ directory inside the app',
                    'In STATIC_ROOT',
                    'In STATICFILES_DIRS'
                ],
                'correct_answer': 2
            },
        ]

    # Module 6 Questions - Django Model
    def get_module6_questions(self):
        return [
            {
                'question': 'What class must Django models inherit from?',
                'options': [
                    'Model',
                    'models.Model',
                    'django.Model',
                    'BaseModel'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which field type is used for storing text up to 255 characters?',
                'options': [
                    'TextField',
                    'CharField',
                    'StringField',
                    'VarcharField'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What command creates migration files?',
                'options': [
                    'python manage.py create_migrations',
                    'python manage.py makemigrations',
                    'python manage.py migrate',
                    'django-admin makemigrations'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method is used to define string representation of a model?',
                'options': [
                    '__repr__()',
                    '__str__()',
                    '__unicode__()',
                    'toString()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does max_length parameter do in CharField?',
                'options': [
                    'Sets minimum length',
                    'Sets maximum length of the field',
                    'Sets default length',
                    'Validates the length'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which field type stores date and time?',
                'options': [
                    'DateField',
                    'DateTimeField',
                    'TimeField',
                    'TimestampField'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does null=True do in a model field?',
                'options': [
                    'Makes the field required',
                    'Allows NULL values in the database',
                    'Sets default to NULL',
                    'Validates NULL input'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which field option makes a field required in forms?',
                'options': [
                    'required=True',
                    'blank=False',
                    'null=False',
                    'not_null=True'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does auto_now=True do in DateTimeField?',
                'options': [
                    'Sets default to now',
                    'Automatically sets field to now on save',
                    'Validates current time',
                    'Updates on every access'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which command applies migrations to the database?',
                'options': [
                    'python manage.py apply_migrations',
                    'python manage.py migrate',
                    'python manage.py sync_db',
                    'django-admin migrate'
                ],
                'correct_answer': 2
            },
        ]

    # Module 7 Questions - Django Forms / Model Forms
    def get_module7_questions(self):
        return [
            {
                'question': 'What class must Django forms inherit from?',
                'options': [
                    'Form',
                    'forms.Form',
                    'django.Form',
                    'BaseForm'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a ModelForm?',
                'options': [
                    'A model that contains forms',
                    'A form class that is automatically generated from a model',
                    'A form stored in the database',
                    'A template for forms'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method renders a form as a paragraph?',
                'options': [
                    '{{ form.as_paragraph }}',
                    '{{ form.as_p }}',
                    '{{ form.render_p }}',
                    '{{ form.p }}'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you check if a form is valid?',
                'options': [
                    'form.valid',
                    'form.is_valid()',
                    'form.check_valid()',
                    'form.validate()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does form.save() do in a ModelForm?',
                'options': [
                    'Saves the form to a file',
                    'Saves the form data to the database',
                    'Saves form configuration',
                    'Saves form template'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which attribute contains cleaned form data?',
                'options': [
                    'form.data',
                    'form.cleaned_data',
                    'form.clean_data',
                    'form.validated_data'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of forms.py file?',
                'options': [
                    'Define form templates',
                    'Define form classes',
                    'Define form URLs',
                    'Define form models'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method is called to clean and validate a specific field?',
                'options': [
                    'validate_fieldname()',
                    'clean_fieldname()',
                    'check_fieldname()',
                    'sanitize_fieldname()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does forms.CharField represent?',
                'options': [
                    'A textarea field',
                    'A text input field',
                    'A select field',
                    'A checkbox field'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you access form errors in a template?',
                'options': [
                    '{{ form.error }}',
                    '{{ form.errors }}',
                    '{{ errors }}',
                    '{{ form.validation_errors }}'
                ],
                'correct_answer': 2
            },
        ]

    # Module 8 Questions - Form Validation
    def get_module8_questions(self):
        return [
            {
                'question': 'Which method validates the entire form?',
                'options': [
                    'validate()',
                    'clean()',
                    'check()',
                    'verify()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does required=True do in a form field?',
                'options': [
                    'Sets a default value',
                    'Makes the field mandatory',
                    'Allows empty values',
                    'Validates format'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you raise a validation error in Django forms?',
                'options': [
                    'raise ValidationError("message")',
                    'raise forms.ValidationError("message")',
                    'return ValidationError("message")',
                    'throw ValidationError("message")'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does {% csrf_token %} protect against?',
                'options': [
                    'SQL injection',
                    'Cross-Site Request Forgery attacks',
                    'XSS attacks',
                    'Session hijacking'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method validates a single field?',
                'options': [
                    'validate_fieldname()',
                    'clean_fieldname()',
                    'check_fieldname()',
                    'sanitize_fieldname()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How are validation errors displayed in templates?',
                'options': [
                    '{{ form.fieldname.errors }}',
                    '{{ form.errors.fieldname }}',
                    '{{ errors.fieldname }}',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What happens if form validation fails?',
                'options': [
                    'Form is saved with errors',
                    'Form is not saved and errors are returned',
                    'Form is ignored',
                    'Form is reset'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which field type automatically validates email format?',
                'options': [
                    'CharField with email validator',
                    'EmailField',
                    'TextField',
                    'URLField'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does min_length parameter do?',
                'options': [
                    'Sets maximum length',
                    'Sets default length',
                    'Sets minimum length requirement',
                    'Validates length range'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Where are non-field errors stored?',
                'options': [
                    'form.errors',
                    'form.global_errors',
                    'form.non_field_errors',
                    'form.form_errors'
                ],
                'correct_answer': 3
            },
        ]

    # Module 9 Questions - Django CRUD Operations
    def get_module9_questions(self):
        return [
            {
                'question': 'What does CRUD stand for?',
                'options': [
                    'Create, Retrieve, Update, Destroy',
                    'Create, Read, Update, Destroy',
                    'Create, Read, Update, Delete',
                    'Create, Retrieve, Update, Delete'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which ORM method creates a new object?',
                'options': [
                    'Model.create()',
                    'Model.new()',
                    'Model.objects.create()',
                    'Model.objects.add()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you retrieve all objects from a model?',
                'options': [
                    'Model.all()',
                    'Model.objects.get_all()',
                    'Model.objects.all()',
                    'Model.fetch_all()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method updates an existing object?',
                'options': [
                    'object.update()',
                    'object.modify()',
                    'object.save()',
                    'object.change()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you delete an object?',
                'options': [
                    'object.remove()',
                    'object.destroy()',
                    'object.delete()',
                    'Model.objects.delete(object)'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method retrieves a single object by ID?',
                'options': [
                    'Model.get(id=1)',
                    'Model.objects.fetch(id=1)',
                    'Model.objects.get(id=1)',
                    'Model.find(id=1)'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between get() and filter()?',
                'options': [
                    'get() returns QuerySet, filter() returns one object',
                    'They are the same',
                    'get() returns one object, filter() returns QuerySet',
                    'get() is for reading, filter() is for updating'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which view displays a list of objects?',
                'options': [
                    'Index view',
                    'Collection view',
                    'List view',
                    'All view'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a detail view used for?',
                'options': [
                    'Displaying all objects',
                    'Creating new objects',
                    'Displaying a single object',
                    'Deleting objects'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method is used for pagination in Django?',
                'options': [
                    'Page class',
                    'Pagination class',
                    'Paginator class',
                    'PageList class'
                ],
                'correct_answer': 3
            },
        ]

    # Module 10 Questions - Django ORM
    def get_module10_questions(self):
        return [
            {
                'question': 'What does ORM stand for?',
                'options': [
                    'Object-Relational Model',
                    'Object-Relational Method',
                    'Object-Relational Mapping',
                    'Object-Relational Module'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method filters objects based on conditions?',
                'options': [
                    'Model.filter()',
                    'Model.objects.where()',
                    'Model.objects.filter()',
                    'Model.find()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does exclude() do?',
                'options': [
                    'Removes objects from database',
                    'Excludes fields from query',
                    'Returns objects that do NOT match the condition',
                    'Filters out duplicates'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which field type creates a many-to-many relationship?',
                'options': [
                    'ForeignKey',
                    'OneToOneField',
                    'ManyToManyField',
                    'MultipleField'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does order_by() do?',
                'options': [
                    'Orders database tables',
                    'Orders form fields',
                    'Orders QuerySet by specified field(s)',
                    'Orders URL patterns'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which field creates a foreign key relationship?',
                'options': [
                    'OneToOneField',
                    'ManyToManyField',
                    'ForeignKey',
                    'RelatedField'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does select_related() do?',
                'options': [
                    'Selects related fields',
                    'Creates relationships',
                    'Performs SQL JOIN to fetch related objects',
                    'Filters related objects'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method counts objects in a QuerySet?',
                'options': [
                    '.size()',
                    '.length()',
                    '.count()',
                    '.total()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does exists() do?',
                'options': [
                    'Checks if object exists in database',
                    'Validates existence',
                    'Returns True if QuerySet has results',
                    'Creates object if not exists'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method returns the first object from QuerySet?',
                'options': [
                    '.get_first()',
                    '.one()',
                    '.first()',
                    '.top()'
                ],
                'correct_answer': 3
            },
        ]

    # Module 11 Questions - User Authentication
    def get_module11_questions(self):
        return [
            {
                'question': 'Which model is used for user authentication in Django?',
                'options': [
                    'AuthUser',
                    'DjangoUser',
                    'User',
                    'Account'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which function is used to authenticate a user?',
                'options': [
                    'login_user()',
                    'verify_user()',
                    'authenticate()',
                    'check_user()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does login(request, user) do?',
                'options': [
                    'Creates a user account',
                    'Validates user credentials',
                    'Logs the user in and creates a session',
                    'Updates user profile'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which decorator requires user to be logged in?',
                'options': [
                    '@require_login',
                    '@authenticated',
                    '@login_required',
                    '@logged_in'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does logout(request) do?',
                'options': [
                    'Deletes user account',
                    'Disables user account',
                    'Logs the user out and clears session',
                    'Removes user permissions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How is password hashing handled in Django?',
                'options': [
                    'Manually with hash()',
                    'Using MD5',
                    'Automatically using PBKDF2',
                    'Using SHA1'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method creates a new user?',
                'options': [
                    'User.create()',
                    'User.objects.add()',
                    'User.objects.create_user()',
                    'User.new()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does user.is_authenticated check?',
                'options': [
                    'Whether user account exists',
                    'Whether user is active',
                    'Whether user is logged in',
                    'Whether user has permissions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method checks if user has a specific permission?',
                'options': [
                    'user.check_perm()',
                    'user.has_permission()',
                    'user.has_perm()',
                    'user.can()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of UserCreationForm?',
                'options': [
                    'Form for updating users',
                    'Form for deleting users',
                    'Form for creating new users',
                    'Form for listing users'
                ],
                'correct_answer': 3
            },
        ]

    # Module 12 Questions - CSV
    def get_module12_questions(self):
        return [
            {
                'question': 'Which Python module is used for CSV operations?',
                'options': [
                    'pandas',
                    'openpyxl',
                    'csv',
                    'xlrd'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you read a CSV file in Python?',
                'options': [
                    'csv.read()',
                    'csv.open()',
                    'csv.reader()',
                    'csv.load()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method writes data to CSV?',
                'options': [
                    'csv.write()',
                    'csv.save()',
                    'csv.writer()',
                    'csv.export()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does DictReader do?',
                'options': [
                    'Reads CSV as list',
                    'Reads CSV as tuple',
                    'Reads CSV rows as dictionaries',
                    'Reads CSV as string'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you create an HTTP response with CSV content?',
                'options': [
                    'JsonResponse',
                    'FileResponse',
                    'StreamingHttpResponse',
                    'HttpResponse with content_type="text/csv"'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which method gets uploaded file from request?',
                'options': [
                    'request.POST["file"]',
                    'request.GET["file"]',
                    'request.file',
                    'request.FILES["file"]'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does DictWriter do?',
                'options': [
                    'Writes lists to CSV',
                    'Writes tuples to CSV',
                    'Writes strings to CSV',
                    'Writes dictionaries to CSV'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which header sets CSV file download?',
                'options': [
                    'Content-Type: text/csv',
                    'Content-Encoding: csv',
                    'Content-Length: csv',
                    'Content-Disposition: attachment; filename="file.csv"'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you handle CSV parsing errors?',
                'options': [
                    'If-else statement',
                    'Validation only',
                    'Error handler',
                    'Try-except block'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of csv.Sniffer?',
                'options': [
                    'Reads CSV files',
                    'Writes CSV files',
                    'Validates CSV data',
                    'Detects CSV dialect and format'
                ],
                'correct_answer': 4
            },
        ]

    # Module 13 Questions - Session Management
    def get_module13_questions(self):
        return [
            {
                'question': 'How do you store data in a session?',
                'options': [
                    'request.session.set("key", value)',
                    'request.session.add("key", value)',
                    'request.session.store("key", value)',
                    'request.session["key"] = value'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you retrieve session data?',
                'options': [
                    'request.session.get("key")',
                    'request.session["key"]',
                    'request.session.retrieve("key")',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which setting controls session expiration?',
                'options': [
                    'SESSION_EXPIRE',
                    'SESSION_TIMEOUT',
                    'SESSION_LIFETIME',
                    'SESSION_COOKIE_AGE'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does request.session.clear() do?',
                'options': [
                    'Deletes the session',
                    'Resets session timeout',
                    'Invalidates session',
                    'Clears all session data'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Where are sessions stored by default in Django?',
                'options': [
                    'In cookies',
                    'In cache',
                    'In files',
                    'In the database'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between sessions and cookies?',
                'options': [
                    'Sessions are encrypted, cookies are not',
                    'Sessions are temporary, cookies are permanent',
                    'No difference',
                    'Sessions stored server-side, cookies client-side'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which setting makes session expire when browser closes?',
                'options': [
                    'SESSION_CLOSE_ON_EXIT = True',
                    'SESSION_BROWSER_CLOSE = True',
                    'SESSION_TEMPORARY = True',
                    'SESSION_EXPIRE_AT_BROWSER_CLOSE = True'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you delete a specific session key?',
                'options': [
                    'request.session.delete("key")',
                    'request.session.remove("key")',
                    'request.session.pop("key")',
                    'del request.session["key"]'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does SESSION_SAVE_EVERY_REQUEST do?',
                'options': [
                    'Saves session once per day',
                    'Saves session on login only',
                    'Never saves session',
                    'Saves session on every request'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which backend stores sessions in database?',
                'options': [
                    'django.sessions.db',
                    'sessions.database',
                    'db.sessions',
                    'django.contrib.sessions.backends.db'
                ],
                'correct_answer': 4
            },
        ]

    # Module 14 Questions - Django Middleware
    def get_module14_questions(self):
        return [
            {
                'question': 'What is middleware in Django?',
                'options': [
                    'Database connection layer',
                    'Template rendering engine',
                    'URL routing system',
                    'Components that process requests and responses'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Where is middleware configured?',
                'options': [
                    'middleware.py file',
                    'urls.py',
                    'views.py',
                    'MIDDLEWARE setting in settings.py'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which method processes requests in middleware?',
                'options': [
                    'handle_request()',
                    'process()',
                    'request()',
                    'process_request()'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which method processes responses in middleware?',
                'options': [
                    'handle_response()',
                    'process()',
                    'response()',
                    'process_response()'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the order of middleware execution?',
                'options': [
                    'Bottom to top for both',
                    'Top to bottom for both',
                    'Random order',
                    'Top to bottom for requests, bottom to top for responses'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which built-in middleware handles CSRF protection?',
                'options': [
                    'django.middleware.security.SecurityMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.middleware.csrf.CsrfViewMiddleware'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does SecurityMiddleware do?',
                'options': [
                    'Validates user authentication',
                    'Encrypts requests',
                    'Blocks malicious requests',
                    'Adds security headers to responses'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which middleware handles user authentication?',
                'options': [
                    'AuthMiddleware',
                    'UserMiddleware',
                    'LoginMiddleware',
                    'AuthenticationMiddleware'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What must a custom middleware class have?',
                'options': [
                    '__init__() method',
                    'handle() method',
                    'process() method',
                    'process_request() or process_response() method'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which middleware processes exceptions?',
                'options': [
                    'handle_exception()',
                    'process_error()',
                    'catch_exception()',
                    'process_exception()'
                ],
                'correct_answer': 4
            },
        ]

    # Module 15 Questions - Database
    def get_module15_questions(self):
        return [
            {
                'question': 'Which setting defines the database engine?',
                'options': [
                    'BACKEND',
                    'DRIVER',
                    'DATABASE_ENGINE',
                    'ENGINE'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the default database in Django?',
                'options': [
                    'MySQL',
                    'PostgreSQL',
                    'Oracle',
                    'SQLite'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which ENGINE value is used for MySQL?',
                'options': [
                    'django.db.backends.sqlite3',
                    'django.db.backends.postgresql',
                    'mysql.connector',
                    'django.db.backends.mysql'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the NAME setting in DATABASES do?',
                'options': [
                    'Specifies the database user',
                    'Specifies the database host',
                    'Specifies the database port',
                    'Specifies the database name'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which command shows SQL for pending migrations?',
                'options': [
                    'python manage.py show_sql',
                    'python manage.py migration_sql',
                    'django-admin sqlmigrate',
                    'python manage.py sqlmigrate appname migration_number'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does migrate --fake do?',
                'options': [
                    'Creates fake migrations',
                    'Deletes migrations',
                    'Validates migrations',
                    'Marks migrations as applied without running them'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which setting specifies database user?',
                'options': [
                    'DB_USER',
                    'DATABASE_USER',
                    'DB_USERNAME',
                    'USER'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does HOST setting specify?',
                'options': [
                    'Web server hostname',
                    'Application hostname',
                    'Static files host',
                    'Database server hostname or IP'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which command shows migration status?',
                'options': [
                    'python manage.py showmigrations',
                    'python manage.py migration_status',
                    'python manage.py list_migrations',
                    'django-admin showmigrations'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does PORT setting specify?',
                'options': [
                    'Database server port number',
                    'Web server port',
                    'Application port',
                    'Static files port'
                ],
                'correct_answer': 1
            },
        ]

