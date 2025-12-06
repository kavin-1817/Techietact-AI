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
            {
                'question': 'What is a servlet?',
                'options': [
                    'A Java class that extends HttpServlet',
                    'A database class',
                    'A configuration file',
                    'A web server'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSP element is used for declarations?',
                'options': [
                    '<%! %>',
                    '<%= %>',
                    '<% %>',
                    '<%@ %>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSP element is used for scriptlets?',
                'options': [
                    '<%! %>',
                    '<%= %>',
                    '<% %>',
                    '<%@ %>'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which JSP element is used for directives?',
                'options': [
                    '<%! %>',
                    '<%= %>',
                    '<% %>',
                    '<%@ %>'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of web.xml?',
                'options': [
                    'To configure servlets and web application settings',
                    'To write Java code',
                    'To define HTML pages',
                    'To configure database'
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
            {
                'question': 'What is the difference between GET and POST methods?',
                'options': [
                    'GET sends data in URL, POST sends in request body',
                    'POST sends data in URL, GET sends in request body',
                    'They are identical',
                    'GET is for forms, POST is for links'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you handle multiple values for the same parameter?',
                'options': [
                    'request.getParameterValues()',
                    'request.getParameter()',
                    'request.getAttributes()',
                    'request.getValues()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of form validation?',
                'options': [
                    'To ensure data integrity and security',
                    'To format data',
                    'To store data',
                    'To display data'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method handles GET requests in a servlet?',
                'options': [
                    'doGet()',
                    'doPost()',
                    'doPut()',
                    'doDelete()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method handles POST requests in a servlet?',
                'options': [
                    'doGet()',
                    'doPost()',
                    'doPut()',
                    'doDelete()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of request.getAttribute()?',
                'options': [
                    'To get attributes set in the request scope',
                    'To get form parameters',
                    'To get session attributes',
                    'To get context attributes'
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
            {
                'question': 'Which JSP action tag is used to set a bean property?',
                'options': [
                    '<jsp:setProperty>',
                    '<jsp:property>',
                    '<jsp:set>',
                    '<jsp:put>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSP action tag is used to get a bean property?',
                'options': [
                    '<jsp:getProperty>',
                    '<jsp:property>',
                    '<jsp:get>',
                    '<jsp:fetch>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which scope makes a bean available only for the current request?',
                'options': [
                    'page',
                    'request',
                    'session',
                    'application'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which scope makes a bean available for the user session?',
                'options': [
                    'page',
                    'request',
                    'session',
                    'application'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is Expression Language (EL) used for in JSP?',
                'options': [
                    'To access bean properties and data',
                    'To write Java code',
                    'To configure servlets',
                    'To define HTML'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the EL syntax to access a bean property?',
                'options': [
                    '${bean.property}',
                    '#{bean.property}',
                    '@{bean.property}',
                    '${bean->property}'
                ],
                'correct_answer': 1
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
            {
                'question': 'What is a cookie?',
                'options': [
                    'A small piece of data stored on the client',
                    'A server-side storage',
                    'A database record',
                    'A session attribute'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you create a cookie in a servlet?',
                'options': [
                    'new Cookie(name, value)',
                    'Cookie.create(name, value)',
                    'request.createCookie(name, value)',
                    'response.createCookie(name, value)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you add a cookie to the response?',
                'options': [
                    'response.addCookie(cookie)',
                    'request.addCookie(cookie)',
                    'session.addCookie(cookie)',
                    'context.addCookie(cookie)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is URL rewriting?',
                'options': [
                    'A technique to maintain session without cookies',
                    'A way to rewrite URLs',
                    'A method to redirect URLs',
                    'A way to encode URLs'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of session.setAttribute()?',
                'options': [
                    'To store data in the session',
                    'To retrieve data from session',
                    'To remove data from session',
                    'To clear the session'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of session.getAttribute()?',
                'options': [
                    'To retrieve data from the session',
                    'To store data in session',
                    'To remove data from session',
                    'To clear the session'
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
            {
                'question': 'Which JSTL tag is used to set a variable?',
                'options': [
                    '<c:set>',
                    '<c:var>',
                    '<c:assign>',
                    '<c:put>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSTL tag is used to remove a variable?',
                'options': [
                    '<c:remove>',
                    '<c:delete>',
                    '<c:clear>',
                    '<c:unset>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSTL tag is used for URL encoding?',
                'options': [
                    '<c:url>',
                    '<c:encode>',
                    '<c:link>',
                    '<c:path>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSTL tag is used for redirecting?',
                'options': [
                    '<c:redirect>',
                    '<c:forward>',
                    '<c:send>',
                    '<c:go>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSTL tag is used to catch exceptions?',
                'options': [
                    '<c:catch>',
                    '<c:error>',
                    '<c:exception>',
                    '<c:try>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which JSTL tag is used to import content?',
                'options': [
                    '<c:import>',
                    '<c:include>',
                    '<c:load>',
                    '<c:fetch>'
                ],
                'correct_answer': 1
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
            {
                'question': 'What is the JSP compilation process called?',
                'options': [
                    'Translation',
                    'Compilation',
                    'Execution',
                    'Interpretation'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a JSP servlet?',
                'options': [
                    'The compiled version of a JSP page',
                    'A regular servlet',
                    'A Java bean',
                    'A configuration file'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of page directive?',
                'options': [
                    'To configure page-level settings',
                    'To include files',
                    'To define beans',
                    'To set session attributes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the isELIgnored attribute used for?',
                'options': [
                    'To disable Expression Language on a page',
                    'To enable Expression Language',
                    'To ignore errors',
                    'To ignore warnings'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the errorPage attribute used for?',
                'options': [
                    'To specify a custom error page',
                    'To handle errors',
                    'To log errors',
                    'To display errors'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the contentType attribute used for?',
                'options': [
                    'To set the MIME type of the response',
                    'To set the character encoding',
                    'To set the page type',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the pageEncoding attribute used for?',
                'options': [
                    'To specify character encoding of the JSP page',
                    'To encode URLs',
                    'To encode forms',
                    'To encode cookies'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of JSP implicit objects?',
                'options': [
                    'To provide access to servlet objects without declaration',
                    'To hide objects',
                    'To create new objects',
                    'To delete objects'
                ],
                'correct_answer': 1
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
            {
                'question': 'Which function converts a string to uppercase?',
                'options': [
                    'fn:toUpperCase()',
                    'fn:upper()',
                    'fn:uppercase()',
                    'fn:toUpper()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function converts a string to lowercase?',
                'options': [
                    'fn:toLowerCase()',
                    'fn:lower()',
                    'fn:lowercase()',
                    'fn:toLower()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function checks if a string contains a substring?',
                'options': [
                    'fn:contains()',
                    'fn:has()',
                    'fn:includes()',
                    'fn:find()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function checks if a string starts with a prefix?',
                'options': [
                    'fn:startsWith()',
                    'fn:starts()',
                    'fn:begin()',
                    'fn:prefix()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function checks if a string ends with a suffix?',
                'options': [
                    'fn:endsWith()',
                    'fn:ends()',
                    'fn:finish()',
                    'fn:suffix()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function replaces characters in a string?',
                'options': [
                    'fn:replace()',
                    'fn:substitute()',
                    'fn:change()',
                    'fn:swap()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which function escapes XML characters?',
                'options': [
                    'fn:escapeXml()',
                    'fn:escape()',
                    'fn:xml()',
                    'fn:encode()'
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
                    'Integration',
                    'Internationalization',
                    'Internet',
                    'Interface'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a Locale object used for?',
                'options': [
                    'Database location',
                    'Language and country settings',
                    'Server location',
                    'File location'
                ],
                'correct_answer': 2
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
            {
                'question': 'What is ResourceBundle used for?',
                'options': [
                    'To load database resources',
                    'To load locale-specific messages',
                    'To load configuration files',
                    'To load HTML files'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the naming convention for locale-specific property files?',
                'options': [
                    'filename-locale.properties',
                    'filename_locale.properties',
                    'filename.properties_locale',
                    'All of the above'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which JSTL tag is used to format messages?',
                'options': [
                    '<fmt:text>',
                    '<fmt:message>',
                    '<fmt:msg>',
                    '<fmt:output>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:setBundle>?',
                'options': [
                    'To set the locale',
                    'To set the resource bundle for the page',
                    'To set the encoding',
                    'To set the format'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:setLocale>?',
                'options': [
                    'To set the bundle',
                    'To set the locale for formatting',
                    'To set the encoding',
                    'To set the format'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is L10N?',
                'options': [
                    'Location',
                    'Localization',
                    'Loading',
                    'Locking'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between I18N and L10N?',
                'options': [
                    'L10N is design, I18N is implementation',
                    'I18N is design, L10N is implementation',
                    'They are identical',
                    'I18N is for servers, L10N is for clients'
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
                    '<i18n:setLocale>',
                    '<fmt:setLocale>',
                    '<c:setLocale>',
                    '<locale:set>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:bundle>?',
                'options': [
                    'To set locale',
                    'To specify a resource bundle',
                    'To format dates',
                    'To format numbers'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:param>?',
                'options': [
                    'To set parameters',
                    'To pass parameters to message placeholders',
                    'To get parameters',
                    'To remove parameters'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a message key in I18N?',
                'options': [
                    'A database key',
                    'A unique identifier for a message in properties file',
                    'A session key',
                    'A cookie key'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the format for locale-specific property files?',
                'options': [
                    'messages-en-US.properties',
                    'messages_en_US.properties',
                    'messages.properties.en_US',
                    'All of the above'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default locale if none is specified?',
                'options': [
                    'English (US)',
                    'System default locale',
                    'No default',
                    'Server locale'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you get the current locale in JSP?',
                'options': [
                    'request.locale',
                    'pageContext.request.locale',
                    'session.locale',
                    'application.locale'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:requestEncoding>?',
                'options': [
                    'To get request encoding',
                    'To set request character encoding',
                    'To validate encoding',
                    'To convert encoding'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the fallback mechanism for missing translations?',
                'options': [
                    'Shows error',
                    'Uses default locale or key name',
                    'Shows blank',
                    'Uses English always'
                ],
                'correct_answer': 2
            },
        ]

    # Module 10 Questions - JSTL Formatting Tags
    def get_module10_questions(self):
        return [
            {
                'question': 'Which tag is used to format dates?',
                'options': [
                    '<fmt:date>',
                    '<fmt:formatDate>',
                    '<fmt:dateFormat>',
                    '<fmt:format>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which tag is used to format numbers?',
                'options': [
                    '<fmt:number>',
                    '<fmt:formatNumber>',
                    '<fmt:numberFormat>',
                    '<fmt:format>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which tag is used to parse dates?',
                'options': [
                    '<fmt:date>',
                    '<fmt:parseDate>',
                    '<fmt:readDate>',
                    '<fmt:getDate>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which tag is used to parse numbers?',
                'options': [
                    '<fmt:number>',
                    '<fmt:parseNumber>',
                    '<fmt:readNumber>',
                    '<fmt:getNumber>'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of type attribute in <fmt:formatDate>?',
                'options': [
                    'To specify data type',
                    'To specify date format type (date, time, both)',
                    'To specify locale type',
                    'To specify format type'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of pattern attribute in <fmt:formatDate>?',
                'options': [
                    'To specify date pattern',
                    'To specify custom date format pattern',
                    'To specify time pattern',
                    'To specify locale pattern'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of type attribute in <fmt:formatNumber>?',
                'options': [
                    'To specify data type',
                    'To specify number type (number, currency, percent)',
                    'To specify locale type',
                    'To specify format type'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of currencyCode attribute?',
                'options': [
                    'To specify currency type',
                    'To specify currency code for currency formatting',
                    'To specify currency symbol',
                    'To specify currency name'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:timeZone>?',
                'options': [
                    'To get time zone',
                    'To set time zone for date formatting',
                    'To validate time zone',
                    'To convert time zone'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <fmt:setTimeZone>?',
                'options': [
                    'To get time zone',
                    'To set time zone in a variable',
                    'To validate time zone',
                    'To convert time zone'
                ],
                'correct_answer': 2
            },
        ]

    # Module 11 Questions - Building Custom Tags
    def get_module11_questions(self):
        return [
            {
                'question': 'What interface must a custom tag handler implement?',
                'options': [
                    'TagHandler',
                    'Tag',
                    'CustomTag',
                    'JspTag'
                ],
                'correct_answer': 2
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
            {
                'question': 'What is a TLD file?',
                'options': [
                    'Tag Library Definition',
                    'Tag Library Descriptor that defines custom tags',
                    'Tag Library Document',
                    'All of the above'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What method is called when a custom tag starts?',
                'options': [
                    'start()',
                    'doStartTag()',
                    'begin()',
                    'init()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What method is called when a custom tag ends?',
                'options': [
                    'end()',
                    'doEndTag()',
                    'finish()',
                    'destroy()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a tag attribute?',
                'options': [
                    'A tag property',
                    'A parameter passed to a custom tag',
                    'A tag variable',
                    'A tag method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you declare tag attributes in TLD?',
                'options': [
                    'Using <param> element',
                    'Using <attribute> element',
                    'Using <property> element',
                    'Using <variable> element'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a tag body?',
                'options': [
                    'Tag attributes',
                    'Content between opening and closing tag',
                    'Tag name',
                    'Tag handler class'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is BodyTag interface used for?',
                'options': [
                    'To process tag attributes',
                    'To process tag body content',
                    'To process tag name',
                    'To process tag handler'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <taglib> directive?',
                'options': [
                    'To define a tag library',
                    'To import a tag library in JSP',
                    'To configure a tag library',
                    'To remove a tag library'
                ],
                'correct_answer': 2
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
                    'Action includes at translation time, directive at runtime',
                    'Directive includes at translation time, action at runtime',
                    'No difference',
                    'Directive is for JSP, action is for HTML'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <jsp:forward>?',
                'options': [
                    'To redirect to another page',
                    'To forward request to another resource',
                    'To include another page',
                    'To link to another page'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between forward and redirect?',
                'options': [
                    'Redirect is server-side, forward is client-side',
                    'Forward is server-side, redirect is client-side',
                    'They are identical',
                    'Forward is for JSP, redirect is for HTML'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of <jsp:param>?',
                'options': [
                    'To get parameters',
                    'To pass parameters when including or forwarding',
                    'To set parameters',
                    'To remove parameters'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a template in web development?',
                'options': [
                    'A database template',
                    'A code template',
                    'A reusable page layout or structure',
                    'A configuration template'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of header and footer includes?',
                'options': [
                    'To reuse common page elements',
                    'To separate content',
                    'To organize code',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the scope of variables in included pages?',
                'options': [
                    'Separate scope',
                    'Global scope',
                    'Same as the including page',
                    'No scope'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <jsp:plugin>?',
                'options': [
                    'To add plugins',
                    'To configure plugins',
                    'To embed applets or JavaBeans in JSP',
                    'To remove plugins'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <jsp:useBean>?',
                'options': [
                    'To create a bean',
                    'To delete a bean',
                    'To instantiate or locate a JavaBean',
                    'To configure a bean'
                ],
                'correct_answer': 3
            },
        ]

    # Module 13 Questions - Revisiting Servlets
    def get_module13_questions(self):
        return [
            {
                'question': 'Which method is called for each HTTP request?',
                'options': [
                    'init()',
                    'doGet()',
                    'service()',
                    'destroy()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of servlet initialization parameters?',
                'options': [
                    'Pass data between requests',
                    'Store session data',
                    'Configure servlet at startup',
                    'Handle errors'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you get initialization parameters in a servlet?',
                'options': [
                    'getParameter()',
                    'getAttribute()',
                    'getInitParameter()',
                    'getConfig()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ServletConfig used for?',
                'options': [
                    'To access application configuration',
                    'To access session data',
                    'To access servlet-specific configuration',
                    'To access request data'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ServletContext used for?',
                'options': [
                    'To access servlet-specific configuration',
                    'To access session data',
                    'To access application-wide configuration and resources',
                    'To access request data'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between ServletConfig and ServletContext?',
                'options': [
                    'Context is per-servlet, Config is per-application',
                    'They are identical',
                    'Config is per-servlet, Context is per-application',
                    'Config is for requests, Context is for responses'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of servlet annotations?',
                'options': [
                    'To configure web.xml',
                    'To configure database',
                    'To configure servlets without web.xml',
                    'To configure session'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which annotation is used to define a servlet?',
                'options': [
                    '@Servlet',
                    '@WebService',
                    '@WebServlet',
                    '@Service'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of loadOnStartup parameter?',
                'options': [
                    'To load servlet on first request',
                    'To load servlet on demand',
                    'To load servlet at server startup',
                    'To unload servlet'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the servlet lifecycle?',
                'options': [
                    'service() -> init() -> destroy()',
                    'destroy() -> init() -> service()',
                    'init() -> service() -> destroy()',
                    'init() -> destroy() -> service()'
                ],
                'correct_answer': 3
            },
        ]

    # Module 14 Questions - Database Connectivity
    def get_module14_questions(self):
        return [
            {
                'question': 'What does JNDI stand for?',
                'options': [
                    'Java Network Directory Interface',
                    'Java Native Data Interface',
                    'Java Naming and Directory Interface',
                    'Java Network Data Interface'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a DataSource?',
                'options': [
                    'A database table',
                    'A database query',
                    'A factory for database connections',
                    'A database result'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is JDBC?',
                'options': [
                    'Java Data Base Connection',
                    'Java Database Connection',
                    'Java Database Connectivity API',
                    'Java Data Binding Connection'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of Connection pooling?',
                'options': [
                    'To create new connections',
                    'To close connections',
                    'To reuse database connections efficiently',
                    'To validate connections'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is PreparedStatement?',
                'options': [
                    'A regular statement',
                    'A database connection',
                    'A precompiled SQL statement',
                    'A result set'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the advantage of PreparedStatement over Statement?',
                'options': [
                    'Easier to use',
                    'More features',
                    'Better performance and SQL injection prevention',
                    'Smaller size'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ResultSet?',
                'options': [
                    'A database table',
                    'A database connection',
                    'An object that contains query results',
                    'A SQL statement'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of JSTL SQL tags?',
                'options': [
                    'To configure database',
                    'To manage connections',
                    'To execute SQL queries in JSP',
                    'To validate queries'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which JSTL tag is used to execute SQL queries?',
                'options': [
                    '<sql:execute>',
                    '<sql:run>',
                    '<sql:query>',
                    '<sql:select>'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which JSTL tag is used to set up database connection?',
                'options': [
                    '<sql:dataSource>',
                    '<sql:connection>',
                    '<sql:setDataSource>',
                    '<sql:connect>'
                ],
                'correct_answer': 3
            },
        ]
            {
                'question': 'Which method is used to get a database connection from JNDI?',
                'options': [
                    'Context.find()',
                    'Context.get()',
                    'Context.lookup()',
                    'Context.retrieve()'
                ],
                'correct_answer': 3
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
            {
                'question': 'What is the purpose of <sql:update> tag?',
                'options': [
                    'To execute SELECT statements',
                    'To create tables',
                    'To execute INSERT, UPDATE, or DELETE statements',
                    'To drop tables'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <sql:param> tag?',
                'options': [
                    'To get parameters',
                    'To remove parameters',
                    'To set parameters for SQL queries',
                    'To validate parameters'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <sql:transaction> tag?',
                'options': [
                    'To execute a single query',
                    'To rollback transactions',
                    'To group multiple SQL operations in a transaction',
                    'To commit transactions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <sql:setDataSource> tag?',
                'options': [
                    'To execute queries',
                    'To close connections',
                    'To configure database connection',
                    'To validate connections'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the var attribute used for in <sql:query>?',
                'options': [
                    'To specify query type',
                    'To specify table name',
                    'To store query results in a variable',
                    'To specify column name'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the scope attribute used for in <sql:setDataSource>?',
                'options': [
                    'To specify query scope',
                    'To specify result scope',
                    'To specify the scope of the data source',
                    'To specify connection scope'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <sql:dateParam> tag?',
                'options': [
                    'To get date parameters',
                    'To format dates',
                    'To set date parameters in SQL queries',
                    'To parse dates'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of <sql:timeParam> tag?',
                'options': [
                    'To get time parameters',
                    'To format time',
                    'To set time parameters in SQL queries',
                    'To parse time'
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
                    'ADD',
                    'CREATE',
                    'INSERT',
                    'UPDATE'
                ],
                'correct_answer': 3
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
            {
                'question': 'What is the syntax for INSERT statement?',
                'options': [
                    'INSERT table VALUES (...)',
                    'INSERT VALUES (...)',
                    'INSERT INTO table VALUES (...)',
                    'INSERT INTO (...) VALUES table'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of executeUpdate() method?',
                'options': [
                    'To execute SELECT statements',
                    'To execute any SQL statement',
                    'To execute INSERT, UPDATE, or DELETE statements',
                    'To execute stored procedures'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does executeUpdate() return?',
                'options': [
                    'ResultSet',
                    'Boolean value',
                    'Number of affected rows',
                    'Connection object'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you set parameters in PreparedStatement?',
                'options': [
                    'Using set() method',
                    'Using add() method',
                    'Using setXXX() methods',
                    'Using put() method'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of setString() in PreparedStatement?',
                'options': [
                    'To get a String value',
                    'To validate a String',
                    'To set a String parameter',
                    'To format a String'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of setInt() in PreparedStatement?',
                'options': [
                    'To get an integer value',
                    'To validate an integer',
                    'To set an integer parameter',
                    'To format an integer'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is SQL injection?',
                'options': [
                    'A way to insert data',
                    'A database feature',
                    'A security vulnerability where malicious SQL is injected',
                    'A query optimization technique'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How does PreparedStatement prevent SQL injection?',
                'options': [
                    'By validating input',
                    'By escaping characters',
                    'By using parameterized queries',
                    'By encrypting queries'
                ],
                'correct_answer': 3
            },
        ]

    # Module 17 Questions - Update Records
    def get_module17_questions(self):
        return [
            {
                'question': 'Which SQL statement is used to update records?',
                'options': [
                    'MODIFY',
                    'CHANGE',
                    'ALTER',
                    'UPDATE'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the WHERE clause used for in UPDATE statements?',
                'options': [
                    'Specify new values',
                    'Specify table name',
                    'Specify column names',
                    'Specify which records to update'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the syntax for UPDATE statement?',
                'options': [
                    'UPDATE SET column = value WHERE condition',
                    'UPDATE table WHERE condition SET column = value',
                    'UPDATE column = value WHERE condition',
                    'UPDATE table SET column = value WHERE condition'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What happens if you omit the WHERE clause in UPDATE?',
                'options': [
                    'Updates first record',
                    'Updates last record',
                    'Nothing happens',
                    'Updates all records'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you update multiple columns in one UPDATE statement?',
                'options': [
                    'Use multiple UPDATE statements',
                    'Use separate SET clauses',
                    'Cannot update multiple columns',
                    'Separate column assignments with commas'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setTimestamp() in PreparedStatement?',
                'options': [
                    'To get a timestamp value',
                    'To validate a timestamp',
                    'To format a timestamp',
                    'To set a timestamp parameter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setDate() in PreparedStatement?',
                'options': [
                    'To get a date value',
                    'To validate a date',
                    'To format a date',
                    'To set a date parameter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a transaction?',
                'options': [
                    'A single SQL statement',
                    'A database connection',
                    'A query result',
                    'A group of SQL operations executed as a single unit'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of commit() in transactions?',
                'options': [
                    'To rollback changes',
                    'To start a transaction',
                    'To end a transaction',
                    'To save changes permanently'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of rollback() in transactions?',
                'options': [
                    'To save changes',
                    'To start a transaction',
                    'To end a transaction',
                    'To undo changes in a transaction'
                ],
                'correct_answer': 4
            },
        ]

    # Module 18 Questions - Delete Records
    def get_module18_questions(self):
        return [
            {
                'question': 'Which SQL statement is used to delete records?',
                'options': [
                    'REMOVE',
                    'DROP',
                    'CLEAR',
                    'DELETE'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What happens if you omit the WHERE clause in a DELETE statement?',
                'options': [
                    'Deletes first record',
                    'Deletes last record',
                    'Nothing happens',
                    'Deletes all records'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the syntax for DELETE statement?',
                'options': [
                    'DELETE table WHERE condition',
                    'DELETE WHERE condition',
                    'DELETE FROM WHERE condition',
                    'DELETE FROM table WHERE condition'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between DELETE and TRUNCATE?',
                'options': [
                    'TRUNCATE can use WHERE, DELETE deletes all',
                    'They are identical',
                    'DELETE is for tables, TRUNCATE is for databases',
                    'DELETE can use WHERE, TRUNCATE deletes all'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a cascade delete?',
                'options': [
                    'Manual deletion of records',
                    'Deletion of all records',
                    'Deletion of first record',
                    'Automatic deletion of related records'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setBoolean() in PreparedStatement?',
                'options': [
                    'To get a boolean value',
                    'To validate a boolean',
                    'To format a boolean',
                    'To set a boolean parameter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setDouble() in PreparedStatement?',
                'options': [
                    'To get a double value',
                    'To validate a double',
                    'To format a double',
                    'To set a double parameter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setFloat() in PreparedStatement?',
                'options': [
                    'To get a float value',
                    'To validate a float',
                    'To format a float',
                    'To set a float parameter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setLong() in PreparedStatement?',
                'options': [
                    'To get a long value',
                    'To validate a long',
                    'To format a long',
                    'To set a long parameter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of setNull() in PreparedStatement?',
                'options': [
                    'To get a NULL value',
                    'To validate NULL',
                    'To format NULL',
                    'To set a NULL parameter'
                ],
                'correct_answer': 4
            },
        ]

    # Module 19 Questions - Add JSTL Support
    def get_module19_questions(self):
        return [
            {
                'question': 'Which JSTL tag is used to iterate over database results?',
                'options': [
                    '<c:for>',
                    '<c:loop>',
                    '<sql:query>',
                    '<c:forEach>'
                ],
                'correct_answer': 4
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
            {
                'question': 'What is the purpose of <sql:query> tag?',
                'options': [
                    'To execute INSERT queries',
                    'To execute UPDATE queries',
                    'To execute DELETE queries',
                    'To execute SELECT queries'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of var attribute in <sql:query>?',
                'options': [
                    'To specify query type',
                    'To specify table name',
                    'To specify column name',
                    'To store query results'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you access query results in JSTL?',
                'options': [
                    'Using ${var}',
                    'Using ${query.rows}',
                    'Using ${result.rows}',
                    'Using ${var.rows}'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of <sql:update> tag?',
                'options': [
                    'To execute SELECT',
                    'To create tables',
                    'To drop tables',
                    'To execute INSERT, UPDATE, or DELETE'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of var attribute in <sql:update>?',
                'options': [
                    'To store query results',
                    'To specify query type',
                    'To specify table name',
                    'To store number of affected rows'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of <sql:transaction> tag?',
                'options': [
                    'To execute a single query',
                    'To rollback transactions',
                    'To commit transactions',
                    'To group SQL operations in a transaction'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of <sql:setDataSource> tag?',
                'options': [
                    'To execute queries',
                    'To close connections',
                    'To validate connections',
                    'To configure database connection'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the scope attribute used for in <sql:setDataSource>?',
                'options': [
                    'To specify query scope',
                    'To specify result scope',
                    'To specify connection scope',
                    'To specify data source scope'
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
                    'action attribute',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which library is commonly used for file upload in servlets?',
                'options': [
                    'Java File API',
                    'Servlet File API',
                    'JSP File API',
                    'Apache Commons FileUpload'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of enctype="multipart/form-data"?',
                'options': [
                    'To enable text input',
                    'To enable password input',
                    'To enable checkbox input',
                    'To enable file upload in forms'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of <input type="file">?',
                'options': [
                    'To create a text field',
                    'To create a password field',
                    'To create a checkbox field',
                    'To create a file upload field'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of DiskFileItemFactory?',
                'options': [
                    'To execute file upload',
                    'To validate file upload',
                    'To cancel file upload',
                    'To configure file upload settings'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of ServletFileUpload?',
                'options': [
                    'To configure file upload',
                    'To validate file upload',
                    'To cancel file upload',
                    'To handle file upload requests'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of FileItem?',
                'options': [
                    'To execute file upload',
                    'To validate file upload',
                    'To cancel file upload',
                    'To represent an uploaded file or form field'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of isFormField() method?',
                'options': [
                    'To check if file is valid',
                    'To check if file exists',
                    'To check if file is empty',
                    'To check if FileItem is a form field or file'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of write() method in FileItem?',
                'options': [
                    'To read file from disk',
                    'To delete file from disk',
                    'To validate file',
                    'To save uploaded file to disk'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of getSize() method in FileItem?',
                'options': [
                    'To get file size in bytes',
                    'To get file name',
                    'To get file type',
                    'To get file content'
                ],
                'correct_answer': 1
            },
        ]

