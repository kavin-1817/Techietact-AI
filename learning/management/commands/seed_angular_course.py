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
            {
                'question': 'What is ES6?',
                'options': [
                    'ECMAScript 2015',
                    'ECMAScript 2016',
                    'ECMAScript 2017',
                    'ECMAScript 2018'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the main advantage of modern web development?',
                'options': [
                    'Better performance',
                    'Component-based architecture',
                    'Better tooling',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is npm?',
                'options': [
                    'Node Package Manager',
                    'Node Program Manager',
                    'Node Project Manager',
                    'Node Process Manager'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of package.json?',
                'options': [
                    'To define project dependencies',
                    'To define project structure',
                    'To define project configuration',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between ES5 and ES6?',
                'options': [
                    'ES6 has new features like arrow functions, classes, and modules',
                    'ES5 has more features',
                    'They are identical',
                    'ES6 is older than ES5'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a transpiler?',
                'options': [
                    'A tool that converts code from one language to another',
                    'A database tool',
                    'A web server',
                    'A testing framework'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of TypeScript compiler?',
                'options': [
                    'To compile TypeScript to JavaScript',
                    'To compile JavaScript to TypeScript',
                    'To compile TypeScript to HTML',
                    'To compile TypeScript to CSS'
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
            {
                'question': 'What is a type alias?',
                'options': [
                    'A way to create a new name for a type',
                    'A way to create a new class',
                    'A way to create a new function',
                    'A way to create a new variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an enum?',
                'options': [
                    'A way to define a set of named constants',
                    'A way to define a class',
                    'A way to define a function',
                    'A way to define a variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between let and const?',
                'options': [
                    'let can be reassigned, const cannot',
                    'const can be reassigned, let cannot',
                    'They are identical',
                    'let is for functions, const is for variables'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is optional chaining?',
                'options': [
                    'A way to safely access nested properties',
                    'A way to chain functions',
                    'A way to chain classes',
                    'A way to chain variables'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a union type?',
                'options': [
                    'A type that can be one of several types',
                    'A type that combines all types',
                    'A type that excludes some types',
                    'A type that is always the same'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a tuple?',
                'options': [
                    'An array with fixed number of elements and known types',
                    'An array with variable length',
                    'A single value',
                    'A function'
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
            {
                'question': 'What command is used to create a new Angular project?',
                'options': [
                    'ng new',
                    'ng create',
                    'ng init',
                    'ng start'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What command is used to serve an Angular application?',
                'options': [
                    'ng serve',
                    'ng start',
                    'ng run',
                    'ng build'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of @NgModule?',
                'options': [
                    'To define an Angular module',
                    'To define a component',
                    'To define a service',
                    'To define a directive'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of declarations in @NgModule?',
                'options': [
                    'To declare components, directives, and pipes',
                    'To declare services',
                    'To declare modules',
                    'To declare routes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of imports in @NgModule?',
                'options': [
                    'To import other modules',
                    'To import components',
                    'To import services',
                    'To import directives'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of providers in @NgModule?',
                'options': [
                    'To provide services',
                    'To provide components',
                    'To provide directives',
                    'To provide pipes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of bootstrap in @NgModule?',
                'options': [
                    'To specify the root component',
                    'To specify the root module',
                    'To specify the root service',
                    'To specify the root directive'
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
            {
                'question': 'What is the purpose of @Component decorator?',
                'options': [
                    'To define a component and its metadata',
                    'To define a service',
                    'To define a directive',
                    'To define a pipe'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the selector in @Component?',
                'options': [
                    'The CSS selector used to identify the component',
                    'The component name',
                    'The component path',
                    'The component type'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is templateUrl?',
                'options': [
                    'The path to the component style file',
                    'The path to the component template file',
                    'The path to the component service file',
                    'The path to the component directive file'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is styleUrls?',
                'options': [
                    'An array of paths to component template files',
                    'An array of paths to component style files',
                    'An array of paths to component service files',
                    'An array of paths to component directive files'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is ngOnInit used for?',
                'options': [
                    'To destroy component',
                    'To initialize component after Angular displays data-bound properties',
                    'To update component',
                    'To create component'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is ngOnDestroy used for?',
                'options': [
                    'To initialize component',
                    'To clean up before component is destroyed',
                    'To update component',
                    'To create component'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is change detection?',
                'options': [
                    'The process of detecting errors',
                    'The process of checking for changes in component data',
                    'The process of detecting components',
                    'The process of detecting services'
                ],
                'correct_answer': 2
            },
        ]

    # Module 5 Questions - Data Binding
    def get_module5_questions(self):
        return [
            {
                'question': 'What is two-way data binding?',
                'options': [
                    'Binding that updates only component',
                    'Binding that updates both component and view',
                    'Binding that updates only view',
                    'No binding'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which syntax is used for string interpolation?',
                'options': [
                    '{{}}',
                    '{{ }}',
                    '[ ]',
                    '( )'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is @Input() used for?',
                'options': [
                    'To pass data from child to parent',
                    'To pass data from parent to child component',
                    'To get user input',
                    'To handle events'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is @Output() used for?',
                'options': [
                    'To receive data from parent',
                    'To emit events from child to parent component',
                    'To output data',
                    'To handle output'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is property binding?',
                'options': [
                    'Binding DOM element property to component property',
                    'Binding component property to DOM element property',
                    'Binding two component properties',
                    'Binding two DOM element properties'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is event binding?',
                'options': [
                    'Binding component methods to DOM events',
                    'Binding DOM events to component methods',
                    'Binding two events',
                    'Binding two methods'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What syntax is used for property binding?',
                'options': [
                    '{{property}}="value"',
                    '[property]="value"',
                    '(property)="value"',
                    '*property="value"'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What syntax is used for event binding?',
                'options': [
                    '[event]="handler()"',
                    '(event)="handler()"',
                    '{{event}}="handler()"',
                    '*event="handler()"'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What syntax is used for two-way binding?',
                'options': [
                    '[ngModel]="property"',
                    '[(ngModel)]="property"',
                    '(ngModel)="property"',
                    '*ngModel="property"'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is EventEmitter used for?',
                'options': [
                    'To receive events',
                    'To emit custom events from components',
                    'To handle events',
                    'To bind events'
                ],
                'correct_answer': 2
            },
        ]

    # Module 6 Questions - Directives
    def get_module6_questions(self):
        return [
            {
                'question': 'What is the difference between attribute and structural directives?',
                'options': [
                    'They are the same',
                    'Structural directives change DOM structure, attribute directives change appearance',
                    'Attribute directives change DOM structure',
                    'Structural directives change appearance'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which directive is used for conditional rendering?',
                'options': [
                    '*ngFor',
                    '*ngIf',
                    '*ngSwitch',
                    'All of the above'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is ng-container used for?',
                'options': [
                    'To create a visible container element',
                    'A container that doesn\'t render in the DOM',
                    'To create a component',
                    'To create a service'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which directive is used for looping?',
                'options': [
                    '*ngIf',
                    '*ngFor',
                    '*ngSwitch',
                    '*ngClass'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is *ngSwitch used for?',
                'options': [
                    'To switch components',
                    'To switch between multiple views based on a value',
                    'To switch services',
                    'To switch directives'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is [ngClass] used for?',
                'options': [
                    'To apply styles',
                    'To conditionally apply CSS classes',
                    'To apply components',
                    'To apply services'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is [ngStyle] used for?',
                'options': [
                    'To apply CSS classes',
                    'To conditionally apply inline styles',
                    'To apply components',
                    'To apply services'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a custom directive?',
                'options': [
                    'A built-in directive',
                    'A directive created by the developer',
                    'A component directive',
                    'A service directive'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is @Directive decorator used for?',
                'options': [
                    'To define a component',
                    'To define a directive',
                    'To define a service',
                    'To define a pipe'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between *ngIf and [hidden]?',
                'options': [
                    '[hidden] removes element from DOM, *ngIf just hides it',
                    '*ngIf removes element from DOM, [hidden] just hides it',
                    'They are identical',
                    '*ngIf is for components, [hidden] is for directives'
                ],
                'correct_answer': 2
            },
        ]

    # Module 7 Questions - Pipes
    def get_module7_questions(self):
        return [
            {
                'question': 'What is a pipe in Angular?',
                'options': [
                    'A component',
                    'A feature that transforms data in templates',
                    'A service',
                    'A directive'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between pure and impure pipes?',
                'options': [
                    'They are the same',
                    'Pure pipes are called only when input changes, impure on every change detection',
                    'Impure pipes are faster',
                    'Pure pipes are slower'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you use a pipe?',
                'options': [
                    '{{ value pipeName }}',
                    '[value | pipeName]',
                    '{{ value | pipeName }}',
                    '(value | pipeName)'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the date pipe used for?',
                'options': [
                    'To format numbers',
                    'To format dates',
                    'To format strings',
                    'To format arrays'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the currency pipe used for?',
                'options': [
                    'To format dates',
                    'To format currency values',
                    'To format strings',
                    'To format arrays'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the uppercase pipe used for?',
                'options': [
                    'To convert text to lowercase',
                    'To format dates',
                    'To convert text to uppercase',
                    'To format numbers'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the lowercase pipe used for?',
                'options': [
                    'To convert text to uppercase',
                    'To format dates',
                    'To convert text to lowercase',
                    'To format numbers'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a custom pipe?',
                'options': [
                    'A built-in pipe',
                    'A component pipe',
                    'A pipe created by the developer',
                    'A service pipe'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is @Pipe decorator used for?',
                'options': [
                    'To define a component',
                    'To define a service',
                    'To define a pipe',
                    'To define a directive'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the async pipe used for?',
                'options': [
                    'To format dates',
                    'To format numbers',
                    'To subscribe to Observables and Promises',
                    'To format strings'
                ],
                'correct_answer': 3
            },
        ]

    # Module 8 Questions - Services & Dependency Injection
    def get_module8_questions(self):
        return [
            {
                'question': 'What is a service in Angular?',
                'options': [
                    'A component',
                    'A directive',
                    'A class that provides functionality to components',
                    'A pipe'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is dependency injection?',
                'options': [
                    'Creating dependencies',
                    'Injecting code',
                    'A design pattern where dependencies are provided rather than created',
                    'A security feature'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What annotation is used to make a class injectable?',
                'options': [
                    '@Service()',
                    '@Component()',
                    '@Injectable()',
                    '@Inject()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you inject a service into a component?',
                'options': [
                    'Through ngOnInit',
                    'Through ngOnDestroy',
                    'Through constructor',
                    'Through template'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of providedIn in @Injectable?',
                'options': [
                    'To specify service name',
                    'To specify service type',
                    'To specify where the service should be provided',
                    'To specify service path'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a singleton service?',
                'options': [
                    'A service with multiple instances',
                    'A service without instances',
                    'A service with a single instance',
                    'A service with shared instances'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between providedIn: root and providedIn: any?',
                'options': [
                    'any provides singleton, root provides separate instance',
                    'They are identical',
                    'root provides singleton, any provides separate instance per module',
                    'root is for components, any is for services'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the inject() function used for?',
                'options': [
                    'To inject components',
                    'To inject directives',
                    'To inject dependencies in functional code',
                    'To inject pipes'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a provider?',
                'options': [
                    'A way to create components',
                    'A way to create directives',
                    'A way to configure how dependencies are created',
                    'A way to create pipes'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of useClass in providers?',
                'options': [
                    'To specify service name',
                    'To specify service type',
                    'To specify which class to use for dependency',
                    'To specify service path'
                ],
                'correct_answer': 3
            },
        ]

    # Module 9 Questions - Template-Driven Forms
    def get_module9_questions(self):
        return [
            {
                'question': 'What is FormsModule used for?',
                'options': [
                    'To enable reactive forms',
                    'To create forms',
                    'To enable template-driven forms',
                    'To validate forms'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ngModel used for?',
                'options': [
                    'One-way binding',
                    'Event binding',
                    'Two-way data binding in forms',
                    'Property binding'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does "dirty" mean in form validation?',
                'options': [
                    'The field is invalid',
                    'The field is empty',
                    'The field has been modified',
                    'The field is touched'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does "touched" mean in form validation?',
                'options': [
                    'The field has been modified',
                    'The field is invalid',
                    'The field has been focused and blurred',
                    'The field is empty'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ngForm used for?',
                'options': [
                    'To create a form control',
                    'To create a form group',
                    'To create a form and track its state',
                    'To create a form array'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ngModelGroup used for?',
                'options': [
                    'To create a form',
                    'To create a form control',
                    'To group form controls',
                    'To create a form array'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What are built-in validators?',
                'options': [
                    'Custom validators',
                    'Component validators',
                    'Predefined validators like required, min, max',
                    'Service validators'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a custom validator?',
                'options': [
                    'A built-in validator',
                    'A component validator',
                    'A validator created by the developer',
                    'A service validator'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of #form="ngForm"?',
                'options': [
                    'To create a form control',
                    'To create a form group',
                    'To create a template reference variable for the form',
                    'To create a form array'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between template-driven and reactive forms?',
                'options': [
                    'Reactive uses directives in template, template-driven uses FormBuilder',
                    'They are identical',
                    'Template-driven uses directives in template, reactive uses FormBuilder in component',
                    'Template-driven is for components, reactive is for services'
                ],
                'correct_answer': 3
            },
        ]

    # Module 10 Questions - Reactive Forms
    def get_module10_questions(self):
        return [
            {
                'question': 'What is FormGroup?',
                'options': [
                    'A single form control',
                    'A form array',
                    'A collection of form controls',
                    'A form builder'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is FormBuilder used for?',
                'options': [
                    'To build forms',
                    'To validate forms',
                    'To simplify form creation',
                    'To submit forms'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between setValue and patchValue?',
                'options': [
                    'They are the same',
                    'patchValue requires all fields',
                    'setValue requires all fields, patchValue allows partial updates',
                    'setValue allows partial updates'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is FormControl?',
                'options': [
                    'A form group',
                    'A form array',
                    'A single form control',
                    'A form builder'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is FormArray?',
                'options': [
                    'A single form control',
                    'A form group',
                    'A form builder',
                    'An array of form controls'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is ReactiveFormsModule used for?',
                'options': [
                    'To enable template-driven forms',
                    'To create forms',
                    'To validate forms',
                    'To enable reactive forms'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is [formGroup] used for?',
                'options': [
                    'To bind a FormControl',
                    'To bind a FormArray',
                    'To bind a FormBuilder',
                    'To bind a FormGroup to a form element'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is formControlName used for?',
                'options': [
                    'To bind a FormGroup',
                    'To bind a FormArray',
                    'To bind a FormBuilder',
                    'To bind a FormControl to an input element'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is Validators.required used for?',
                'options': [
                    'To make a field optional',
                    'To make a field valid',
                    'To make a field invalid',
                    'To make a field required'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of get() method in FormGroup?',
                'options': [
                    'To get a FormGroup',
                    'To get a FormArray',
                    'To get a FormBuilder',
                    'To get a FormControl from FormGroup'
                ],
                'correct_answer': 4
            },
        ]

    # Module 11 Questions - HTTP & Reactive Programming
    def get_module11_questions(self):
        return [
            {
                'question': 'What is an Observable?',
                'options': [
                    'A promise',
                    'A function',
                    'A variable',
                    'A stream of data over time'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between Observable and Promise?',
                'options': [
                    'They are the same',
                    'Promises can emit multiple values',
                    'Observables are synchronous',
                    'Observables can emit multiple values, Promises emit one'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a Subject?',
                'options': [
                    'A promise',
                    'A component',
                    'A service',
                    'A special type of Observable that can multicast'
                ],
                'correct_answer': 4
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
            {
                'question': 'What is HttpClient used for?',
                'options': [
                    'To make HTTP requests',
                    'To handle HTTP responses',
                    'To intercept HTTP requests',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is subscribe() used for?',
                'options': [
                    'To unsubscribe from an Observable',
                    'To create an Observable',
                    'To destroy an Observable',
                    'To subscribe to an Observable'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is map() operator used for?',
                'options': [
                    'To filter Observable values',
                    'To combine Observables',
                    'To create Observables',
                    'To transform Observable values'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is catchError() operator used for?',
                'options': [
                    'To create errors',
                    'To ignore errors',
                    'To throw errors',
                    'To handle errors in Observables'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is RxJS?',
                'options': [
                    'React JavaScript',
                    'React Extensions',
                    'Reactive JavaScript',
                    'Reactive Extensions for JavaScript'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of takeUntil() operator?',
                'options': [
                    'To subscribe to an Observable',
                    'To create an Observable',
                    'To destroy an Observable',
                    'To unsubscribe when a signal is emitted'
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
                    'A service',
                    'A component',
                    'A directive',
                    'A mapping between URL and component'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is RouterOutlet used for?',
                'options': [
                    'To navigate',
                    'To configure routes',
                    'To guard routes',
                    'To display routed components'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a route guard?',
                'options': [
                    'A component',
                    'A service',
                    'A directive',
                    'A mechanism to control route access'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is CanActivate used for?',
                'options': [
                    'To activate routes',
                    'To deactivate routes',
                    'To navigate routes',
                    'To control if a route can be activated'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is RouterModule used for?',
                'options': [
                    'To disable routing',
                    'To configure routing',
                    'To guard routes',
                    'To enable routing in Angular'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is routerLink used for?',
                'options': [
                    'To configure routes',
                    'To guard routes',
                    'To display routes',
                    'To navigate to routes'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is routerLinkActive used for?',
                'options': [
                    'To activate routes',
                    'To deactivate routes',
                    'To navigate routes',
                    'To apply CSS class when route is active'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a route parameter?',
                'options': [
                    'A parameter passed in component',
                    'A parameter passed in service',
                    'A parameter passed in directive',
                    'A parameter passed in the URL'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is ActivatedRoute used for?',
                'options': [
                    'To activate routes',
                    'To deactivate routes',
                    'To navigate routes',
                    'To access route information'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is CanDeactivate used for?',
                'options': [
                    'To activate routes',
                    'To navigate routes',
                    'To display routes',
                    'To control if a route can be deactivated'
                ],
                'correct_answer': 4
            },
        ]

