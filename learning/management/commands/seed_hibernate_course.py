"""
Management command to seed Hibernate course with complete modules and topics
Run with: python manage.py seed_hibernate_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Hibernate course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Hibernate course
        course, created = Course.objects.get_or_create(
            title='HIBERNATE COURSE',
            defaults={
                'description': 'Complete Hibernate course covering framework setup, HQL, integration with JSP/Servlets, and building applications with Hibernate.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Hibernate course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Hibernate Introduction',
                'summary': 'Introduction to Hibernate framework. Learn about Hibernate overview, installing MySQL, and setting up SQL Workbench.',
                'learning_objectives': 'Understand Hibernate framework\nInstall MySQL database\nSet up SQL Workbench\nLearn Hibernate basics',
                'topics': "Let's start with Hibernate\nHibernate overview\nInstalling MySQL\nSQL Workbench",
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Hibernate Framework Setup',
                'summary': 'Learn to set up Hibernate framework. Configure Hibernate, understand SessionFactory and Session, create entity classes, and perform CRUD operations.',
                'learning_objectives': 'Set up Hibernate project\nConfigure Hibernate configuration file\nUnderstand SessionFactory and Session\nCreate entity classes\nPerform CRUD operations (Create, Read, Update, Delete)',
                'topics': 'Setting up project\nSetting up Hibernate configuration file\nSessionFactory and Session\nAdding Entity Class\nHibernate in action\nCRUD operations:\nRetrieve record from database\nUpdate record in database\nDelete record in database',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Hibernate Query Language (HQL)',
                'summary': 'Master Hibernate Query Language (HQL). Learn to list records, use WHERE clause, and perform update and delete operations using HQL.',
                'learning_objectives': 'List records using HQL\nUse HQL WHERE clause\nUpdate records using HQL\nDelete records using HQL',
                'topics': 'Listing records\nHQL WHERE clause\nUpdating records using HQL\nDeleting records using HQL',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Hibernate + JSP/Servlet Integration',
                'summary': 'Integrate Hibernate with JSP and Servlets. Add Hibernate support, understand configuration, create entity classes, and use Hibernate in web applications.',
                'learning_objectives': 'Integrate Hibernate with JSP & Servlets\nAdd Hibernate support to web applications\nUnderstand Hibernate configuration in web context\nCreate Hibernate entity classes\nUse Hibernate in web applications',
                'topics': 'Integrating Hibernate with JSP & Servlets\nAdd Hibernate support\nUnderstanding Hibernate configuration\nHibernate entity class\nHibernate in action',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Building the Application (Hibernate + JSP)',
                'summary': 'Build a complete application using Hibernate and JSP. Set up the project, display images, implement update and delete functionality, and create a view image page.',
                'learning_objectives': 'Set up Hibernate + JSP application\nList and display files\nDisplay image files on JSP page\nImprove page view\nAdd update information form\nImplement update functionality\nUpdate specific column data using Hibernate\nAdd view image action\nImplement view image page\nAdd delete image action',
                'topics': 'Setting things up\nList available files\nDisplay image files on JSP page\nImprove view of the page\nAdding update information form\nImplement update information functionality\nUpdate information logic revisited\nUpdate specific column data using Hibernate\nAdd view image action\nImplement view image page\nAdd delete image action\nRecheck the application working',
                'questions': self.get_module5_questions(),
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

    # Module 1 Questions - Hibernate Introduction
    def get_module1_questions(self):
        return [
            {
                'question': 'What is Hibernate?',
                'options': [
                    'A Java ORM (Object-Relational Mapping) framework',
                    'A database server',
                    'A web framework',
                    'A programming language'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does ORM stand for?',
                'options': [
                    'Object-Relational Mapping',
                    'Object-Relational Model',
                    'Object-Relational Method',
                    'Object-Relational Module'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which database is commonly used with Hibernate?',
                'options': [
                    'MySQL',
                    'PostgreSQL',
                    'Oracle',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is SQL Workbench used for?',
                'options': [
                    'Database administration and query execution',
                    'Code editing',
                    'Web development',
                    'Version control'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the main advantage of using Hibernate?',
                'options': [
                    'Reduces boilerplate JDBC code',
                    'Provides object-relational mapping',
                    'Handles database connections automatically',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the minimum Java version required for Hibernate 5?',
                'options': [
                    'Java 6',
                    'Java 7',
                    'Java 8',
                    'Java 11'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of Hibernate configuration?',
                'options': [
                    'To configure database connection',
                    'To configure entity mappings',
                    'To configure Hibernate properties',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a dialect in Hibernate?',
                'options': [
                    'Database-specific SQL syntax',
                    'A programming language',
                    'A query language',
                    'A configuration file'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which property is used to specify database dialect in Hibernate?',
                'options': [
                    'hibernate.dialect',
                    'hibernate.database',
                    'hibernate.dbtype',
                    'hibernate.sql'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of hibernate.show_sql property?',
                'options': [
                    'To display SQL queries in console',
                    'To hide SQL queries',
                    'To validate SQL queries',
                    'To format SQL queries'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - Hibernate Framework Setup
    def get_module2_questions(self):
        return [
            {
                'question': 'What is the main configuration file in Hibernate?',
                'options': [
                    'hibernate.cfg.xml',
                    'hibernate.properties',
                    'Both A and B',
                    'application.xml'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is SessionFactory in Hibernate?',
                'options': [
                    'A factory for creating Session objects',
                    'A database connection',
                    'A query executor',
                    'A transaction manager'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a Session in Hibernate?',
                'options': [
                    'A single-threaded object representing a conversation with the database',
                    'A database connection pool',
                    'A transaction',
                    'A query object'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to mark a class as a Hibernate entity?',
                'options': [
                    '@Entity',
                    '@Table',
                    '@HibernateEntity',
                    '@Persistent'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does CRUD stand for?',
                'options': [
                    'Create, Read, Update, Delete',
                    'Create, Retrieve, Update, Delete',
                    'Create, Read, Upload, Delete',
                    'Create, Retrieve, Upload, Delete'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the lifecycle of a SessionFactory?',
                'options': [
                    'Created once, used throughout application',
                    'Created per request',
                    'Created per session',
                    'Created per transaction'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method is used to save an entity in Hibernate?',
                'options': [
                    'session.save()',
                    'session.persist()',
                    'session.saveOrUpdate()',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between save() and persist()?',
                'options': [
                    'save() returns generated ID, persist() returns void',
                    'persist() returns generated ID, save() returns void',
                    'They are identical',
                    'save() is for updates, persist() is for inserts'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to specify the primary key?',
                'options': [
                    '@PrimaryKey',
                    '@Id',
                    '@Key',
                    '@GeneratedValue'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is @GeneratedValue used for?',
                'options': [
                    'To generate values for all fields',
                    'To auto-generate primary key values',
                    'To generate SQL queries',
                    'To generate entity classes'
                ],
                'correct_answer': 2
            },
        ]

    # Module 3 Questions - Hibernate Query Language (HQL)
    def get_module3_questions(self):
        return [
            {
                'question': 'What does HQL stand for?',
                'options': [
                    'Hibernate Question Language',
                    'Hibernate Query Language',
                    'Hibernate Query Library',
                    'Hibernate Question Library'
                ],
                'correct_answer': 2
            },
            {
                'question': 'In HQL, what do you query?',
                'options': [
                    'Database tables',
                    'Java objects/entities',
                    'SQL statements',
                    'Database schemas'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method is used to execute HQL queries?',
                'options': [
                    'createSQLQuery()',
                    'createQuery()',
                    'executeQuery()',
                    'runQuery()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you update records using HQL?',
                'options': [
                    'Using SQL UPDATE',
                    'Using UPDATE statement in HQL',
                    'Using session.update()',
                    'Using session.save()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the syntax for HQL SELECT query?',
                'options': [
                    'FROM EntityName',
                    'SELECT e FROM EntityName e',
                    'Both A and B',
                    'SELECT * FROM table'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you use WHERE clause in HQL?',
                'options': [
                    'FROM EntityName WHERE condition',
                    'SELECT e FROM EntityName e WHERE e.property = :value',
                    'Both A and B',
                    'WHERE condition FROM EntityName'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between HQL and SQL?',
                'options': [
                    'SQL works with objects, HQL works with tables',
                    'HQL works with objects, SQL works with tables',
                    'They are identical',
                    'HQL is for queries, SQL is for updates'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you use named parameters in HQL?',
                'options': [
                    'Using ? parameter',
                    'Using :parameterName',
                    'Using @parameterName',
                    'Using $parameterName'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What method is used to set parameters in HQL query?',
                'options': [
                    'setValue()',
                    'setParameter()',
                    'setProperty()',
                    'setAttribute()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you delete records using HQL?',
                'options': [
                    'Using session.delete()',
                    'DELETE FROM EntityName WHERE condition',
                    'Using SQL DELETE',
                    'All of the above'
                ],
                'correct_answer': 2
            },
        ]

    # Module 4 Questions - Hibernate + JSP/Servlet Integration
    def get_module4_questions(self):
        return [
            {
                'question': 'Where should Hibernate configuration file be placed in a web application?',
                'options': [
                    'WEB-INF/classes',
                    'WEB-INF',
                    'src/main/resources',
                    'Both A and C'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the best practice for SessionFactory in web applications?',
                'options': [
                    'Create a new SessionFactory for each request',
                    'Create SessionFactory once at application startup',
                    'Create SessionFactory per session',
                    'Create SessionFactory per user'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How should Session objects be managed in web applications?',
                'options': [
                    'One Session per application',
                    'One Session per user',
                    'One Session per request',
                    'One Session per transaction'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which pattern is commonly used to manage Hibernate Session in web applications?',
                'options': [
                    'Session-per-application pattern',
                    'Session-per-user pattern',
                    'Session-per-request pattern',
                    'Session-per-transaction pattern'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of ServletContextListener in Hibernate integration?',
                'options': [
                    'To initialize SessionFactory at application startup',
                    'To close SessionFactory at application shutdown',
                    'Both A and B',
                    'To manage sessions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you access SessionFactory in a servlet?',
                'options': [
                    'Create new SessionFactory',
                    'From HttpSession',
                    'From ServletContext attribute',
                    'From request parameter'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What should be done with Session after use in a servlet?',
                'options': [
                    'Keep it open',
                    'Store it in session',
                    'Close the session',
                    'Return it to pool'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of @WebListener annotation?',
                'options': [
                    'To mark a class as a servlet',
                    'To mark a class as a filter',
                    'To mark a class as a servlet listener',
                    'To mark a class as a controller'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the best practice for transaction management in web applications?',
                'options': [
                    'One transaction per application',
                    'One transaction per user',
                    'One transaction per request',
                    'No transactions needed'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you handle exceptions in Hibernate web applications?',
                'options': [
                    'Let exceptions propagate',
                    'Log and ignore',
                    'Catch HibernateException and handle appropriately',
                    'Convert to runtime exceptions'
                ],
                'correct_answer': 3
            },
        ]

    # Module 5 Questions - Building the Application
    def get_module5_questions(self):
        return [
            {
                'question': 'How do you update a specific column in Hibernate?',
                'options': [
                    'Using HQL UPDATE with SET clause',
                    'Load entity, modify property, save',
                    'Using SQL UPDATE',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the best way to display images stored in database in JSP?',
                'options': [
                    'Store image path and display using <img> tag',
                    'Store image as BLOB and create a servlet to serve it',
                    'Both A and B',
                    'Store images in file system only'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you delete a record in Hibernate?',
                'options': [
                    'session.delete(entity)',
                    'Using HQL DELETE',
                    'session.remove(entity)',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What should be done before deleting an entity in Hibernate?',
                'options': [
                    'Load the entity first',
                    'Check if entity exists',
                    'Close all sessions',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of @Lob annotation?',
                'options': [
                    'To mark a field as local',
                    'To mark a field as lazy',
                    'To mark a field as loadable',
                    'To mark a field as Large Object (BLOB/CLOB)'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you retrieve an entity by ID in Hibernate?',
                'options': [
                    'session.get(EntityClass.class, id)',
                    'session.load(EntityClass.class, id)',
                    'session.find(EntityClass.class, id)',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between get() and load()?',
                'options': [
                    'load() returns null if not found, get() throws exception',
                    'They are identical',
                    'get() is lazy, load() is eager',
                    'get() returns null if not found, load() throws exception'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of session.flush()?',
                'options': [
                    'To clear the session',
                    'To close the session',
                    'To validate the session',
                    'To synchronize session state with database'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of session.clear()?',
                'options': [
                    'To clear all entities from session',
                    'To clear cache',
                    'To clear transactions',
                    'To clear configuration'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you list all entities of a type in Hibernate?',
                'options': [
                    'Using HQL: FROM EntityName',
                    'Using Criteria API',
                    'Using session.createQuery()',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

