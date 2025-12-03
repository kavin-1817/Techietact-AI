"""
Management command to seed JSP & Servlets course with complete modules and topics
Run with: python manage.py seed_jsp_servlets_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with JSP & Servlets course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get JSP & Servlets course
        course, created = Course.objects.get_or_create(
            title='JSP & SERVLETS COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete JSP & Servlets course covering web application development, forms, Java Beans, session management, JSTL tags, internationalization, database connectivity, and file uploads.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated JSP & Servlets course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Web Application Introduction',
                'summary': 'Introduction to JSP and Servlets. Learn about project setup, servlet lifecycle, JSP elements, deployment descriptors, MVC pattern, and basic application structure.',
                'learning_objectives': 'Understand web application basics\nSet up JSP and Servlets project\nLearn servlet lifecycle\nMaster JSP elements (expression, scriptlets, declarations, comments, directives)\nUnderstand deployment descriptors and annotations\nLearn MVC pattern\nBuild basic MVC application',
                'topics': 'Before we start with JSP and Servlets\nRequirements to get started\nProject setup\nHello Servlets\nHello JSP\nServlets life cycle\nJSP expression element\nJSP scriptlets element\nJSP declarations element\nJSP comment element\nJSP directive element\nMCQs and Predict the Output\nDeployment descriptor & annotations\nJSP configuration in deployment descriptor\nReading URL parameter(s)\nInclude file(s) in JSP page\nImport class into JSP page\nForward and redirect under JSP\nMVC overview\nExercise – Basic redirection using servlet\nBasic application based on MVC',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Forms in JSP & Servlets',
                'summary': 'Learn to create and handle web forms in JSP and Servlets. Understand form elements, form processing, and basic form validations.',
                'learning_objectives': 'Understand forms overview\nLearn form elements\nCreate forms in JSP\nHandle forms in Servlets\nImplement basic form validations',
                'topics': 'Forms overview\nForm elements\nForms under JSP\nForms under Servlets\nBasic form validations',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Java Beans in JSP',
                'summary': 'Introduction to Java Beans in JSP. Learn about bean scope types (session, page, application, request) and using beans with web forms.',
                'learning_objectives': 'Understand Java Beans overview\nLearn bean scope types (session, page, application)\nUnderstand request scope\nUse beans with web forms',
                'topics': 'Beans overview\nBean scope types (session, page, application)\nRequest scope\nBeans with web forms',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Session Management',
                'summary': 'Learn session management in JSP. Understand cookies, session attributes, user logout, servlet filters, and handling sessions without cookies.',
                'learning_objectives': 'Understand session management in JSP\nLearn about cookies\nPerform read & write cookie operations\nImplement user logout (via cookie and session attribute)\nOrganize application structure\nFix redirect & forward links\nHandle session without cookies\nUnderstand servlet filters',
                'topics': 'Session under JSP overview\nIntroduction to cookies\nRead & write cookie operations\nUser logout (via cookie)\nUser logout (via session attribute)\nOrganizing application\nFixing redirect & forward links\nHandling session without cookies\nServlet filters',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'JSTL – Core Tags',
                'summary': 'Introduction to JSTL (JSP Standard Tag Library) core tags. Learn set, remove, decision-making, loops, import, URL, redirect, and catch tags.',
                'learning_objectives': 'Set up JSTL\nUse JSTL set & remove tags\nRead from Bean using Expression Language (EL)\nMake decisions under JSTL\nUse JSTL Choose & When tags\nImplement JSTL for loop\nUse JSTL forEach loop\nUnderstand JSTL forTokens tag\nUse JSTL import & param tags\nImplement JSTL URL & redirect tags\nHandle errors with JSTL catch tag',
                'topics': 'JSTL setup\nJSTL set & remove tags\nReading from Bean using Expression Language (EL)\nDecision making under JSTL\nJSTL Choose & When tags\nMCQs and Predict the Output\nJSTL for loop\nJSTL forEach loop\nJSTL forTokens tag\nJSTL import & param tags\nJSTL URL & redirect tags\nJSTL catch tag',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'JSP & JSTL – Good to Know',
                'summary': 'Important information about JSP and JSTL project files, execution, and best practices.',
                'learning_objectives': 'Understand good to know information\nLearn about project files\nUnderstand execution of the project',
                'topics': 'Good to know information\nProject files\nExecution of the project',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'JSTL – Function Tags',
                'summary': 'Learn JSTL function tags including length, trim, escape XML, split, join, and other advanced functions.',
                'learning_objectives': 'Use JSTL length functions\nApply JSTL trim & escape XML functions\nLearn more JSTL functions\nMaster JSTL advanced functions\nUse JSTL Split & Join functions',
                'topics': 'JSTL length functions\nJSTL trim & escape XML functions\nJSTL more functions\nJSTL advanced functions\nJSTL Split & Join functions',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Internationalization (I18N)',
                'summary': 'Introduction to internationalization (I18N) in web applications. Learn about locale and document localization.',
                'learning_objectives': 'Understand overview of I18N\nLearn about locale\nUnderstand locale (document)',
                'topics': 'Overview of I18N\nLocale\nLocale (document)',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'JSTL I18N Project',
                'summary': 'Build a complete I18N project using JSTL. Set up internationalization, add properties files, and integrate with website.',
                'learning_objectives': 'Set up I18N project\nAdd properties files\nIntegrate I18N with website',
                'topics': 'Setting up\nAdding properties\nIntegration with website (I18N)',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'JSTL Formatting Tags',
                'summary': 'Learn JSTL formatting tags for dates and numbers. Format data according to different locales and patterns.',
                'learning_objectives': 'Format date & number using JSTL\nApply locale-specific formatting',
                'topics': 'Formatting date & number',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'Building Custom Tags',
                'summary': 'Learn to build custom JSP tags. Create reusable tag libraries for your web applications.',
                'learning_objectives': 'Build custom tags\nCreate reusable tag libraries',
                'topics': 'Building custom tag',
                'questions': self.get_module11_questions(),
            },
            {
                'order': 12,
                'title': 'Web Template Integration',
                'summary': 'Learn to integrate web templates with JSP projects. Extract header and footer from templates and integrate using JSTL.',
                'learning_objectives': 'Extract header & footer from template\nIntegrate template with project\nIntegrate template using JSTL',
                'topics': 'Extracting header & footer from template\nIntegrate template with project\nIntegrate template using JSTL',
                'questions': self.get_module12_questions(),
            },
            {
                'order': 13,
                'title': 'Revisiting Servlets',
                'summary': 'Deep dive into servlets. Learn servlet initialization, advanced servlet concepts, and best practices.',
                'learning_objectives': 'Understand servlet initialization\nLearn more about servlets\nMaster advanced servlet concepts',
                'topics': 'Servlet initialization\nUnderstanding more about Servlet',
                'questions': self.get_module13_questions(),
            },
            {
                'order': 14,
                'title': 'Database Connectivity (JSP + Servlets)',
                'summary': 'Learn to connect JSP and Servlets with databases. Set up JNDI, configure database connections, and test connectivity.',
                'learning_objectives': 'Set up tools required\nUse workbench\nSet up JNDI\nTest database connection',
                'topics': 'Setting tools required\nUse of workbench\nSetting up JNDI\nTesting connection',
                'questions': self.get_module14_questions(),
            },
            {
                'order': 15,
                'title': 'Listing Data on Webpage',
                'summary': 'Learn to retrieve and display database records on web pages. Use include directives and organize data presentation.',
                'learning_objectives': 'Set up data listing\nList data on webpage\nUse include directive',
                'topics': 'Setting up\nListing data on webpage\nUsing include directive',
                'questions': self.get_module15_questions(),
            },
            {
                'order': 16,
                'title': 'Add Records to Database',
                'summary': 'Implement functionality to add records to database. Create forms, validate user inputs, apply business rules, and finalize the feature.',
                'learning_objectives': 'Implement form for adding records\nValidate user inputs\nApply business rules\nOrganize application structure\nFinalize add record feature',
                'topics': 'Form implementation\nValidate user inputs\nBusiness rules\nOrganizing application\nFinalizing feature',
                'questions': self.get_module16_questions(),
            },
            {
                'order': 17,
                'title': 'Update Records',
                'summary': 'Implement update functionality for database records. Upgrade the list view, update controller, populate forms, and implement update operations.',
                'learning_objectives': 'Upgrade the list view\nUpdate controller\nPopulate form with existing data\nImplement update functionality',
                'topics': 'Upgrading the list\nUpdating controller\nPopulating form\nUpdate functionality',
                'questions': self.get_module17_questions(),
            },
            {
                'order': 18,
                'title': 'Delete Records',
                'summary': 'Implement delete functionality for database records. Upgrade the list view and implement delete operations.',
                'learning_objectives': 'Upgrade list view\nImplement delete functionality',
                'topics': 'Upgrading list\nDelete functionality',
                'questions': self.get_module18_questions(),
            },
            {
                'order': 19,
                'title': 'Add JSTL Support',
                'summary': 'Add JSTL support to existing database operations. Enhance the application with JSTL tags.',
                'learning_objectives': 'Add JSTL support to database operations\nEnhance application with JSTL',
                'topics': 'Add JSTL support',
                'questions': self.get_module19_questions(),
            },
            {
                'order': 20,
                'title': 'Image/File Upload',
                'summary': 'Implement image and file upload functionality. Create upload forms, handle image files, and upload to file system.',
                'learning_objectives': 'Create image upload form\nHandle image files\nUpload files to file system',
                'topics': 'Image upload form\nHandle image files\nUpload to file system',
                'questions': self.get_module20_questions(),
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

    # Module 1 Questions - Web Application Introduction
    def get_module1_questions(self):
        return [
            {
                'question': 'What does JSP stand for?',
                'options': [
                    'Java Server Pages',
                    'Java Service Protocol',
                    'Java Script Pages',
                    'Java Servlet Pages'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method is called first in the servlet lifecycle?',
                'options': [
                    'service()',
                    'init()',
                    'doGet()',
                    'destroy()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which JSP element is used to output values?',
                'options': [
                    '<%! %>',
                    '<%= %>',
                    '<% %>',
                    '<%@ %>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the deployment descriptor file in Java web applications?',
                'options': [
                    'web.xml',
                    'deploy.xml',
                    'config.xml',
                    'application.xml'
                ],
                'correct_answer': 1
            },
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
        ]

    # Module 2 Questions - Forms in JSP & Servlets
    def get_module2_questions(self):
        return [
            {
                'question': 'Which HTML form method is commonly used with servlets?',
                'options': [
                    'GET',
                    'POST',
                    'Both GET and POST',
                    'PUT'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you retrieve form data in a servlet?',
                'options': [
                    'request.getParameter()',
                    'request.getAttribute()',
                    'request.getSession()',
                    'request.getContext()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSP element is used to include form validation?',
                'options': [
                    'JSP scriptlets',
                    'JSP expressions',
                    'JSP declarations',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the default method for HTML forms?',
                'options': [
                    'GET',
                    'POST',
                    'PUT',
                    'DELETE'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions - Java Beans in JSP
    def get_module3_questions(self):
        return [
            {
                'question': 'What is the default scope of a Java Bean in JSP?',
                'options': [
                    'page',
                    'request',
                    'session',
                    'application'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSP action tag is used to use a Java Bean?',
                'options': [
                    '<jsp:useBean>',
                    '<jsp:bean>',
                    '<jsp:setBean>',
                    '<jsp:getBean>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which scope makes a bean available across the entire application?',
                'options': [
                    'page',
                    'request',
                    'session',
                    'application'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is required for a class to be a Java Bean?',
                'options': [
                    'Public no-arg constructor',
                    'Private fields with getters/setters',
                    'Implements Serializable',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 4 Questions - Session Management
    def get_module4_questions(self):
        return [
            {
                'question': 'How do you get a session object in a servlet?',
                'options': [
                    'request.getSession()',
                    'response.getSession()',
                    'application.getSession()',
                    'context.getSession()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the default lifetime of a session?',
                'options': [
                    '5 minutes',
                    '30 minutes',
                    '1 hour',
                    'Until browser closes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method is used to invalidate a session?',
                'options': [
                    'session.remove()',
                    'session.invalidate()',
                    'session.delete()',
                    'session.clear()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a servlet filter used for?',
                'options': [
                    'Filter requests and responses',
                    'Filter database queries',
                    'Filter HTML content',
                    'Filter CSS styles'
                ],
                'correct_answer': 1
            },
        ]

    # Module 5 Questions - JSTL Core Tags
    def get_module5_questions(self):
        return [
            {
                'question': 'What does JSTL stand for?',
                'options': [
                    'Java Standard Tag Library',
                    'JSP Standard Tag Library',
                    'Java Servlet Tag Library',
                    'JSP Servlet Tag Library'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which JSTL tag is used for conditional logic?',
                'options': [
                    '<c:if>',
                    '<c:choose>',
                    '<c:when>',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which JSTL tag is used for iteration?',
                'options': [
                    '<c:for>',
                    '<c:forEach>',
                    '<c:loop>',
                    '<c:iterate>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is Expression Language (EL) used for?',
                'options': [
                    'Accessing Java objects',
                    'Performing calculations',
                    'Calling methods',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 6 Questions - JSP & JSTL Good to Know
    def get_module6_questions(self):
        return [
            {
                'question': 'What file contains JSP configuration?',
                'options': [
                    'web.xml',
                    'jsp-config.xml',
                    'application.xml',
                    'Both web.xml and jsp-config.xml'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Where are compiled JSP files stored?',
                'options': [
                    'WEB-INF/classes',
                    'WEB-INF/jsp',
                    'Work directory of the server',
                    'Root directory'
                ],
                'correct_answer': 3
            },
        ]

    # Module 7 Questions - JSTL Function Tags
    def get_module7_questions(self):
        return [
            {
                'question': 'Which JSTL function returns the length of a string?',
                'options': [
                    'fn:length()',
                    'fn:size()',
                    'fn:count()',
                    'fn:len()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function is used to remove whitespace?',
                'options': [
                    'fn:trim()',
                    'fn:strip()',
                    'fn:remove()',
                    'fn:clean()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function splits a string?',
                'options': [
                    'fn:split()',
                    'fn:divide()',
                    'fn:separate()',
                    'fn:break()'
                ],
                'correct_answer': 1
            },
        ]

    # Module 8 Questions - Internationalization (I18N)
    def get_module8_questions(self):
        return [
            {
                'question': 'What does I18N stand for?',
                'options': [
                    'Internationalization',
                    'Integration',
                    'Internet',
                    'Interface'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a Locale object used for?',
                'options': [
                    'Language and country settings',
                    'Database location',
                    'Server location',
                    'File location'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which file extension is used for locale-specific properties?',
                'options': [
                    '.txt',
                    '.properties',
                    '.config',
                    '.locale'
                ],
                'correct_answer': 2
            },
        ]

    # Module 9 Questions - JSTL I18N Project
    def get_module9_questions(self):
        return [
            {
                'question': 'Which JSTL library is used for I18N?',
                'options': [
                    'Core',
                    'Formatting',
                    'I18N',
                    'SQL'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which tag is used to set the locale?',
                'options': [
                    '<fmt:setLocale>',
                    '<i18n:setLocale>',
                    '<c:setLocale>',
                    '<locale:set>'
                ],
                'correct_answer': 1
            },
        ]

    # Module 10 Questions - JSTL Formatting Tags
    def get_module10_questions(self):
        return [
            {
                'question': 'Which tag is used to format dates?',
                'options': [
                    '<fmt:formatDate>',
                    '<fmt:date>',
                    '<fmt:dateFormat>',
                    '<fmt:format>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tag is used to format numbers?',
                'options': [
                    '<fmt:formatNumber>',
                    '<fmt:number>',
                    '<fmt:numberFormat>',
                    '<fmt:format>'
                ],
                'correct_answer': 1
            },
        ]

    # Module 11 Questions - Building Custom Tags
    def get_module11_questions(self):
        return [
            {
                'question': 'What interface must a custom tag handler implement?',
                'options': [
                    'Tag',
                    'TagHandler',
                    'CustomTag',
                    'JspTag'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Where is the TLD (Tag Library Descriptor) file typically placed?',
                'options': [
                    'WEB-INF',
                    'WEB-INF/tlds',
                    'WEB-INF/lib',
                    'Any of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 12 Questions - Web Template Integration
    def get_module12_questions(self):
        return [
            {
                'question': 'Which JSP directive is used to include files?',
                'options': [
                    '<%@ include %>',
                    '<jsp:include>',
                    'Both A and B',
                    'None of the above'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between include directive and include action?',
                'options': [
                    'Directive includes at translation time, action at runtime',
                    'Action includes at translation time, directive at runtime',
                    'No difference',
                    'Directive is for JSP, action is for HTML'
                ],
                'correct_answer': 1
            },
        ]

    # Module 13 Questions - Revisiting Servlets
    def get_module13_questions(self):
        return [
            {
                'question': 'Which method is called for each HTTP request?',
                'options': [
                    'init()',
                    'service()',
                    'doGet()',
                    'destroy()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of servlet initialization parameters?',
                'options': [
                    'Configure servlet at startup',
                    'Pass data between requests',
                    'Store session data',
                    'Handle errors'
                ],
                'correct_answer': 1
            },
        ]

    # Module 14 Questions - Database Connectivity
    def get_module14_questions(self):
        return [
            {
                'question': 'What does JNDI stand for?',
                'options': [
                    'Java Naming and Directory Interface',
                    'Java Network Directory Interface',
                    'Java Native Data Interface',
                    'Java Network Data Interface'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method is used to get a database connection from JNDI?',
                'options': [
                    'Context.lookup()',
                    'Context.find()',
                    'Context.get()',
                    'Context.retrieve()'
                ],
                'correct_answer': 1
            },
        ]

    # Module 15 Questions - Listing Data on Webpage
    def get_module15_questions(self):
        return [
            {
                'question': 'Which JSP directive is used to include another JSP file?',
                'options': [
                    '<%@ include file="..." %>',
                    '<jsp:include page="..." />',
                    'Both A and B',
                    'None of the above'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you iterate over a ResultSet in JSP?',
                'options': [
                    'Using JSTL forEach',
                    'Using scriptlets with while loop',
                    'Both A and B',
                    'Using only JSP expressions'
                ],
                'correct_answer': 3
            },
        ]

    # Module 16 Questions - Add Records to Database
    def get_module16_questions(self):
        return [
            {
                'question': 'Which SQL statement is used to insert records?',
                'options': [
                    'INSERT',
                    'ADD',
                    'CREATE',
                    'UPDATE'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is PreparedStatement used for?',
                'options': [
                    'Execute parameterized queries',
                    'Prevent SQL injection',
                    'Improve performance',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 17 Questions - Update Records
    def get_module17_questions(self):
        return [
            {
                'question': 'Which SQL statement is used to update records?',
                'options': [
                    'UPDATE',
                    'MODIFY',
                    'CHANGE',
                    'ALTER'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the WHERE clause used for in UPDATE statements?',
                'options': [
                    'Specify which records to update',
                    'Specify new values',
                    'Specify table name',
                    'Specify column names'
                ],
                'correct_answer': 1
            },
        ]

    # Module 18 Questions - Delete Records
    def get_module18_questions(self):
        return [
            {
                'question': 'Which SQL statement is used to delete records?',
                'options': [
                    'DELETE',
                    'REMOVE',
                    'DROP',
                    'CLEAR'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What happens if you omit the WHERE clause in a DELETE statement?',
                'options': [
                    'Deletes all records',
                    'Deletes first record',
                    'Deletes last record',
                    'Nothing happens'
                ],
                'correct_answer': 1
            },
        ]

    # Module 19 Questions - Add JSTL Support
    def get_module19_questions(self):
        return [
            {
                'question': 'Which JSTL tag is used to iterate over database results?',
                'options': [
                    '<c:forEach>',
                    '<c:for>',
                    '<c:loop>',
                    '<sql:query>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the benefit of using JSTL over scriptlets?',
                'options': [
                    'Better separation of concerns',
                    'Easier to maintain',
                    'More readable',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 20 Questions - Image/File Upload
    def get_module20_questions(self):
        return [
            {
                'question': 'Which attribute is required for file upload in HTML forms?',
                'options': [
                    'method="post"',
                    'enctype="multipart/form-data"',
                    'Both A and B',
                    'action attribute'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which library is commonly used for file upload in servlets?',
                'options': [
                    'Apache Commons FileUpload',
                    'Java File API',
                    'Servlet File API',
                    'JSP File API'
                ],
                'correct_answer': 1
            },
        ]

