"""
Management command to seed Spring Boot course with complete modules and topics
Run with: python manage.py seed_springboot_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Spring Boot course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Spring Boot course
        course, created = Course.objects.get_or_create(
            title='SPRING BOOT COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete Spring Boot course covering setup, Spring Boot applications, RESTful microservices, database connectivity, microservices architecture, and service discovery with Eureka.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Spring Boot course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Background & Setup',
                'summary': 'Introduction to Spring Boot setup. Learn about requirements, Maven overview, and setting up a Maven project for Spring Boot.',
                'learning_objectives': 'Understand Spring Boot requirements\nLearn Maven overview\nSet up Maven project for Spring Boot\nConfigure development environment',
                'topics': 'Setting up requirements\nMaven overview\nSet up Maven project for Spring Boot',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Getting Started with Spring Boot',
                'summary': 'Create your first Spring Boot application. Learn to build web applications with JSP support, configure application.properties, use ServletInitializer, and create WAR files.',
                'learning_objectives': 'Create first Spring Boot application\nBuild web applications with Spring Boot\nAdd JSP support\nConfigure application.properties\nUse ServletInitializer\nCreate WAR file using Maven',
                'topics': 'First Spring Boot application\nWebapp with Spring Boot\nWebapp with Spring Boot (JSP support)\nApplication.properties\nServletInitializer\nCreating WAR file using Maven project',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Spring MVC + RESTful Background',
                'summary': 'Learn to set up RESTful web applications with Spring Boot. Define REST rules and bootstrap Spring Boot projects.',
                'learning_objectives': 'Set up RESTful webapp with Spring Boot\nDefine REST rules\nBootstrap Spring Boot project\nUnderstand Spring MVC with REST',
                'topics': 'Setting up Restful webapp\nDefining the rules\nBootstrapping Spring Boot project',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Building RESTful Microservices with Spring Boot',
                'summary': 'Build RESTful microservices with Spring Boot. Implement view all posts, view specific post, POST functionality, update and delete operations, and use Postman for testing.',
                'learning_objectives': 'Add "View all posts" functionality\nAdd "View specific post" functionality\nUse Postman for API testing\nAdd POST functionality\nPerform update operations\nPerform delete operations\nFix common issues',
                'topics': 'Add "View all posts" functionality\nAdd "View specific post" functionality\nUsing Postman\nAdd POST functionality\nFixing issues\nPerform update operation\nPerform delete operation',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Microservice + Database Connectivity',
                'summary': 'Connect microservices to databases. Set up MySQL, configure database connections, create tables, configure entity classes, update service layer, and perform CRUD operations.',
                'learning_objectives': 'Set up database connectivity\nInstall and configure MySQL\nSet up database connection\nCreate database tables\nConfigure Entity classes\nUpdate Service layer\nPerform CRUD operations',
                'topics': 'Setting up\nInstalling MySQL\nSetting up connection\nCreating database table\nConfiguring Entity class\nUpdating Service layer\nCRUD operations',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Microservices with Spring Boot',
                'summary': 'Master microservices architecture with Spring Boot. Understand microservices, set up Spring MVC projects, communicate between microservices, implement best practices, customize error pages, add JSTL support, and implement service discovery with Eureka and load balancing.',
                'learning_objectives': 'Understand microservices architecture\nSet up Spring MVC project for microservices\nCreate Spring Boot microservices\nEnable communication between microservices\nImprove apps with best practices\nCustomize white-label error page\nAdd JSTL support\nUnderstand microservice discovery service\nCreate Eureka server\nCreate Eureka client\nImplement load balancing',
                'topics': 'Understanding microservices again\nSetting up Spring MVC project\nSpring Boot microservice\nCommunicating with another microservice\nImprove apps with best practices\nCustomize white-label error page\nImprove the view – Add JSTL support\nMicroservice discovery service overview\nCreate Eureka server\nCreate Eureka client\nLoad balancing',
                'questions': self.get_module6_questions(),
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

    # Module 1 Questions - Background & Setup
    def get_module1_questions(self):
        return [
            {
                'question': 'What is Spring Boot?',
                'options': [
                    'A framework that simplifies Spring application development',
                    'A database',
                    'A web server',
                    'A programming language'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is Maven?',
                'options': [
                    'A build automation and project management tool',
                    'A database',
                    'A web framework',
                    'A testing framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the main configuration file for Maven?',
                'options': [
                    'pom.xml',
                    'maven.xml',
                    'build.xml',
                    'config.xml'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - Getting Started with Spring Boot
    def get_module2_questions(self):
        return [
            {
                'question': 'What is the main annotation for a Spring Boot application?',
                'options': [
                    '@SpringBootApplication',
                    '@SpringApplication',
                    '@BootApplication',
                    '@Application'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is application.properties used for?',
                'options': [
                    'To configure Spring Boot application settings',
                    'To define database schema',
                    'To write Java code',
                    'To define HTML templates'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is ServletInitializer used for?',
                'options': [
                    'To initialize servlet context for WAR deployment',
                    'To start the application',
                    'To configure database',
                    'To handle HTTP requests'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you create a WAR file using Maven?',
                'options': [
                    'mvn package',
                    'mvn war',
                    'mvn build',
                    'mvn compile'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions - Spring MVC + RESTful Background
    def get_module3_questions(self):
        return [
            {
                'question': 'What is a RESTful web service?',
                'options': [
                    'A web service that follows REST principles',
                    'A database service',
                    'A file service',
                    'A security service'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to create REST controllers in Spring Boot?',
                'options': [
                    '@RestController',
                    '@Controller',
                    '@REST',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does bootstrapping mean in Spring Boot?',
                'options': [
                    'Auto-configuration and starting the application',
                    'Installing the framework',
                    'Configuring the database',
                    'Creating templates'
                ],
                'correct_answer': 1
            },
        ]

    # Module 4 Questions - Building RESTful Microservices
    def get_module4_questions(self):
        return [
            {
                'question': 'What is Postman used for?',
                'options': [
                    'Testing REST APIs',
                    'Database management',
                    'Code editing',
                    'Version control'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which HTTP method is used for updating resources?',
                'options': [
                    'PUT',
                    'POST',
                    'GET',
                    'DELETE'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which HTTP method is used for deleting resources?',
                'options': [
                    'DELETE',
                    'PUT',
                    'POST',
                    'GET'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a microservice?',
                'options': [
                    'A small, independent service that performs a specific function',
                    'A large monolithic application',
                    'A database service',
                    'A web server'
                ],
                'correct_answer': 1
            },
        ]

    # Module 5 Questions - Microservice + Database Connectivity
    def get_module5_questions(self):
        return [
            {
                'question': 'Which annotation is used to mark a class as a JPA entity?',
                'options': [
                    '@Entity',
                    '@Table',
                    '@JPAEntity',
                    '@Persistent'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the default database connection pool in Spring Boot?',
                'options': [
                    'HikariCP',
                    'Tomcat Pool',
                    'C3P0',
                    'DBCP'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used for Spring Data JPA repositories?',
                'options': [
                    '@Repository',
                    '@JpaRepository',
                    '@Component',
                    'All of the above'
                ],
                'correct_answer': 4
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
        ]

    # Module 6 Questions - Microservices with Spring Boot
    def get_module6_questions(self):
        return [
            {
                'question': 'What is Eureka?',
                'options': [
                    'A service discovery server',
                    'A database',
                    'A web server',
                    'A testing framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is service discovery?',
                'options': [
                    'A mechanism for services to find and communicate with each other',
                    'A database discovery mechanism',
                    'A file discovery system',
                    'A network discovery protocol'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is load balancing?',
                'options': [
                    'Distributing incoming requests across multiple service instances',
                    'Balancing database load',
                    'Balancing memory usage',
                    'Balancing CPU usage'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to enable Eureka client?',
                'options': [
                    '@EnableEurekaClient',
                    '@EurekaClient',
                    '@EnableDiscoveryClient',
                    'Both A and C'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which annotation is used to enable Eureka server?',
                'options': [
                    '@EnableEurekaServer',
                    '@EurekaServer',
                    '@EnableDiscoveryServer',
                    '@Server'
                ],
                'correct_answer': 1
            },
        ]

