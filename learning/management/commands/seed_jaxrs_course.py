"""
Management command to seed RESTful API (JAX-RS) course with complete modules and topics
Run with: python manage.py seed_jaxrs_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with RESTful API (JAX-RS) course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get JAX-RS course
        course, created = Course.objects.get_or_create(
            title='RESTful API (JAX-RS) COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete RESTful API course using JAX-RS covering web services, REST principles, JAX-RS setup, Hibernate integration, advanced JAX-RS concepts, and building REST clients.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated RESTful API (JAX-RS) course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Web Services & REST Introduction',
                'summary': 'Introduction to web services and REST architecture. Learn about REST principles, resource-based URIs, HTTP methods, status codes, HATEOAS, Richardson Maturity Model, and JAX-RS overview.',
                'learning_objectives': 'Understand web services concepts\nLearn REST architecture principles\nUnderstand resource-based URIs\nLearn HTTP methods and status codes\nUnderstand idempotence of HTTP methods\nLearn HATEOAS concept\nUnderstand Richardson Maturity Model\nLearn about JAX-RS and its implementations',
                'topics': "Let's start with Restful Web Services\nIntroduction to Web Services\nREST Web Services overview\nResource-based URIs\nMore about resource-based URIs\nREST response\nStatus codes\nIdempotence of HTTP methods\nHATEOAS (Hypermedia as the Engine of Application State)\nThe Richardson Maturity Model\nJAX-RS and implementations overview",
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Setting Up JAX-RS',
                'summary': 'Learn to set up JAX-RS environment and create your first REST API. Handle GET and POST requests, use resource-based URIs for CRUD operations, and work with PathParams.',
                'learning_objectives': 'Set up JAX-RS environment\nCreate first REST API implementation\nHandle GET and POST requests\nUse resource-based URIs for CRUD methods\nWork with PathParams\nUnderstand REST API basics',
                'topics': 'Setting up environment\nBackground story\nGetting started with Restful API (fixing warnings)\nFirst REST API implementation\nRevisiting basics & handling POST requests\nResource-based URI for CRUD methods\nUsing PathParams',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Database Connectivity using Hibernate',
                'summary': 'Integrate Hibernate with JAX-RS for database operations. Set up MySQL, create sample database, implement service and DAO layers, and return XML and JSON responses.',
                'learning_objectives': 'Install and configure MySQL\nCreate sample database\nSet up Service layer\nIntegrate Hibernate with JAX-RS\nAdd and implement DAO layer\nReturn XML and JSON responses',
                'topics': 'Installing MySQL\nCreating sample database\nSetting up Service layer\nService layer (continued)\nIntegrating Hibernate\nAdding DAO layer\nImplementing DAO layer\nXML response\nJSON response',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Understanding JAX-RS (Advanced Concepts)',
                'summary': 'Master advanced JAX-RS concepts including subresources, Hibernate relationships, filters, pagination, parameters, status codes, exception handling, and HATEOAS implementation.',
                'learning_objectives': 'Work with subresources\nUnderstand ManyToOne mapping in Hibernate\nDelegate calls to subresources\nImplement filters\nAdd pagination\nUse HeaderParam, CookieParam, and ContextParam\nSend status codes and location headers\nHandle exceptions\nImplement Exception Mapper\nBuild custom exception maps\nImplement HATEOAS',
                'topics': 'Subresource – Setting up table\nAdding subresource on existing resource\nSubresource in action\nManyToOne mapping in Hibernate\nDelegation calls to subresources\nFilters\nPagination\nHeaderParam & CookieParam\nContextParam (Review)\nSending status codes\nLocation headers\nAdd specific entity method\nURI Builder\nWebApplicationException\nException handling with JSON response\nException Mapper\nCustom Exception Map\nHATEOAS (detailed)',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Building REST Client',
                'summary': 'Learn to build REST clients. Create client applications, build URLs, make POST requests, read responses, work with wrapper classes, build HATEOAS models, and implement PUT and DELETE operations.',
                'learning_objectives': 'Understand REST client concepts\nBuild REST client applications\nBuild URLs programmatically\nMake POST requests from client\nRead and parse responses\nWork with wrapper classes\nBuild HATEOAS models\nImplement PUT and DELETE operations from client',
                'topics': 'REST client introduction\nClient building steps\nURL building\nPOST request\nReading response & wrapper class (overview)\nBuilding HATEOAS model\nPUT and DELETE operations',
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

    # Module 1 Questions - Web Services & REST Introduction
    def get_module1_questions(self):
        return [
            {
                'question': 'What does REST stand for?',
                'options': [
                    'Representational State Transfer',
                    'Remote State Transfer',
                    'Resource State Transfer',
                    'Representational Service Transfer'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a resource-based URI?',
                'options': [
                    'A URI that represents a resource (noun) rather than an action',
                    'A URI that contains actions',
                    'A URI that contains verbs',
                    'A URI for database connections'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which HTTP method is idempotent?',
                'options': [
                    'GET',
                    'POST',
                    'PUT',
                    'Both A and C'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does HATEOAS stand for?',
                'options': [
                    'Hypermedia as the Engine of Application State',
                    'Hypertext as the Engine of Application State',
                    'HTTP as the Engine of Application State',
                    'Hyperlink as the Engine of Application State'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is JAX-RS?',
                'options': [
                    'Java API for RESTful Web Services',
                    'Java API for Remote Services',
                    'Java API for REST Services',
                    'Java API for Resource Services'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which is a popular JAX-RS implementation?',
                'options': [
                    'Jersey',
                    'RESTEasy',
                    'Apache CXF',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What are the main principles of REST?',
                'options': [
                    'Stateless, resource-based, uniform interface',
                    'Stateful, action-based, custom interface',
                    'Stateless, action-based, uniform interface',
                    'Stateful, resource-based, custom interface'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What HTTP status code indicates successful creation?',
                'options': [
                    '200 OK',
                    '201 Created',
                    '204 No Content',
                    '202 Accepted'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of HTTP verbs in REST?',
                'options': [
                    'To indicate the operation to perform on a resource',
                    'To indicate the resource type',
                    'To indicate the response format',
                    'To indicate the request format'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which HTTP method is used to retrieve a resource?',
                'options': [
                    'GET',
                    'POST',
                    'PUT',
                    'DELETE'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - Setting Up JAX-RS
    def get_module2_questions(self):
        return [
            {
                'question': 'Which annotation is used to mark a class as a REST resource?',
                'options': [
                    '@Path',
                    '@Resource',
                    '@REST',
                    '@Endpoint'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to handle GET requests?',
                'options': [
                    '@GET',
                    '@POST',
                    '@PUT',
                    '@DELETE'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which annotation is used to extract path parameters?',
                'options': [
                    '@PathParam',
                    '@QueryParam',
                    '@FormParam',
                    '@HeaderParam'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the correct way to define a resource-based URI?',
                'options': [
                    '/users/{userId}',
                    '/getUser/{userId}',
                    '/user/get/{userId}',
                    '/get/user/{userId}'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which HTTP method is typically used for creating resources?',
                'options': [
                    'GET',
                    'POST',
                    'PUT',
                    'DELETE'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of @ApplicationPath annotation?',
                'options': [
                    'To define the base path for all REST resources',
                    'To define a specific resource path',
                    'To define query parameters',
                    'To define path parameters'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which class must extend Application in JAX-RS?',
                'options': [
                    'ResourceConfig (Jersey)',
                    'Application class',
                    'Both A and B',
                    'WebApplication'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of @Produces annotation?',
                'options': [
                    'To specify the media type of the request',
                    'To specify the media type of the response',
                    'To specify the resource path',
                    'To specify query parameters'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of @Consumes annotation?',
                'options': [
                    'To specify the media type of the response',
                    'To specify the media type of the request',
                    'To specify the resource path',
                    'To specify path parameters'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which annotation is used to extract query parameters?',
                'options': [
                    '@PathParam',
                    '@QueryParam',
                    '@FormParam',
                    '@HeaderParam'
                ],
                'correct_answer': 2
            },
        ]

    # Module 3 Questions - Database Connectivity using Hibernate
    def get_module3_questions(self):
        return [
            {
                'question': 'What is the purpose of a Service layer?',
                'options': [
                    'To handle database operations',
                    'To contain business logic',
                    'To manage HTTP requests',
                    'To format responses'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of a DAO layer?',
                'options': [
                    'To contain business logic',
                    'To handle database operations',
                    'To manage HTTP requests',
                    'To format responses'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which annotation is used to produce JSON response?',
                'options': [
                    '@JSON',
                    '@Produces(MediaType.APPLICATION_JSON)',
                    '@ResponseType(JSON)',
                    '@Format(JSON)'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which annotation is used to consume JSON request?',
                'options': [
                    '@JSON',
                    '@Consumes(MediaType.APPLICATION_JSON)',
                    '@RequestType(JSON)',
                    '@Format(JSON)'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of Response class in JAX-RS?',
                'options': [
                    'To build HTTP requests',
                    'To build HTTP responses with status codes and headers',
                    'To validate responses',
                    'To format responses'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you return a 404 Not Found response?',
                'options': [
                    'Response.status(404).build()',
                    'Response.notFound().build()',
                    'Both A and B',
                    'Response.error(404).build()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of Entity class in JAX-RS?',
                'options': [
                    'To represent database entities',
                    'To represent request/response body',
                    'To represent HTTP entities',
                    'To represent REST entities'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of MessageBodyWriter?',
                'options': [
                    'To convert HTTP request body to Java objects',
                    'To convert Java objects to HTTP response body',
                    'To write messages',
                    'To read messages'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of MessageBodyReader?',
                'options': [
                    'To convert Java objects to HTTP response body',
                    'To read messages',
                    'To convert HTTP request body to Java objects',
                    'To write messages'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of @Context annotation?',
                'options': [
                    'To define context path',
                    'To set context variables',
                    'To inject JAX-RS context objects',
                    'To get context information'
                ],
                'correct_answer': 3
            },
        ]

    # Module 4 Questions - Understanding JAX-RS (Advanced Concepts)
    def get_module4_questions(self):
        return [
            {
                'question': 'What is a subresource in JAX-RS?',
                'options': [
                    'A resource method that returns another resource',
                    'A nested resource',
                    'A child resource',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is ManyToOne mapping in Hibernate?',
                'options': [
                    'One entity related to many entities',
                    'Many-to-many relationship',
                    'Many entities related to one entity',
                    'One-to-one relationship'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a Filter in JAX-RS?',
                'options': [
                    'A database filter',
                    'A query filter',
                    'A component that intercepts requests and responses',
                    'A response filter only'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which annotation is used to extract header parameters?',
                'options': [
                    '@PathParam',
                    '@QueryParam',
                    '@HeaderParam',
                    '@CookieParam'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which annotation is used to extract cookie parameters?',
                'options': [
                    '@HeaderParam',
                    '@PathParam',
                    '@CookieParam',
                    '@QueryParam'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is an Exception Mapper?',
                'options': [
                    'A database exception handler',
                    'A validation exception',
                    'A component that maps exceptions to HTTP responses',
                    'A runtime exception'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is URI Builder used for?',
                'options': [
                    'To parse URIs',
                    'To validate URIs',
                    'To build URIs programmatically',
                    'To encode URIs'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between ContainerRequestFilter and ContainerResponseFilter?',
                'options': [
                    'ResponseFilter intercepts requests, RequestFilter intercepts responses',
                    'They are identical',
                    'RequestFilter intercepts requests, ResponseFilter intercepts responses',
                    'RequestFilter is for GET, ResponseFilter is for POST'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is @Priority annotation used for in filters?',
                'options': [
                    'To set filter priority level',
                    'To mark high-priority filters',
                    'To specify the order of filter execution',
                    'To disable filters'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of @NameBinding annotation?',
                'options': [
                    'To bind resources to names',
                    'To bind parameters to names',
                    'To bind responses to names',
                    'To bind filters or interceptors to specific resources'
                ],
                'correct_answer': 4
            },
        ]

    # Module 5 Questions - Building REST Client
    def get_module5_questions(self):
        return [
            {
                'question': 'What is a REST client?',
                'options': [
                    'A REST server',
                    'A database client',
                    'A web browser',
                    'An application that consumes REST APIs'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which class is used to build REST clients in JAX-RS?',
                'options': [
                    'Client',
                    'ClientBuilder',
                    'WebTarget',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you make a POST request from a REST client?',
                'options': [
                    'Using request().post()',
                    'Using post() method',
                    'Using build().post()',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a wrapper class in REST context?',
                'options': [
                    'A primitive wrapper',
                    'A database wrapper',
                    'A service wrapper',
                    'A class that wraps response data'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of Invocation.Builder?',
                'options': [
                    'To build responses',
                    'To build clients',
                    'To build targets',
                    'To build and configure HTTP requests'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you add headers to a REST client request?',
                'options': [
                    'Using header() method on Invocation.Builder',
                    'Using addHeader() method',
                    'Using setHeader() method',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of WebTarget?',
                'options': [
                    'To represent a REST resource',
                    'To represent a REST service',
                    'To represent a REST endpoint',
                    'To represent a target URI for REST client requests'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How do you handle errors in REST client?',
                'options': [
                    'Using Response.getStatus() to check status code',
                    'Using exception handling',
                    'Using error handlers',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of AsyncInvoker in REST client?',
                'options': [
                    'To make asynchronous REST calls',
                    'To make synchronous REST calls',
                    'To validate REST calls',
                    'To log REST calls'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between sync and async REST client calls?',
                'options': [
                    'Sync blocks until response, async returns immediately',
                    'Async blocks until response, sync returns immediately',
                    'They are identical',
                    'Sync is for GET, async is for POST'
                ],
                'correct_answer': 1
            },
        ]

