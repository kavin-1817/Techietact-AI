"""
Management command to seed Spring 5 course with complete modules and topics
Run with: python manage.py seed_spring5_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Spring 5 course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Spring 5 course
        course, created = Course.objects.get_or_create(
            title='SPRING 5 COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete Spring 5 framework course covering IoC, Dependency Injection, Autowiring, Spring Beans, Spring MVC, Form elements, Validations, Spring JDBC, and more.',
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
                self.stdout.write(self.style.SUCCESS(f'  Created module: {module.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Updated module: {module.title}'))
            
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Spring 5 course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Getting Started with Spring 5',
                'summary': 'Introduction to Spring 5 framework. Learn to download and install required software, set up development environment, and create your first Spring project.',
                'learning_objectives': 'Understand Spring 5 framework\nDownload and install required software\nSet up development environment for Mac, Linux, and Windows\nCreate first Spring project on STS (Spring Tool Suite)',
                'topics': "Let's start with Spring 5\nDownload required software\nInstalling required software\nSetup process for Mac and Linux\nFirst project setup on STS",
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Inversion of Control (IoC) & Dependency Injection (DI)',
                'summary': 'Learn the core concepts of Spring framework: Inversion of Control and Dependency Injection. Understand how Spring manages object dependencies.',
                'learning_objectives': 'Understand Inversion of Control (IoC)\nMaster Dependency Injection (DI)\nLearn how Spring manages dependencies\nUnderstand the benefits of DI',
                'topics': 'Dependency Injection\nUnderstanding Dependency Injection',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Autowiring in Spring',
                'summary': 'Learn Spring autowiring mechanism. Understand different autowiring scenarios and how to use @Qualifier annotation for fine-grained control.',
                'learning_objectives': 'Understand autowiring in Spring\nLearn different autowiring scenarios\nUse @Qualifier annotation\nMaster dependency resolution',
                'topics': 'Autowire introduction\nAutowire scenarios\nQualifier annotation',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Spring Beans',
                'summary': 'Deep dive into Spring Beans. Learn about bean lifecycle, constructor injection, and bean configuration.',
                'learning_objectives': 'Understand Spring Beans\nLearn bean lifecycle\nMaster constructor injection\nConfigure and manage beans',
                'topics': 'Spring Bean\nConstructor Injection',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'IDE Setup Steps for Spring Development',
                'summary': 'Set up your IDE for Spring development. Learn to create Spring projects in IntelliJ and Eclipse, add Spring MVC support, and work with dynamic web projects.',
                'learning_objectives': 'Set up Spring project in IntelliJ\nAdd Spring MVC support in Eclipse\nCreate simple dynamic web project\nUnderstand model in web project',
                'topics': 'Spring project on IntelliJ\nAdding Spring MVC support in Eclipse\nSimple dynamic web project\nModel in web project',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Spring MVC',
                'summary': 'Introduction to Spring MVC framework. Learn minimal setup, create basic forms, use @RequestParam and Model, work with ModelAndView, and iterate over data.',
                'learning_objectives': 'Set up Spring MVC minimal configuration\nCreate basic forms with Spring MVC\nUse @RequestParam and Model\nWork with ModelAndView\nIterate over data using foreach',
                'topics': 'Spring MVC minimal setup\nBasic form with Spring MVC\nRequestParam and Model\nModelAndView\nforeach on data',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Spring Form Elements',
                'summary': 'Learn to work with various Spring form elements including input fields, radio buttons, dropdown lists, text areas, and checkboxes.',
                'learning_objectives': 'Set up Eclipse project for forms\nGet started with Spring forms\nUse input fields\nImplement radio buttons\nCreate dropdown lists\nWork with text areas\nUse checkboxes',
                'topics': 'Setting up Eclipse project\nGetting started with forms\nInput fields\nRadio buttons\nRadio buttons with background\nDropdown lists\nText area\nCheckboxes',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Styling & External Resources',
                'summary': 'Learn to add styling and external resources to Spring MVC applications. Add STS3 support, external resources, and stylesheets.',
                'learning_objectives': 'Add STS3 support into Eclipse\nAdd external resources to Spring MVC\nAdd stylesheets\nStyle Spring MVC applications',
                'topics': 'Adding STS3 support into Eclipse\nAdding external resources\nAdding stylesheet',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Spring Form Validations',
                'summary': 'Master Spring form validations. Learn HTML validation, Hibernate Validator, repopulate form data, show error messages, validation rules, configurable messages, and exception handling.',
                'learning_objectives': 'Implement form validation using HTML\nUse Hibernate Validator\nRepopulate form data\nUse ModelMap to simplify controller\nShow error messages\nDefine validation rules\nConfigure error messages from properties file\nHandle exceptions',
                'topics': 'Form validation using HTML\nHibernate Validator introduction\nRepopulate form data\nModelMap (simplifying controller)\nShow error messages\nValidation rules\nConfigurable error messages from properties file\nException handling',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Spring JDBC – XML Configuration',
                'summary': 'Learn Spring JDBC with XML configuration. Set up Maven, understand architecture, create DAO, configure beans using XML, and read from database.',
                'learning_objectives': 'Set up Maven for Hibernate and MySQL\nUnderstand Spring JDBC architecture\nLearn methods of mapping\nSet up project\nAdd Data Access Object (DAO)\nDefine beans using XML configuration\nRead from database\nDisplay information on webpage',
                'topics': 'Maven setup for Hibernate and MySQL\nAlternate Eclipse environment\nDynamic web project approach\nInstalling MySQL\nSQL Workbench\nUnderstanding the Architecture\nArchitecture (Document)\nMethods of Mapping\nMethods of Mapping (Document)\nSetting up project\nAdding Data Access Object (DAO)\nDefining Beans (XML configuration)\nReading from database\nShowing information on webpage',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'Spring JDBC – Annotation Configuration',
                'summary': 'Learn Spring JDBC with annotation-based configuration. Define annotations, add user functionality, implement validation, user roles, authentication, and authorization with JAAS overview.',
                'learning_objectives': 'Define annotations for Spring JDBC\nGet things in place\nAdd "Add User" link\nUpdate controller\nAdd validation\nAdd user functionality\nUnderstand user roles & authentication\nLearn overview of JAAS\nImplement user authorization',
                'topics': 'Defining annotations\nGetting things in place\nAdding "Add User" link\nWalkthrough\nUpdating the controller\nAdding validation\nAdding user\nUser roles & authentication\nOverview of JAAS\nUser authorization',
                'questions': self.get_module11_questions(),
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
            
            # Create options
            for opt_order, option_text in enumerate(question_data['options'], start=1):
                is_correct = (opt_order == question_data['correct_answer'])
                QuizOption.objects.create(
                    question=question,
                    option_text=option_text,
                    is_correct=is_correct,
                    order=opt_order
                )
            count += 1
        return count

    # Module 1 Questions - Getting Started with Spring 5
    def get_module1_questions(self):
        return [
            {
                'question': 'What is Spring Framework?',
                'options': [
                    'A Java application framework',
                    'A database',
                    'A web server',
                    'A programming language'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does STS stand for?',
                'options': [
                    'Spring Tool Suite',
                    'Spring Technology Stack',
                    'Spring Testing Suite',
                    'Spring Template System'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which IDE is commonly used for Spring development?',
                'options': [
                    'Eclipse/STS',
                    'IntelliJ IDEA',
                    'NetBeans',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 2 Questions - IoC & Dependency Injection
    def get_module2_questions(self):
        return [
            {
                'question': 'What does IoC stand for?',
                'options': [
                    'Inversion of Control',
                    'Injection of Components',
                    'Integration of Classes',
                    'Interface of Components'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is Dependency Injection?',
                'options': [
                    'A design pattern where dependencies are injected rather than created',
                    'A way to inject code into classes',
                    'A database injection technique',
                    'A security vulnerability'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What are the benefits of Dependency Injection?',
                'options': [
                    'Loose coupling',
                    'Easier testing',
                    'Better maintainability',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which annotation is used for dependency injection in Spring?',
                'options': [
                    '@Autowired',
                    '@Inject',
                    '@Resource',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 3 Questions - Autowiring in Spring
    def get_module3_questions(self):
        return [
            {
                'question': 'What is autowiring in Spring?',
                'options': [
                    'Automatic dependency injection by Spring container',
                    'Automatic code generation',
                    'Automatic database connection',
                    'Automatic error handling'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the default autowiring mode in Spring?',
                'options': [
                    'byType',
                    'byName',
                    'constructor',
                    'no (no autowiring)'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is @Qualifier annotation used for?',
                'options': [
                    'To specify which bean to inject when multiple candidates exist',
                    'To qualify a method',
                    'To add validation',
                    'To mark a class as qualified'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which autowiring mode uses constructor parameters?',
                'options': [
                    'byType',
                    'byName',
                    'constructor',
                    'autodetect'
                ],
                'correct_answer': 3
            },
        ]

    # Module 4 Questions - Spring Beans
    def get_module4_questions(self):
        return [
            {
                'question': 'What is a Spring Bean?',
                'options': [
                    'An object managed by Spring container',
                    'A Java class',
                    'A database entity',
                    'A configuration file'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is constructor injection?',
                'options': [
                    'Injecting dependencies through constructor',
                    'Creating objects using constructor',
                    'Calling constructor methods',
                    'Defining constructors in classes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the default scope of a Spring bean?',
                'options': [
                    'singleton',
                    'prototype',
                    'request',
                    'session'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to define a Spring bean?',
                'options': [
                    '@Component',
                    '@Service',
                    '@Repository',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 5 Questions - IDE Setup
    def get_module5_questions(self):
        return [
            {
                'question': 'What is Spring MVC?',
                'options': [
                    'A web framework built on Spring',
                    'A database framework',
                    'A testing framework',
                    'A security framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the Model in Spring MVC?',
                'options': [
                    'The data/objects passed to the view',
                    'A database model',
                    'A class model',
                    'A design pattern'
                ],
                'correct_answer': 1
            },
        ]

    # Module 6 Questions - Spring MVC
    def get_module6_questions(self):
        return [
            {
                'question': 'What does MVC stand for?',
                'options': [
                    'Model View Controller',
                    'Model View Component',
                    'Multiple View Controller',
                    'Main View Controller'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is @RequestParam used for?',
                'options': [
                    'To bind request parameters to method parameters',
                    'To create request parameters',
                    'To validate requests',
                    'To handle responses'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is ModelAndView?',
                'options': [
                    'A class that holds both model data and view name',
                    'A database model',
                    'A view template',
                    'A controller class'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to mark a class as a Spring MVC controller?',
                'options': [
                    '@Controller',
                    '@RestController',
                    'Both A and B',
                    '@Component'
                ],
                'correct_answer': 3
            },
        ]

    # Module 7 Questions - Spring Form Elements
    def get_module7_questions(self):
        return [
            {
                'question': 'Which Spring tag library is used for forms?',
                'options': [
                    'spring:form',
                    'form:form',
                    'sf:form',
                    'spring-form:form'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which attribute is required for form:form tag?',
                'options': [
                    'modelAttribute',
                    'action',
                    'method',
                    'All of the above'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag is used for input fields in Spring forms?',
                'options': [
                    '<form:input>',
                    '<form:textfield>',
                    '<form:field>',
                    '<input>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag is used for dropdown lists in Spring forms?',
                'options': [
                    '<form:select>',
                    '<form:dropdown>',
                    '<form:list>',
                    '<select>'
                ],
                'correct_answer': 1
            },
        ]

    # Module 8 Questions - Styling & External Resources
    def get_module8_questions(self):
        return [
            {
                'question': 'How do you add external resources (CSS, JS) in Spring MVC?',
                'options': [
                    'Using <mvc:resources> in configuration',
                    'Placing files in webapp/resources',
                    'Both A and B',
                    'Using @Resource annotation'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the default location for static resources in Spring MVC?',
                'options': [
                    '/resources',
                    '/static',
                    '/public',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 9 Questions - Spring Form Validations
    def get_module9_questions(self):
        return [
            {
                'question': 'Which annotation is used for validation in Spring?',
                'options': [
                    '@Valid',
                    '@NotNull',
                    '@Size',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is Hibernate Validator?',
                'options': [
                    'A validation framework',
                    'An ORM framework',
                    'A database',
                    'A web framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to show validation errors?',
                'options': [
                    '<form:errors>',
                    '<errors:form>',
                    '<validation:errors>',
                    '<spring:errors>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is ModelMap?',
                'options': [
                    'A simplified way to pass data to views',
                    'A database mapping',
                    'A configuration map',
                    'A validation map'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you configure error messages from properties file?',
                'options': [
                    'Using MessageSource',
                    'Using ResourceBundle',
                    'Using Properties file',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 10 Questions - Spring JDBC XML Configuration
    def get_module10_questions(self):
        return [
            {
                'question': 'What is Spring JDBC?',
                'options': [
                    'A JDBC abstraction framework',
                    'A database',
                    'A web framework',
                    'A testing framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a DAO?',
                'options': [
                    'Data Access Object',
                    'Database Access Object',
                    'Data Application Object',
                    'Database Application Object'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which class is used for JDBC operations in Spring?',
                'options': [
                    'JdbcTemplate',
                    'JdbcDaoSupport',
                    'Both A and B',
                    'Connection'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you configure DataSource in XML?',
                'options': [
                    'Using <bean> tag with DataSource class',
                    'Using <datasource> tag',
                    'Using @DataSource annotation',
                    'Using properties file only'
                ],
                'correct_answer': 1
            },
        ]

    # Module 11 Questions - Spring JDBC Annotation Configuration
    def get_module11_questions(self):
        return [
            {
                'question': 'Which annotation is used for JDBC configuration?',
                'options': [
                    '@Configuration',
                    '@EnableJdbc',
                    '@JdbcConfiguration',
                    'Both A and B'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does JAAS stand for?',
                'options': [
                    'Java Authentication and Authorization Service',
                    'Java Application and Authorization Service',
                    'Java Authentication and Access Service',
                    'Java Application and Access Service'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used for repository classes?',
                'options': [
                    '@Repository',
                    '@Component',
                    '@Service',
                    'All of the above'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between authentication and authorization?',
                'options': [
                    'Authentication verifies identity, authorization checks permissions',
                    'Authorization verifies identity, authentication checks permissions',
                    'They are the same',
                    'Authentication is for users, authorization is for admins'
                ],
                'correct_answer': 1
            },
        ]

