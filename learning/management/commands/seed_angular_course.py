"""
Management command to seed Angular Training course with complete modules and topics
Run with: python manage.py seed_angular_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Angular Training course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Angular course
        course, created = Course.objects.get_or_create(
            title='ANGULAR TRAINING COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete Angular training course covering TypeScript fundamentals, Angular setup, components, data binding, directives, pipes, services, forms, HTTP, RxJS, and routing.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Angular Training course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Introduction to Modern Web Development',
                'summary': 'Introduction to modern web development. Learn about traditional vs modern web development, Node.js, ES5 vs ES6, TypeScript advantages, and AngularJS vs Angular.',
                'learning_objectives': 'Understand web development evolution\nCompare traditional vs modern web development\nUnderstand Node.js vs traditional servers\nLearn ES5 vs ES6 differences\nUnderstand issues with ES5 JavaScript\nLearn why TypeScript is used\nCompare AngularJS vs Angular 2+\nUnderstand current web development scenario',
                'topics': 'Introduction to web development\nTraditional vs Modern Web Development\nTraditional Servers vs Node.js\nOld vs Modern JavaScript\nIssues with ES5 JavaScript\nES5 vs ES6\nWhy TypeScript? Advantages\nAngularJS vs Angular 2/4/5/6\nCurrent Web Development Scenario',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'TypeScript Fundamentals',
                'summary': 'Master TypeScript fundamentals. Learn typing system, types, enums, arrays, functions, arrow functions, interfaces, OOP, classes, generics, and decorators.',
                'learning_objectives': 'Understand TypeScript typing system\nLearn TypeScript types\nWork with enums, consts & type aliases\nUse array types\nMaster functions and arrow functions\nUnderstand interfaces\nLearn object-oriented programming\nWork with classes, constructors, properties, methods\nUnderstand generics\nLearn decorators',
                'topics': 'Typing system\nTypeScript types\nEnums, consts & type aliases\nArray types\nFunctions\nOptional & default parameters\nArrow functions\nInterfaces\nObject-oriented programming\nClasses & constructors\nProperties, methods, getters & setters\nGenerics\nDecorators',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Angular Setup & Architecture',
                'summary': 'Set up Angular development environment. Learn Angular CLI, application structure, modules, root and feature modules, lazy loading, and dependency injection.',
                'learning_objectives': 'Install Angular\nUse Angular CLI\nServe and build applications\nUnderstand application structure\nLearn Angular Modules\nUnderstand root and feature modules\nImplement lazy loading\nLearn imports, declarations, providers & dependencies',
                'topics': 'Angular installation\nAngular CLI\nServing & building the application\nApplication structure\nAngular Modules\nRoot & Feature Modules\nLazy loading\nImports, declarations, providers & dependencies',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Components',
                'summary': 'Master Angular components. Learn component syntax, selectors, templates, styles, nested components, lifecycle hooks, view encapsulation, and reusable components.',
                'learning_objectives': 'Understand what components are\nLearn role of components\nWork with root component\nMaster component syntax\nUse selectors, templates, styles\nCreate nested components\nUnderstand component lifecycle\nUse initialization and destroy hooks\nLearn view encapsulation\nCreate reusable components\nDynamically create components',
                'topics': 'What are components?\nRole of components\nRoot component\nComponent syntax\nSelectors, templates, styles\nNested components\nComponent lifecycle\nInitialization hooks\nDestroy hooks\nView encapsulation\nWeb components\nReusable components\nDynamically creating components\nEntry components',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Data Binding',
                'summary': 'Learn Angular data binding. Master string interpolation, property binding, event binding, two-way binding, component communication, Input/Output, ViewChild, and event emitters.',
                'learning_objectives': 'Understand Angular data binding\nUse string interpolation\nImplement property binding\nUse event binding\nMaster two-way data binding\nWork with template variables\nEnable component communication\nUse Input / Output\nWork with ViewChild\nLearn content projection\nUse event emitters\nUnderstand smart & dumb components',
                'topics': 'Angular data binding\nString interpolation\nProperty binding\nEvent binding\nTwo-way data binding\nTemplate variables\nComponent communication\nInput / Output\nViewChild\nContent projection\nEvent emitters\nSmart & dumb components\nContainer & presentational components',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Directives',
                'summary': 'Master Angular directives. Learn attribute and structural directives, built-in directives (NgIf, NgFor, NgSwitch), ng-container, ng-template, and custom directives.',
                'learning_objectives': 'Understand Angular directives\nLearn attribute directives\nMaster structural directives\nUse built-in directives (NgIf, NgFor, NgSwitch)\nWork with ng-container\nUse ng-template & template outlets\nUnderstand template context\nCreate custom directives\nWork with ElementRefs & Renderers\nUse host binding & host listeners',
                'topics': 'Angular directives\nAttribute directives\nStructural directives\nBuilt-in directives:\nNgIf\nNgFor\nNgSwitch\nng-container\nng-template & template outlets\nTemplate context\nCustom directives\nElementRefs & Renderers\nHost binding & host listeners',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Pipes',
                'summary': 'Learn Angular pipes. Use built-in pipes (Currency, Number, Percent, Lowercase, Uppercase, Date), create custom pipes, and understand pure vs impure pipes.',
                'learning_objectives': 'Understand what pipes are\nUse built-in pipes\nWork with Currency, Number, Percent pipes\nUse Lowercase & Uppercase pipes\nFormat dates\nCreate custom pipes\nAdd parameters to custom pipes\nUnderstand pure vs impure pipes',
                'topics': 'What are pipes\nBuilt-in pipes\nCurrency, Number, Percent\nLowercase & Uppercase\nDate\nCustom pipes\nCustom pipes with parameters\nPure vs Impure pipes',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Services & Dependency Injection',
                'summary': 'Master Angular services and dependency injection. Learn to create injectable services, understand singletons, export/import services, and provide services at component and global levels.',
                'learning_objectives': 'Understand what services are\nCreate injectable services\nMaster dependency injection\nUnderstand singletons\nExport and import services\nCreate shared services\nProvide services at component level\nProvide services at global level',
                'topics': 'What are services\nInjectable services\nDependency injection\nSingletons\nExport & import services\nShared services\nProviding services\nComponent level\nGlobal level',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Template-Driven Forms',
                'summary': 'Learn template-driven forms in Angular. Use FormsModule, ngForm, ngModel, implement form validations, handle form states, and work with various input types.',
                'learning_objectives': 'Use FormsModule\nCreate template-driven forms\nWork with ngForm & ngSubmit\nUse ngModel for two-way binding\nImplement form validations\nUnderstand touched/untouched states\nUnderstand dirty/pristine states\nHandle valid/invalid states\nSubmit forms\nValidate passwords and confirm passwords\nWork with checkboxes, radio buttons, select inputs, ranges',
                'topics': 'FormsModule\nTemplate-driven forms\nngForm & ngSubmit\nngModel & two-way binding\nForm validations\nTouched / Untouched\nDirty / Pristine\nValid / Invalid states\nForm submit\nPassword & confirm-password validations\nCheckboxes, radio buttons, select inputs, ranges',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Reactive Forms',
                'summary': 'Master reactive forms in Angular. Learn FormGroup, FormControl, FormArray, FormBuilder, validators, custom validators, async validators, and form value subscriptions.',
                'learning_objectives': 'Understand reactive forms\nCompare reactive vs template-driven forms\nWork with FormGroup\nUse FormControl\nImplement FormArray\nUse FormBuilder\nApply validators (required, min, max, pattern)\nCreate custom validators\nCreate custom async validators\nSubscribe to form values\nSet and patch values\nReset forms\nHandle form status changes\nHandle inputs dynamically',
                'topics': 'What are reactive forms\nReactive vs Template-driven\nFormGroup\nFormControl\nFormArray\nFormBuilder\nValidators\nRequired, min, max, pattern\nCustom validators\nCustom async validators\nSubscribing to form values\nSetting & patching values\nResetting form\nForm status changes\nHandling inputs dynamically',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'HTTP & Reactive Programming (RxJS)',
                'summary': 'Learn HTTP communication and reactive programming. Use HttpClientModule, work with Observables, Subscriptions, Subjects, make HTTP requests (GET, POST, PUT, DELETE), handle errors, and use HTTP interceptors.',
                'learning_objectives': 'Use HttpClientModule\nUnderstand Promises\nLearn reactive programming\nWork with Observables\nHandle Subscriptions\nUse Subjects & BehaviorSubjects\nWork with JSONP\nMake GET, POST, PUT, DELETE requests\nHandle errors\nWork with APIs\nImplement HTTP interceptors',
                'topics': 'HttpClientModule\nPromises\nReactive programming\nObservables\nSubscriptions\nSubjects & BehaviorSubjects\nJSONP\nGET, POST, PUT, DELETE requests\nError handling\nWorking with APIs\nHTTP interceptors',
                'questions': self.get_module11_questions(),
            },
            {
                'order': 12,
                'title': 'Routing & Navigation',
                'summary': 'Master Angular routing and navigation. Configure routes, use RouterLink, work with route parameters, query params, implement route guards (CanActivate, CanDeactivate), and create child routes.',
                'learning_objectives': 'Understand what routes are\nConfigure routes\nUse Router outlet\nImplement RouterLink & navigation\nBuild SPA (Single Page Applications)\nWork with route parameters\nSubscribe to params\nConfigure root module & child module routes\nUse query params\nWork with ActivatedRoute\nImplement route guards\nUse CanActivate\nUse CanDeactivate\nCreate child routes',
                'topics': 'What are routes\nConfiguring routes\nRouter outlet\nRouterLink & navigation\nSPA (Single Page Applications)\nRoute parameters\nSubscribing to params\nRoot module & child module routes\nQuery params\nActivatedRoute\nRoute guards\nCanActivate\nCanDeactivate\nChild routes',
                'questions': self.get_module12_questions(),
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

    # Module 1 Questions - Introduction to Modern Web Development
    def get_module1_questions(self):
        return [
            {
                'question': 'What is the main advantage of TypeScript over JavaScript?',
                'options': [
                    'Static typing',
                    'Better IDE support',
                    'Early error detection',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the key difference between AngularJS and Angular 2+?',
                'options': [
                    'Angular 2+ uses TypeScript',
                    'Angular 2+ has component-based architecture',
                    'Angular 2+ has better performance',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is Node.js?',
                'options': [
                    'JavaScript runtime built on Chrome\'s V8 engine',
                    'A database',
                    'A web framework',
                    'A programming language'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - TypeScript Fundamentals
    def get_module2_questions(self):
        return [
            {
                'question': 'What is a decorator in TypeScript?',
                'options': [
                    'A special kind of declaration that can be attached to classes, methods, etc.',
                    'A function',
                    'A class',
                    'A variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the syntax for arrow functions?',
                'options': [
                    '() => {}',
                    'function() {}',
                    'arrow function() {}',
                    '() function {}'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an interface in TypeScript?',
                'options': [
                    'A contract that defines the structure of an object',
                    'A class',
                    'A function',
                    'A variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What are generics used for?',
                'options': [
                    'To create reusable components that work with multiple types',
                    'To generate code',
                    'To create generic classes',
                    'To handle errors'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions - Angular Setup & Architecture
    def get_module3_questions(self):
        return [
            {
                'question': 'What is Angular CLI?',
                'options': [
                    'Command Line Interface for Angular',
                    'A database',
                    'A web server',
                    'A testing framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is lazy loading?',
                'options': [
                    'Loading modules on-demand',
                    'Loading all modules at once',
                    'Loading modules slowly',
                    'Not loading modules'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the root module in Angular?',
                'options': [
                    'AppModule',
                    'RootModule',
                    'MainModule',
                    'CoreModule'
                ],
                'correct_answer': 1
            },
        ]

    # Module 4 Questions - Components
    def get_module4_questions(self):
        return [
            {
                'question': 'What is a component in Angular?',
                'options': [
                    'A building block of Angular applications',
                    'A service',
                    'A directive',
                    'A pipe'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which lifecycle hook is called first?',
                'options': [
                    'ngOnInit',
                    'ngOnChanges',
                    'ngAfterViewInit',
                    'ngOnDestroy'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is view encapsulation?',
                'options': [
                    'Isolating component styles',
                    'Hiding components',
                    'Encapsulating data',
                    'Protecting components'
                ],
                'correct_answer': 1
            },
        ]

    # Module 5 Questions - Data Binding
    def get_module5_questions(self):
        return [
            {
                'question': 'What is two-way data binding?',
                'options': [
                    'Binding that updates both component and view',
                    'Binding that updates only component',
                    'Binding that updates only view',
                    'No binding'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which syntax is used for string interpolation?',
                'options': [
                    '{{ }}',
                    '{{}}',
                    '[ ]',
                    '( )'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is @Input() used for?',
                'options': [
                    'To pass data from parent to child component',
                    'To pass data from child to parent',
                    'To get user input',
                    'To handle events'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is @Output() used for?',
                'options': [
                    'To emit events from child to parent component',
                    'To receive data from parent',
                    'To output data',
                    'To handle output'
                ],
                'correct_answer': 1
            },
        ]

    # Module 6 Questions - Directives
    def get_module6_questions(self):
        return [
            {
                'question': 'What is the difference between attribute and structural directives?',
                'options': [
                    'Structural directives change DOM structure, attribute directives change appearance',
                    'They are the same',
                    'Attribute directives change DOM structure',
                    'Structural directives change appearance'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which directive is used for conditional rendering?',
                'options': [
                    '*ngIf',
                    '*ngFor',
                    '*ngSwitch',
                    'All of the above'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is ng-container used for?',
                'options': [
                    'A container that doesn\'t render in DOM',
                    'A visible container',
                    'A styling container',
                    'A data container'
                ],
                'correct_answer': 1
            },
        ]

    # Module 7 Questions - Pipes
    def get_module7_questions(self):
        return [
            {
                'question': 'What is a pipe in Angular?',
                'options': [
                    'A feature that transforms data in templates',
                    'A component',
                    'A service',
                    'A directive'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between pure and impure pipes?',
                'options': [
                    'Pure pipes are called only when input changes, impure on every change detection',
                    'They are the same',
                    'Impure pipes are faster',
                    'Pure pipes are slower'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you use a pipe?',
                'options': [
                    '{{ value | pipeName }}',
                    '{{ value pipeName }}',
                    '[value | pipeName]',
                    '(value | pipeName)'
                ],
                'correct_answer': 1
            },
        ]

    # Module 8 Questions - Services & Dependency Injection
    def get_module8_questions(self):
        return [
            {
                'question': 'What is a service in Angular?',
                'options': [
                    'A class that provides functionality to components',
                    'A component',
                    'A directive',
                    'A pipe'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is dependency injection?',
                'options': [
                    'A design pattern where dependencies are provided rather than created',
                    'Creating dependencies',
                    'Injecting code',
                    'A security feature'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What annotation is used to make a class injectable?',
                'options': [
                    '@Injectable()',
                    '@Service()',
                    '@Component()',
                    '@Inject()'
                ],
                'correct_answer': 1
            },
        ]

    # Module 9 Questions - Template-Driven Forms
    def get_module9_questions(self):
        return [
            {
                'question': 'What is FormsModule used for?',
                'options': [
                    'To enable template-driven forms',
                    'To enable reactive forms',
                    'To create forms',
                    'To validate forms'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is ngModel used for?',
                'options': [
                    'Two-way data binding in forms',
                    'One-way binding',
                    'Event binding',
                    'Property binding'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does "dirty" mean in form validation?',
                'options': [
                    'The field has been modified',
                    'The field is invalid',
                    'The field is empty',
                    'The field is touched'
                ],
                'correct_answer': 1
            },
        ]

    # Module 10 Questions - Reactive Forms
    def get_module10_questions(self):
        return [
            {
                'question': 'What is FormGroup?',
                'options': [
                    'A collection of form controls',
                    'A single form control',
                    'A form array',
                    'A form builder'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is FormBuilder used for?',
                'options': [
                    'To simplify form creation',
                    'To build forms',
                    'To validate forms',
                    'To submit forms'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between setValue and patchValue?',
                'options': [
                    'setValue requires all fields, patchValue allows partial updates',
                    'They are the same',
                    'patchValue requires all fields',
                    'setValue allows partial updates'
                ],
                'correct_answer': 1
            },
        ]

    # Module 11 Questions - HTTP & Reactive Programming
    def get_module11_questions(self):
        return [
            {
                'question': 'What is an Observable?',
                'options': [
                    'A stream of data over time',
                    'A promise',
                    'A function',
                    'A variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between Observable and Promise?',
                'options': [
                    'Observables can emit multiple values, Promises emit one',
                    'They are the same',
                    'Promises can emit multiple values',
                    'Observables are synchronous'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a Subject?',
                'options': [
                    'A special type of Observable that can multicast',
                    'A promise',
                    'A component',
                    'A service'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What are HTTP interceptors used for?',
                'options': [
                    'To intercept HTTP requests and responses',
                    'To handle errors',
                    'To validate requests',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 12 Questions - Routing & Navigation
    def get_module12_questions(self):
        return [
            {
                'question': 'What is a route in Angular?',
                'options': [
                    'A mapping between URL and component',
                    'A service',
                    'A component',
                    'A directive'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is RouterOutlet used for?',
                'options': [
                    'To display routed components',
                    'To navigate',
                    'To configure routes',
                    'To guard routes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a route guard?',
                'options': [
                    'A mechanism to control route access',
                    'A component',
                    'A service',
                    'A directive'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is CanActivate used for?',
                'options': [
                    'To control if a route can be activated',
                    'To activate routes',
                    'To deactivate routes',
                    'To navigate routes'
                ],
                'correct_answer': 1
            },
        ]

