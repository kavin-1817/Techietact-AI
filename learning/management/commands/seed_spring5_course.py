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
                    'Spring Technology Stack',
                    'Spring Tool Suite',
                    'Spring Testing Suite',
                    'Spring Template System'
                ],
                'correct_answer': 2
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
            {
                'question': 'What is the minimum Java version required for Spring 5?',
                'options': [
                    'Java 6',
                    'Java 7',
                    'Java 8',
                    'Java 11'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the main advantage of using Spring Framework?',
                'options': [
                    'It simplifies Java development',
                    'It provides dependency injection',
                    'It supports enterprise features',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which build tool is commonly used with Spring projects?',
                'options': [
                    'Maven',
                    'Gradle',
                    'Ant',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of Spring Tool Suite (STS)?',
                'options': [
                    'An IDE specifically designed for Spring development',
                    'A Spring testing framework',
                    'A Spring deployment tool',
                    'A Spring configuration manager'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What file is used to configure Spring application context?',
                'options': [
                    'application.properties',
                    'spring-config.xml',
                    'Both A and B',
                    'web.xml only'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the core container in Spring Framework?',
                'options': [
                    'Spring Core',
                    'Spring Beans',
                    'Spring Context',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which command is used to create a new Spring project using Spring Initializr?',
                'options': [
                    'spring create project',
                    'spring init',
                    'spring new',
                    'spring start'
                ],
                'correct_answer': 2
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
                    'A way to inject code into classes',
                    'A design pattern where dependencies are injected rather than created',
                    'A database injection technique',
                    'A security vulnerability'
                ],
                'correct_answer': 2
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
            {
                'question': 'What is the traditional way of creating dependencies (before DI)?',
                'options': [
                    'Using new keyword inside classes',
                    'Using factory methods',
                    'Using static methods',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What are the types of Dependency Injection in Spring?',
                'options': [
                    'Constructor injection',
                    'Setter injection',
                    'Field injection',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which type of injection is recommended by Spring?',
                'options': [
                    'Constructor injection',
                    'Setter injection',
                    'Field injection',
                    'All are equally recommended'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does Inversion of Control mean?',
                'options': [
                    'The developer controls object creation',
                    'The framework controls object creation and lifecycle',
                    'Objects control their own creation',
                    'No control over object creation'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the Spring IoC container?',
                'options': [
                    'A container that manages Spring beans',
                    'A container that stores configuration',
                    'A container for web applications',
                    'A database container'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the main interface of Spring IoC container?',
                'options': [
                    'ApplicationContext',
                    'BeanFactory',
                    'Both A and B',
                    'ContainerFactory'
                ],
                'correct_answer': 3
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
                    'To qualify a method',
                    'To specify which bean to inject when multiple candidates exist',
                    'To add validation',
                    'To mark a class as qualified'
                ],
                'correct_answer': 2
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
            {
                'question': 'What happens when autowiring byType finds multiple beans of the same type?',
                'options': [
                    'Spring throws an exception',
                    'Spring uses the first bean found',
                    'Spring uses @Primary bean',
                    'Both A and C'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is @Primary annotation used for?',
                'options': [
                    'To mark a class as primary',
                    'To mark a bean as the primary candidate for autowiring',
                    'To set primary key in database',
                    'To mark a method as primary'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which autowiring mode matches beans by property name?',
                'options': [
                    'byType',
                    'byName',
                    'constructor',
                    'autodetect'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between @Autowired and @Resource?',
                'options': [
                    '@Resource is Spring-specific, @Autowired is JSR-250',
                    '@Autowired is Spring-specific, @Resource is JSR-250',
                    'They are identical',
                    '@Autowired is for fields, @Resource is for methods'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Can you use @Autowired on a constructor?',
                'options': [
                    'No, only on fields',
                    'Yes, it is the recommended way',
                    'No, only on setters',
                    'Yes, but not recommended'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is required=false in @Autowired used for?',
                'options': [
                    'To make dependency optional',
                    'To make dependency required',
                    'To disable autowiring',
                    'To enable lazy loading'
                ],
                'correct_answer': 1
            },
        ]

    # Module 4 Questions - Spring Beans
    def get_module4_questions(self):
        return [
            {
                'question': 'What is a Spring Bean?',
                'options': [
                    'A Java class',
                    'A database entity',
                    'A configuration file',
                    'An object managed by Spring container'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is constructor injection?',
                'options': [
                    'Creating objects using constructor',
                    'Injecting dependencies through constructor',
                    'Calling constructor methods',
                    'Defining constructors in classes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default scope of a Spring bean?',
                'options': [
                    'prototype',
                    'request',
                    'session',
                    'singleton'
                ],
                'correct_answer': 4
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
            {
                'question': 'What is the difference between singleton and prototype scope?',
                'options': [
                    'Prototype creates one instance, singleton creates new instance each time',
                    'They are the same',
                    'Singleton is for web, prototype is for desktop',
                    'Singleton creates one instance, prototype creates new instance each time'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is bean lifecycle in Spring?',
                'options': [
                    'The time a bean exists',
                    'The process of bean creation, initialization, and destruction',
                    'The version of a bean',
                    'The location of a bean'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method is called after bean initialization?',
                'options': [
                    '@PreDestroy',
                    '@Init',
                    '@After',
                    '@PostConstruct'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is @Bean annotation used for?',
                'options': [
                    'To mark a class as a bean',
                    'To define a bean in Java configuration',
                    'To inject a bean',
                    'To destroy a bean'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between @Component and @Bean?',
                'options': [
                    '@Bean is class-level, @Component is method-level',
                    'They are identical',
                    '@Component is for services, @Bean is for repositories',
                    '@Component is class-level, @Bean is method-level'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is lazy initialization of beans?',
                'options': [
                    'Beans are created immediately',
                    'Beans are never created',
                    'Beans are created in background thread',
                    'Beans are created only when first requested'
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
                    'A database framework',
                    'A testing framework',
                    'A security framework',
                    'A web framework built on Spring'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the Model in Spring MVC?',
                'options': [
                    'A database model',
                    'A class model',
                    'A design pattern',
                    'The data/objects passed to the view'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you add Spring MVC support in Eclipse?',
                'options': [
                    'Install Spring Tools plugin',
                    'Add Spring MVC dependencies',
                    'Configure web.xml',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a dynamic web project in Eclipse?',
                'options': [
                    'A project with dynamic content',
                    'A project that changes automatically',
                    'A project with dynamic variables',
                    'A web project that can be deployed to a server'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of web.xml in Spring MVC?',
                'options': [
                    'To configure DispatcherServlet',
                    'To define servlet mappings',
                    'To configure filters',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is DispatcherServlet?',
                'options': [
                    'A database servlet',
                    'A security servlet',
                    'A configuration servlet',
                    'The front controller in Spring MVC'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What file is used for Spring MVC configuration in Java config?',
                'options': [
                    'WebMvcConfigurer',
                    'WebConfig',
                    'SpringConfig',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of @EnableWebMvc annotation?',
                'options': [
                    'To enable web services',
                    'To enable web security',
                    'To enable web sockets',
                    'To enable Spring MVC configuration'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the default view resolver in Spring MVC?',
                'options': [
                    'JstlViewResolver',
                    'ThymeleafViewResolver',
                    'FreeMarkerViewResolver',
                    'InternalResourceViewResolver'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of @RequestMapping annotation?',
                'options': [
                    'To map database tables',
                    'To map configuration files',
                    'To map services',
                    'To map URLs to controller methods'
                ],
                'correct_answer': 4
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
            {
                'question': 'What is the difference between @Controller and @RestController?',
                'options': [
                    '@RestController includes @ResponseBody, @Controller does not',
                    '@Controller includes @ResponseBody, @RestController does not',
                    'They are identical',
                    '@RestController is for web, @Controller is for API'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is @PathVariable used for?',
                'options': [
                    'To extract path variables from URL',
                    'To create path variables',
                    'To validate paths',
                    'To handle path errors'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of Model interface?',
                'options': [
                    'To add attributes to be used in view',
                    'To define data models',
                    'To configure models',
                    'To validate models'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What HTTP methods can be specified in @RequestMapping?',
                'options': [
                    'GET, POST, PUT, DELETE',
                    'GET, POST only',
                    'GET only',
                    'All HTTP methods'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is @GetMapping a shortcut for?',
                'options': [
                    '@RequestMapping(method = RequestMethod.GET)',
                    '@RequestMapping(method = RequestMethod.POST)',
                    '@RequestMapping without method',
                    '@RequestMapping(method = RequestMethod.PUT)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of @ResponseBody annotation?',
                'options': [
                    'To return response directly without view',
                    'To return response body',
                    'To handle response errors',
                    'To validate response'
                ],
                'correct_answer': 1
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
            {
                'question': 'Which tag is used for radio buttons in Spring forms?',
                'options': [
                    '<form:radiobutton>',
                    '<form:radio>',
                    '<form:input type="radio">',
                    '<radio>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag is used for checkboxes in Spring forms?',
                'options': [
                    '<form:checkbox>',
                    '<form:check>',
                    '<form:input type="checkbox">',
                    '<checkbox>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag is used for text areas in Spring forms?',
                'options': [
                    '<form:textarea>',
                    '<form:text>',
                    '<form:area>',
                    '<textarea>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of path attribute in form tags?',
                'options': [
                    'To bind form field to model property',
                    'To specify URL path',
                    'To define file path',
                    'To set form path'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What happens if modelAttribute is not set in form:form?',
                'options': [
                    'Form will not bind to model',
                    'Form will use default model',
                    'Form will throw error',
                    'Form will work normally'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you bind a form to a model object?',
                'options': [
                    'Using modelAttribute in form:form',
                    'Using @ModelAttribute in controller',
                    'Both A and B',
                    'Using @RequestParam'
                ],
                'correct_answer': 3
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
                    'All of the above',
                    '/static',
                    '/public'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <mvc:resources> tag?',
                'options': [
                    'To map static resources to URLs',
                    'To load resources dynamically',
                    'To validate resources',
                    'To cache resources'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the mapping attribute in <mvc:resources> used for?',
                'options': [
                    'To specify URL pattern for resources',
                    'To map resources to database',
                    'To map resources to services',
                    'To validate resource mapping'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the location attribute in <mvc:resources> used for?',
                'options': [
                    'To specify physical location of resources',
                    'To specify URL location',
                    'To specify database location',
                    'To specify service location'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you add CSS files to Spring MVC views?',
                'options': [
                    'Using <link> tag with proper resource mapping',
                    'Using @Import annotation',
                    'Using @Resource annotation',
                    'Using <style> tag only'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is STS3 support in Eclipse?',
                'options': [
                    'Spring Testing Suite 3',
                    'Spring Tool Suite 3 plugin for Eclipse',
                    'Spring Template System 3',
                    'Spring Technology Stack 3'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of ResourceHandlerRegistry?',
                'options': [
                    'To register database resources',
                    'To register static resource handlers in Java config',
                    'To register service resources',
                    'To register validation resources'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you configure static resources in Java-based configuration?',
                'options': [
                    'Using @ResourceHandler annotation',
                    'Using addResourceHandlers in WebMvcConfigurer',
                    'Using ResourceConfig class',
                    'Using web.xml only'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the benefit of using resource mapping?',
                'options': [
                    'Better organization and caching of static resources',
                    'All of the above',
                    'Faster resource loading',
                    'Better security'
                ],
                'correct_answer': 2
            },
        ]

    # Module 9 Questions - Spring Form Validations
    def get_module9_questions(self):
        return [
            {
                'question': 'Which annotation is used for validation in Spring?',
                'options': [
                    '@Valid',
                    'All of the above',
                    '@NotNull',
                    '@Size'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is Hibernate Validator?',
                'options': [
                    'An ORM framework',
                    'A validation framework',
                    'A database',
                    'A web framework'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which annotation is used to show validation errors?',
                'options': [
                    '<errors:form>',
                    '<form:errors>',
                    '<validation:errors>',
                    '<spring:errors>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is ModelMap?',
                'options': [
                    'A database mapping',
                    'A simplified way to pass data to views',
                    'A configuration map',
                    'A validation map'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you configure error messages from properties file?',
                'options': [
                    'Using MessageSource',
                    'All of the above',
                    'Using ResourceBundle',
                    'Using Properties file'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is @Valid annotation used for?',
                'options': [
                    'To validate forms',
                    'To trigger validation on model object',
                    'To validate requests',
                    'All of the above'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is BindingResult used for?',
                'options': [
                    'To bind form data',
                    'To hold validation errors',
                    'To bind model data',
                    'To validate results'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What happens if validation fails in Spring MVC?',
                'options': [
                    'BindingResult contains errors',
                    'Form is redisplayed with errors',
                    'Both A and B',
                    'Exception is thrown'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which annotation validates string length?',
                'options': [
                    '@Size',
                    'Both A and B',
                    '@Length',
                    '@Min'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is @InitBinder used for?',
                'options': [
                    'To bind form data',
                    'To initialize data binder',
                    'To validate data',
                    'To configure validation'
                ],
                'correct_answer': 2
            },
        ]

    # Module 10 Questions - Spring JDBC XML Configuration
    def get_module10_questions(self):
        return [
            {
                'question': 'What is Spring JDBC?',
                'options': [
                    'A database',
                    'A web framework',
                    'A JDBC abstraction framework',
                    'A testing framework'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a DAO?',
                'options': [
                    'Database Access Object',
                    'Data Application Object',
                    'Data Access Object',
                    'Database Application Object'
                ],
                'correct_answer': 3
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
                    'Using <datasource> tag',
                    'Using @DataSource annotation',
                    'Using <bean> tag with DataSource class',
                    'Using properties file only'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the advantage of using JdbcTemplate?',
                'options': [
                    'Reduces boilerplate JDBC code',
                    'Handles exceptions automatically',
                    'All of the above',
                    'Manages connections'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is RowMapper used for?',
                'options': [
                    'To map objects to rows',
                    'To map tables',
                    'To map database rows to objects',
                    'To map columns'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of DriverManagerDataSource?',
                'options': [
                    'To manage database drivers',
                    'To configure database',
                    'To create DataSource for simple JDBC connections',
                    'To validate database'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between query() and queryForObject()?',
                'options': [
                    'queryForObject() returns list, query() returns single object',
                    'They are identical',
                    'query() returns list, queryForObject() returns single object',
                    'query() is for updates, queryForObject() is for selects'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is NamedParameterJdbcTemplate?',
                'options': [
                    'JdbcTemplate with positional parameters',
                    'A different JDBC framework',
                    'JdbcTemplate with named parameters',
                    'A database template'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of @Repository annotation in DAO?',
                'options': [
                    'To mark class as service',
                    'To mark class as controller',
                    'To mark class as repository and enable exception translation',
                    'To mark class as component'
                ],
                'correct_answer': 3
            },
        ]

    # Module 11 Questions - Spring JDBC Annotation Configuration
    def get_module11_questions(self):
        return [
            {
                'question': 'Which annotation is used for JDBC configuration?',
                'options': [
                    '@EnableJdbc',
                    '@JdbcConfiguration',
                    '@Configuration',
                    'Both A and B'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does JAAS stand for?',
                'options': [
                    'Java Application and Authorization Service',
                    'Java Authentication and Access Service',
                    'Java Authentication and Authorization Service',
                    'Java Application and Access Service'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which annotation is used for repository classes?',
                'options': [
                    '@Component',
                    '@Service',
                    '@Repository',
                    'All of the above'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between authentication and authorization?',
                'options': [
                    'Authorization verifies identity, authentication checks permissions',
                    'They are the same',
                    'Authentication verifies identity, authorization checks permissions',
                    'Authentication is for users, authorization is for admins'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you configure DataSource using annotations?',
                'options': [
                    'Using @DataSource annotation',
                    'Using @ConfigureDataSource',
                    'Using @Bean method with DataSource',
                    'Using @Resource annotation'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is @Transactional used for?',
                'options': [
                    'To configure transactions',
                    'To validate transactions',
                    'To manage database transactions',
                    'To log transactions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of @EnableTransactionManagement?',
                'options': [
                    'To enable programmatic transactions',
                    'To enable transaction logging',
                    'To enable declarative transaction management',
                    'To enable transaction validation'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a user role in Spring security context?',
                'options': [
                    'A user type',
                    'A user category',
                    'A permission level assigned to a user',
                    'A user group'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of addUser functionality?',
                'options': [
                    'To add new users to the system',
                    'To add user roles',
                    'To add user permissions',
                    'To add user data'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is exception translation in Spring JDBC?',
                'options': [
                    'Converting database exceptions to Spring exceptions',
                    'Translating error messages',
                    'Translating SQL queries',
                    'Translating database schemas'
                ],
                'correct_answer': 1
            },
        ]

