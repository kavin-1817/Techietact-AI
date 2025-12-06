"""
Management command to seed Core Python course with modules and quizzes
Run with: python manage.py seed_python_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Core Python course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Core Python course
        course, created = Course.objects.get_or_create(
            title='Core Python Programming',
            defaults={
                'description': 'Master the fundamentals of Python programming language. Learn syntax, data structures, object-oriented programming, file handling, and more. This comprehensive course covers everything from basic concepts to advanced Python features.',
                'category': 'programming',
                'is_featured': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Course already exists: {course.title}. Updating modules and quizzes...'))
        
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Core Python course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data with questions"""
        return [
            {
                'order': 1,
                'title': 'Introduction to Python',
                'summary': 'Get started with Python programming. Learn about Python history, features, installation, and write your first Python program.',
                'learning_objectives': 'Understand Python features and advantages\nInstall and configure Python development environment\nWrite and run your first Python program\nUnderstand Python syntax and indentation rules',
                'topics': 'Python History and Features\nPython Installation and Setup\nPython IDEs and Editors\nHello World Program\nPython Syntax and Indentation\nPython Comments and Docstrings',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Python Fundamentals: Variables, Data Types, and Operators',
                'summary': 'Master the building blocks of Python programming. Learn about data types, variables, type conversion, and various operators.',
                'learning_objectives': 'Understand Python data types (int, float, str, bool)\nDeclare and use variables\nPerform type conversion and casting\nUse arithmetic, comparison, logical, and assignment operators',
                'topics': 'Python Data Types\nVariables and Naming Conventions\nType Conversion (int(), float(), str())\nArithmetic Operators\nComparison Operators\nLogical Operators (and, or, not)\nAssignment Operators\nIdentity and Membership Operators',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Control Flow: Conditionals and Loops',
                'summary': 'Learn to control program flow using conditional statements and loops. Master if-elif-else, for loops, while loops, and loop control statements.',
                'learning_objectives': 'Use if-elif-else statements for decision making\nImplement for and while loops\nUnderstand break, continue, and pass statements\nHandle nested control structures',
                'topics': 'If-elif-else Statements\nTernary Operator (Conditional Expression)\nFor Loop and Range Function\nWhile Loop\nBreak and Continue Statements\nPass Statement\nNested Loops\nLoop with else Clause',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Data Structures: Lists, Tuples, Sets, and Dictionaries',
                'summary': 'Work with Python built-in data structures. Learn list, tuple, set, and dictionary operations and methods.',
                'learning_objectives': 'Create and manipulate lists, tuples, sets, and dictionaries\nUnderstand mutability and immutability\nUse built-in methods for data structures\nPerform common operations on collections',
                'topics': 'Lists: Creation, Indexing, Slicing, Methods\nTuples: Creation, Packing, Unpacking\nSets: Creation, Operations, Methods\nDictionaries: Creation, Accessing, Methods\nList Comprehensions\nDictionary Comprehensions\nSet Comprehensions',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Functions and Modules',
                'summary': 'Learn to create reusable code with functions and modules. Understand function definition, parameters, return values, and module organization.',
                'learning_objectives': 'Define and call functions\nUnderstand function parameters and arguments\nUse default arguments, *args, and **kwargs\nCreate and import modules\nUnderstand scope and namespace',
                'topics': 'Function Definition and Calling\nFunction Parameters and Arguments\nDefault Arguments\n*args and **kwargs\nReturn Statement and Multiple Returns\nLambda Functions\nLocal vs Global Scope\nModule Creation and Import\nBuilt-in Modules (math, random, datetime)',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Object-Oriented Programming in Python',
                'summary': 'Dive into object-oriented programming in Python. Learn to create classes, instantiate objects, understand constructors, methods, and inheritance.',
                'learning_objectives': 'Create classes and objects\nUnderstand __init__ method and constructors\nUse instance methods, class methods, and static methods\nImplement inheritance and method overriding',
                'topics': 'Classes and Objects\n__init__ Method (Constructor)\nInstance Methods\nClass Methods and Static Methods\nInstance Variables vs Class Variables\nInheritance and Method Overriding\nSuper() Function\nEncapsulation and Name Mangling',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Advanced OOP: Magic Methods, Properties, and Decorators',
                'summary': 'Explore advanced object-oriented concepts including magic methods, properties, and decorators.',
                'learning_objectives': 'Understand magic methods (__str__, __repr__, etc.)\nUse properties and property decorators\nCreate and use decorators\nUnderstand method resolution order',
                'topics': 'Magic Methods (__str__, __repr__, __len__, etc.)\nOperator Overloading\nProperty Decorator and Getters/Setters\nDecorators: Function and Class Decorators\nMultiple Inheritance and MRO\nAbstract Base Classes\nDuck Typing',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Exception Handling and File I/O',
                'summary': 'Master exception handling and file operations in Python. Learn try-except blocks, custom exceptions, and file reading/writing.',
                'learning_objectives': 'Handle exceptions using try-except-finally\nRaise and create custom exceptions\nRead from and write to files\nWork with different file modes',
                'topics': 'Try-Except-Finally Blocks\nException Types and Hierarchy\nRaising Exceptions\nCustom Exceptions\nFile Operations (open, read, write, close)\nFile Modes (r, w, a, x, b)\nContext Managers (with statement)\nCSV and JSON File Handling',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Working with Strings and Regular Expressions',
                'summary': 'Master string manipulation and pattern matching using regular expressions in Python.',
                'learning_objectives': 'Perform string operations and formatting\nUse string methods effectively\nUnderstand and use regular expressions\nMatch and search patterns in text',
                'topics': 'String Methods (upper, lower, split, join, etc.)\nString Formatting (f-strings, format(), %)\nString Slicing and Indexing\nRegular Expressions (re module)\nPattern Matching and Searching\nGroups and Capturing\nSubstitution and Splitting',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Advanced Topics: Generators, Iterators, and Comprehensions',
                'summary': 'Explore advanced Python features including generators, iterators, list comprehensions, and generator expressions.',
                'learning_objectives': 'Understand iterators and iterables\nCreate generators using yield\nUse list, dictionary, and set comprehensions\nUnderstand generator expressions',
                'topics': 'Iterators and Iterables\nGenerator Functions and yield\nGenerator Expressions\nList Comprehensions\nDictionary and Set Comprehensions\nNested Comprehensions\nMemory Efficiency with Generators',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'Python Mini Project Studio',
                'summary': 'Learn how to translate fresh concepts into tightly scoped Python mini projects for fast validation.',
                'learning_objectives': (
                    'Break a concept into a project brief with Python-first constraints\n'
                    'Select the right tooling (virtualenv, pytest, formatting) for quick builds\n'
                    'Capture insights and feedback loops at each milestone'
                ),
                'topics': (
                    'Problem framing & success metrics\n'
                    'Choosing FastAPI, Flask, or scripts appropriately\n'
                    'pytest-driven feedback loops\n'
                    'Issue templates and lightweight retrospectives'
                ),
                'questions': self.get_module11_questions(),
            },
            {
                'order': 12,
                'title': 'Python End-to-End Delivery Blueprint',
                'summary': 'Design, implement, and ship production-ready Python systems that span API, background work, and deployment.',
                'learning_objectives': (
                    'Model services with FastAPI/Django plus async workers (Celery/RQ)\n'
                    'Package code with type checking, linting, and layered testing\n'
                    'Automate delivery using CI/CD, container images, and observability hooks'
                ),
                'topics': (
                    'API contracts + schema evolution\n'
                    'Task queues and scheduling\n'
                    'Container builds, Compose, and IaC hand-offs\n'
                    'Telemetry: OpenTelemetry, logging, health probes'
                ),
                'questions': self.get_module12_questions(),
            },
            {
                'order': 13,
                'title': 'Python Interview Readiness Lab',
                'summary': 'Master Python-focused interview loops covering algorithms, system design, and behavioral storytelling.',
                'learning_objectives': (
                    'Create reusable approaches for DSA prompts using Python idioms\n'
                    'Discuss system designs referencing async, scaling, and packaging choices\n'
                    'Tell outcome-driven stories that highlight collaboration and impact'
                ),
                'topics': (
                    'Pattern catalog for lists, heaps, graphs\n'
                    'Async + multiprocessing trade-offs\n'
                    'STAR stories, failure analysis, negotiation tips\n'
                    'Mock interview scorecards and follow-up plans'
                ),
                'questions': self.get_module13_questions(),
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

    # Module 1 Questions
    def get_module1_questions(self):
        return [
            {
                'question': 'Who created Python programming language?',
                'options': [
                    'James Gosling',
                    'Guido van Rossum',
                    'Bjarne Stroustrup',
                    'Dennis Ritchie'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the extension of a Python source file?',
                'options': [
                    '.py',
                    '.python',
                    '.pyt',
                    '.pt'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is NOT a feature of Python?',
                'options': [
                    'Interpreted',
                    'Dynamically typed',
                    'Compiled to machine code',
                    'Object-oriented'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is used for indentation in Python?',
                'options': [
                    'Braces {}',
                    'Brackets []',
                    'Spaces or tabs',
                    'Parentheses ()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the correct way to print "Hello, World!" in Python 3?',
                'options': [
                    'print "Hello, World!"',
                    'print("Hello, World!")',
                    'echo "Hello, World!"',
                    'printf("Hello, World!")'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which of the following is a valid Python comment?',
                'options': [
                    '// This is a comment',
                    '# This is a comment',
                    '/* This is a comment */',
                    '<!-- This is a comment -->'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is PEP 8?',
                'options': [
                    'Python Enhancement Proposal for code style',
                    'A Python library',
                    'A Python framework',
                    'A Python version'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command is used to run a Python script?',
                'options': [
                    'python script.py',
                    'run script.py',
                    'execute script.py',
                    'start script.py'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the Python interactive shell called?',
                'options': [
                    'Python Shell',
                    'Python REPL',
                    'Python Console',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which of the following is a Python IDE?',
                'options': [
                    'PyCharm',
                    'IDLE',
                    'Jupyter Notebook',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 2 Questions
    def get_module2_questions(self):
        return [
            {
                'question': 'What is the data type of the value 3.14?',
                'options': [
                    'int',
                    'float',
                    'str',
                    'bool'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which of the following is a mutable data type?',
                'options': [
                    'int',
                    'str',
                    'tuple',
                    'list'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the result of: type(True)',
                'options': [
                    '<class "int">',
                    '<class "bool">',
                    '<class "str">',
                    '<class "float">'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the result of: 5 // 2',
                'options': [
                    '2.5',
                    '2',
                    '3',
                    '2.0'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the result of: 2 ** 3',
                'options': [
                    '6',
                    '8',
                    '9',
                    '5'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which operator is used for exponentiation?',
                'options': [
                    '^',
                    '**',
                    'exp',
                    'pow'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the result of: "Hello" + "World"',
                'options': [
                    'HelloWorld',
                    'Hello World',
                    'Error',
                    'Hello+World'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the result of: 10 == "10"',
                'options': [
                    'True',
                    'False',
                    'Error',
                    'None'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which function is used to convert a value to an integer?',
                'options': [
                    'int()',
                    'integer()',
                    'to_int()',
                    'convert_int()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the result of: bool(0)',
                'options': [
                    'True',
                    'False',
                    '0',
                    'Error'
                ],
                'correct_answer': 2
            },
        ]

    # Module 3 Questions
    def get_module3_questions(self):
        return [
            {
                'question': 'What is the output of: if 5 > 3: print("Yes")',
                'options': [
                    'Yes',
                    'No output',
                    'Error',
                    'True'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the correct syntax for an if-elif-else statement?',
                'options': [
                    'if condition: elif condition: else:',
                    'if condition: elif: else:',
                    'if condition: elif condition: else',
                    'if condition: elif condition: else:'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the output of: for i in range(3): print(i)',
                'options': [
                    '0 1 2',
                    '1 2 3',
                    '0 1 2 3',
                    '1 2'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the break statement do?',
                'options': [
                    'Skips the current iteration',
                    'Exits the loop',
                    'Continues to next iteration',
                    'Pauses execution'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does the continue statement do?',
                'options': [
                    'Exits the loop',
                    'Skips the current iteration',
                    'Stops the program',
                    'Restarts the loop'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output of: x = 5; while x > 0: x -= 1; print(x)',
                'options': [
                    '4 3 2 1 0',
                    '5 4 3 2 1',
                    '4 3 2 1',
                    '5 4 3 2 1 0'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the ternary operator syntax in Python?',
                'options': [
                    'condition ? value1 : value2',
                    'value1 if condition else value2',
                    'if condition value1 else value2',
                    'condition if value1 else value2'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output of: for i in range(1, 5): print(i)',
                'options': [
                    '1 2 3 4',
                    '1 2 3 4 5',
                    '0 1 2 3 4',
                    '0 1 2 3'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the pass statement do?',
                'options': [
                    'Exits the function',
                    'Does nothing (placeholder)',
                    'Skips iteration',
                    'Breaks the loop'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output of: for i in range(3): if i == 1: continue; print(i)',
                'options': [
                    '0 1 2',
                    '0 2',
                    '1 2',
                    '0 1'
                ],
                'correct_answer': 2
            },
        ]

    # Module 4 Questions
    def get_module4_questions(self):
        return [
            {
                'question': 'How do you access the first element of a list?',
                'options': [
                    'list[1]',
                    'list[0]',
                    'list.first()',
                    'list.get(0)'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method adds an element to the end of a list?',
                'options': [
                    'add()',
                    'append()',
                    'insert()',
                    'push()'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between a list and a tuple?',
                'options': [
                    'Lists are immutable, tuples are mutable',
                    'Lists are mutable, tuples are immutable',
                    'There is no difference',
                    'Lists can only store numbers'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output of: [1, 2, 3][1:3]',
                'options': [
                    '[1, 2]',
                    '[2, 3]',
                    '[1, 2, 3]',
                    '[2]'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you create an empty dictionary?',
                'options': [
                    '{}',
                    'dict()',
                    'Both A and B',
                    '[]'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: {1, 2, 3} & {2, 3, 4}',
                'options': [
                    '{1, 2, 3, 4}',
                    '{2, 3}',
                    '{1, 4}',
                    'Error'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which method removes an item from a dictionary?',
                'options': [
                    'remove()',
                    'delete()',
                    'pop()',
                    'discard()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a list comprehension?',
                'options': [
                    'A way to create lists',
                    'A way to iterate lists',
                    'A way to sort lists',
                    'A way to delete lists'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the output of: [x*2 for x in range(3)]',
                'options': [
                    '[0, 2, 4]',
                    '[2, 4, 6]',
                    '[0, 1, 2]',
                    '[1, 2, 3]'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which data structure does not allow duplicate elements?',
                'options': [
                    'List',
                    'Tuple',
                    'Set',
                    'Dictionary'
                ],
                'correct_answer': 3
            },
        ]

    # Module 5 Questions
    def get_module5_questions(self):
        return [
            {
                'question': 'What keyword is used to define a function?',
                'options': [
                    'def',
                    'function',
                    'define',
                    'func'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the output of: def func(): return 5; print(func())',
                'options': [
                    '5',
                    'None',
                    'Error',
                    'func()'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is *args used for?',
                'options': [
                    'To pass keyword arguments',
                    'To pass variable number of positional arguments',
                    'To pass default arguments',
                    'To pass no arguments'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is **kwargs used for?',
                'options': [
                    'To pass variable number of keyword arguments',
                    'To pass positional arguments',
                    'To pass default arguments',
                    'To pass no arguments'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a lambda function?',
                'options': [
                    'A named function',
                    'An anonymous function',
                    'A recursive function',
                    'A built-in function'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the correct syntax for a lambda function?',
                'options': [
                    'lambda x: x*2',
                    'lambda(x): x*2',
                    'lambda x => x*2',
                    'lambda: x*2'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the scope of a variable defined inside a function?',
                'options': [
                    'Global',
                    'Local',
                    'Both',
                    'None'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which keyword is used to import a module?',
                'options': [
                    'include',
                    'import',
                    'require',
                    'using'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output of: def func(x=5): return x; print(func())',
                'options': [
                    '5',
                    'None',
                    'Error',
                    'x'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the return statement do?',
                'options': [
                    'Prints a value',
                    'Exits the function and returns a value',
                    'Continues execution',
                    'Stops the program'
                ],
                'correct_answer': 2
            },
        ]

    # Module 6 Questions
    def get_module6_questions(self):
        return [
            {
                'question': 'What keyword is used to define a class?',
                'options': [
                    'class',
                    'Class',
                    'def',
                    'object'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the special method called when an object is created?',
                'options': [
                    '__init__',
                    '__new__',
                    '__create__',
                    '__construct__'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is self in Python?',
                'options': [
                    'A keyword',
                    'A reference to the instance',
                    'A built-in function',
                    'A module'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between an instance method and a class method?',
                'options': [
                    'Instance methods take self, class methods take cls',
                    'There is no difference',
                    'Instance methods are static',
                    'Class methods cannot access class variables'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What decorator is used for class methods?',
                'options': [
                    '@instancemethod',
                    '@classmethod',
                    '@staticmethod',
                    '@method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is inheritance?',
                'options': [
                    'Creating a new class',
                    'A class inheriting attributes from another class',
                    'Creating an object',
                    'Defining a method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is method overriding?',
                'options': [
                    'Defining a method in a subclass with the same name',
                    'Defining multiple methods with the same name',
                    'Calling a method multiple times',
                    'Deleting a method'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the super() function used for?',
                'options': [
                    'To call the parent class method',
                    'To create a superclass',
                    'To override a method',
                    'To delete a method'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is encapsulation?',
                'options': [
                    'Hiding implementation details',
                    'Inheriting from a class',
                    'Creating multiple objects',
                    'Defining methods'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the output of: class A: pass; a = A(); print(type(a))',
                'options': [
                    "<class '__main__.A'>",
                    "<class 'A'>",
                    "<type 'A'>",
                    'Error'
                ],
                'correct_answer': 1
            },
        ]

    # Module 7 Questions
    def get_module7_questions(self):
        return [
            {
                'question': 'What are magic methods?',
                'options': [
                    'Methods that perform magic',
                    'Special methods with double underscores',
                    'Methods that cannot be called',
                    'Built-in functions'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the __str__ method used for?',
                'options': [
                    'String representation for users',
                    'String representation for developers',
                    'String conversion',
                    'String manipulation'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the __repr__ method used for?',
                'options': [
                    'String representation for users',
                    'Unambiguous string representation for developers',
                    'String conversion',
                    'String manipulation'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is operator overloading?',
                'options': [
                    'Defining how operators work with custom objects',
                    'Using too many operators',
                    'Removing operators',
                    'Changing operator precedence'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a property decorator used for?',
                'options': [
                    'To create properties',
                    'To define getters and setters',
                    'To create methods',
                    'To define classes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a decorator?',
                'options': [
                    'A function that modifies another function',
                    'A class',
                    'A variable',
                    'A module'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is MRO?',
                'options': [
                    'Method Resolution Order',
                    'Multiple Return Order',
                    'Method Return Object',
                    'Multiple Resolution Object'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is duck typing?',
                'options': [
                    'A type system based on behavior',
                    'A type system based on inheritance',
                    'A type system based on classes',
                    'A type system based on modules'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the @property decorator used for?',
                'options': [
                    'To create a property',
                    'To create a getter',
                    'To create a setter',
                    'To create a deleter'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an abstract base class?',
                'options': [
                    'A class that cannot be instantiated',
                    'A class with abstract methods',
                    'A class that must be subclassed',
                    'All of the above'
                ],
                'correct_answer': 4
            },
        ]

    # Module 8 Questions
    def get_module8_questions(self):
        return [
            {
                'question': 'What is exception handling?',
                'options': [
                    'Handling errors in code',
                    'Preventing errors',
                    'Ignoring errors',
                    'Logging errors'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the correct syntax for try-except?',
                'options': [
                    'try: code except: handler',
                    'try: code except Exception: handler',
                    'try: code except Exception as e: handler',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the finally block do?',
                'options': [
                    'Handles exceptions',
                    'Catches exceptions',
                    'Executes regardless of exceptions',
                    'Raises exceptions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What keyword is used to raise an exception?',
                'options': [
                    'raise',
                    'throw',
                    'except',
                    'error'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the base class for all exceptions?',
                'options': [
                    'Exception',
                    'BaseException',
                    'Error',
                    'Throwable'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What file mode opens a file for reading?',
                'options': [
                    "'r'",
                    "'w'",
                    "'a'",
                    "'x'"
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a context manager?',
                'options': [
                    'A way to open files',
                    'A way to handle exceptions',
                    'A way to manage resources',
                    'A way to define classes'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the with statement used for?',
                'options': [
                    'Exception handling',
                    'Loop control',
                    'Context management',
                    'Function definition'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: try: 1/0 except ZeroDivisionError: print("Error")',
                'options': [
                    'ZeroDivisionError',
                    'No output',
                    'Error',
                    'Exception'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you open a file in Python?',
                'options': [
                    'file(filename)',
                    'read(filename)',
                    'open(filename)',
                    'load(filename)'
                ],
                'correct_answer': 3
            },
        ]

    # Module 9 Questions
    def get_module9_questions(self):
        return [
            {
                'question': 'What method converts a string to uppercase?',
                'options': [
                    'uppercase()',
                    'toUpper()',
                    'upper()',
                    'to_upper()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What method splits a string into a list?',
                'options': [
                    'divide()',
                    'separate()',
                    'split()',
                    'break()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is f-string formatting?',
                'options': [
                    'A way to format strings with format()',
                    'A way to format strings with %',
                    'A way to format strings with f prefix',
                    'A way to format strings with template'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: "Hello".replace("l", "L")',
                'options': [
                    'Hello',
                    'HELLO',
                    'HeLLo',
                    'HeLlo'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What module is used for regular expressions?',
                'options': [
                    'regex',
                    'string',
                    're',
                    'pattern'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What method searches for a pattern in a string?',
                'options': [
                    'find()',
                    'match()',
                    'search()',
                    'locate()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: "Python".find("th")',
                'options': [
                    '3',
                    '4',
                    '2',
                    '-1'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What method joins a list of strings?',
                'options': [
                    'combine()',
                    'merge()',
                    'join()',
                    'concat()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: " ".join(["Hello", "World"])',
                'options': [
                    'HelloWorld',
                    'Hello,World',
                    'Hello World',
                    'Hello-World'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does the re.match() function do?',
                'options': [
                    'Matches pattern anywhere in string',
                    'Matches pattern at the end of string',
                    'Matches pattern at the start of string',
                    'Matches all occurrences'
                ],
                'correct_answer': 3
            },
        ]

    # Module 10 Questions
    def get_module10_questions(self):
        return [
            {
                'question': 'What is an iterator?',
                'options': [
                    'A function that returns values',
                    'A class',
                    'An object that can be iterated',
                    'A module'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is an iterable?',
                'options': [
                    'An iterator',
                    'A function',
                    'An object that can return an iterator',
                    'A class'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What keyword is used in a generator function?',
                'options': [
                    'return',
                    'generate',
                    'yield',
                    'produce'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a generator?',
                'options': [
                    'A class',
                    'A module',
                    'A function that returns a generator object',
                    'A variable'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: [x for x in range(3)]',
                'options': [
                    '(0, 1, 2)',
                    '{0, 1, 2}',
                    '[0, 1, 2]',
                    '0 1 2'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a generator expression?',
                'options': [
                    'A list comprehension',
                    'A tuple comprehension',
                    'A generator created with parentheses',
                    'A set comprehension'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the output of: (x*2 for x in range(3))',
                'options': [
                    '[0, 2, 4]',
                    '(0, 2, 4)',
                    '<generator object>',
                    '{0, 2, 4}'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the advantage of generators?',
                'options': [
                    'Speed',
                    'Simplicity',
                    'Memory efficiency',
                    'All of the above'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What method is used to get the next value from an iterator?',
                'options': [
                    'get()',
                    'fetch()',
                    'next()',
                    'retrieve()'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a nested list comprehension?',
                'options': [
                    'A list with nested lists',
                    'A list with multiple dimensions',
                    'A list comprehension inside another',
                    'A list with functions'
                ],
                'correct_answer': 3
            },
        ]

    # Module 11 Questions
    def get_module11_questions(self):
        return [
            {
                'question': 'What should the first section of a Python mini project brief capture?',
                'options': [
                    'Styling preferences for the IDE',
                    'Names of every contributor',
                    'Problem statement, constraints, and success metrics',
                    'Production traffic projections'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which virtual environment tool keeps isolated dependencies for quick prototypes?',
                'options': [
                    'pip freeze',
                    'tar',
                    'venv',
                    'pip install --upgrade'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Why run pytest at every milestone of a mini build?',
                'options': [
                    'It guarantees 100% coverage instantly',
                    'It replaces code reviews',
                    'It removes the need for documentation',
                    'It provides fast regression feedback as scope evolves'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which artifact documents quick lessons learned after each Python experiment?',
                'options': [
                    'Dockerfile',
                    'requirements.txt',
                    'Procfile',
                    'Retrospective note in the repo'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the benefit of keeping mini projects under two weeks of effort?',
                'options': [
                    'They become easier to forget',
                    'They remove the need for planning',
                    'They satisfy compliance requirements',
                    'They surface gaps early without large rewrites'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which tool automates formatting for quick-read diffs in a Python mini project?',
                'options': [
                    'curl',
                    'dig',
                    'scp',
                    'Black'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How can you collect asynchronous feedback during a scoped experiment?',
                'options': [
                    'Push directly to main without review',
                    'Wait for a quarterly meeting',
                    'Email zipped source code',
                    'Open draft pull requests with checklists'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which dependency file should be pinned for reproducible exercises?',
                'options': [
                    'README.md',
                    'CONTRIBUTING.md',
                    'LICENSE',
                    'poetry.lock or requirements.txt'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a lightweight way to track scope changes mid-project?',
                'options': [
                    'Tagging releases hourly',
                    'Renaming the repo',
                    'Rewriting the Git history',
                    'Updating the project Kanban cards and notes'
                ],
                'correct_answer': 4
            },
            {
                'question': 'When should a Python mini project graduate into a larger initiative?',
                'options': [
                    'After it reaches 10k lines of code',
                    'Once the CI pipeline fails',
                    'When the repo receives two stars',
                    'When the experiment validates user value worth scaling'
                ],
                'correct_answer': 4
            },
        ]

    # Module 12 Questions
    def get_module12_questions(self):
        return [
            {
                'question': 'Which framework pairing best suits a Python API plus background worker architecture?',
                'options': [
                    'Tkinter with Paramiko',
                    'Flask with Bash scripts only',
                    'Django templates without views',
                    'FastAPI with Celery/RQ'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Why run mypy and ruff in CI for production Python services?',
                'options': [
                    'They optimize SQL queries automatically',
                    'They deploy to Kubernetes',
                    'They generate changelog entries',
                    'They enforce typing and linting to prevent regressions'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of a health probe endpoint in a FastAPI service?',
                'options': [
                    'Render dashboards',
                    'Store secrets',
                    'Replace authentication',
                    'Provide liveness/readiness signals to orchestrators'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which file typically defines Python dependency metadata for Docker builds?',
                'options': [
                    'docker-compose.yml',
                    'README.md',
                    'alembic.ini',
                    'pyproject.toml or requirements.txt'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does OpenTelemetry instrumentation enable in an end-to-end pipeline?',
                'options': [
                    'Static code analysis',
                    'Secret rotation',
                    'Unit test discovery',
                    'Cross-service tracing and metrics correlation'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which storage strategy helps maintain schema compatibility over time?',
                'options': [
                    'Applying migrations only in production',
                    'Editing tables manually',
                    'Dropping the database on every deploy',
                    'Versioned migrations with Alembic or Django Migrations'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Why include contract tests between FastAPI and a frontend client?',
                'options': [
                    'Ensure UI colors match brand guidelines',
                    'Reduce logging noise',
                    'Speed up database writes',
                    'Validate that payload shapes stay backward compatible'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a safe rollout strategy for Python services consuming third-party APIs?',
                'options': [
                    'Deploy to 100% instantly',
                    'Disable retries entirely',
                    'Ignore rate limits',
                    'Use staged traffic (canary) with feature flags'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which command builds a deterministic container image for deployment?',
                'options': [
                    'pip install -r requirements.txt',
                    'pytest',
                    'git merge origin/main',
                    'docker build -t service:latest .'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Why capture runbooks alongside Terraform or deployment manifests?',
                'options': [
                    'They boost test coverage',
                    'They replace CI pipelines',
                    'They remove the need for monitoring',
                    'They explain recovery steps for on-call engineers'
                ],
                'correct_answer': 4
            },
        ]

    # Module 13 Questions
    def get_module13_questions(self):
        return [
            {
                'question': 'Which Python feature is most persuasive when explaining algorithm choices in interviews?',
                'options': [
                    'Global interpreter lock trivia',
                    'Terminal color customization',
                    'Knowledge of every PEP number',
                    'Time/space trade-offs using built-in data structures'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the primary goal of walking through edge cases before coding?',
                'options': [
                    'Impress the interviewer with syntax',
                    'Shorten the interview time',
                    'Avoid writing tests',
                    'Validate understanding of constraints and failure modes'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which technique keeps Python whiteboard solutions testable?',
                'options': [
                    'Hard-coding stdin reads',
                    'Mutating global state frequently',
                    'Avoiding helper functions',
                    'Writing pure functions with clear inputs/outputs'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How can you showcase familiarity with concurrency in system design interviews?',
                'options': [
                    'Draw a desktop UI mock',
                    'Share screenshot of htop',
                    'Talk about CSS frameworks',
                    'Discuss asyncio, Celery, or multiprocessing trade-offs'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What makes STAR stories compelling for behavioral rounds?',
                'options': [
                    'They repeat the resume verbatim',
                    'They only discuss setbacks',
                    'They rely on jargon',
                    'They provide structured context, actions, and measurable results'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Why keep a post-interview notebook?',
                'options': [
                    'Record coding shortcuts',
                    'Document IDE settings',
                    'Track company stock prices',
                    'Capture questions asked, feedback themes, and follow-up notes'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a strong opening question to clarify during a system design interview?',
                'options': [
                    'Favorite office snack',
                    'Number of interviewers',
                    'Vacation policy',
                    'Expected scale: QPS, users, data retention'
                ],
                'correct_answer': 4
            },
            {
                'question': 'How should you respond when stuck during a coding round?',
                'options': [
                    'Stay silent until you finish',
                    'Ask for the solution',
                    'Change the question',
                    'Verbalize your thought process and consider alternative strategies'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Why is benchmarking important for Python interview take-home tasks?',
                'options': [
                    'It ensures UI looks correct',
                    'It validates performance claims with actual measurements',
                    'It reduces bundle size',
                    'It documents meeting notes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which resource helps calibrate difficulty for upcoming interviews?',
                'options': [
                    'Personal difficulty matrix tracking solved problems',
                    'Random YouTube playlists',
                    'System logs',
                    'Package-lock.json'
                ],
                'correct_answer': 1
            },
        ]



