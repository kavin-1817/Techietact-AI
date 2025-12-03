"""
Management command to seed Java course with complete modules and topics
Run with: python manage.py seed_java_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Java course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Java course
        course, created = Course.objects.get_or_create(
            title='JAVA COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete Java programming course covering all fundamental and advanced concepts. Learn from basics to advanced topics including OOP, Collections, Generics, Lambda expressions, File Handling, and Git basics.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Java course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data with questions"""
        return [
            {
                'order': 1,
                'title': 'Introduction to Java',
                'summary': 'Get started with Java programming. Learn about Java background, write your first program, understand variables, data types, type casting, and string basics.',
                'learning_objectives': 'Understand Java background and history\nWrite your first Java program\nLearn about variables and data types\nUnderstand primitive data types (Integer, Floating point, Boolean, char)\nLearn about BigDecimal class\nMaster String basics and type casting',
                'topics': 'Background\nOur first Java program\nVariable and data type\nUnderstanding variables\nPrimitive data types (Integer)\nPrimitive data types (Floating point)\nPrimitive data types (Boolean and char)\nBigDecimal class introduction\nString basics\nType casting',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Java Development Tools',
                'summary': 'Learn to set up your Java development environment. Install Java and Eclipse IDE, explore Eclipse features, and create your first program in IntelliJ.',
                'learning_objectives': 'Install Java and Eclipse IDE\nSet up development environment\nLearn Eclipse installation and hello world program in IntelliJ\nExplore Eclipse features\nUnderstand IDE capabilities',
                'topics': 'Java and Eclipse IDE installation\nEclipse installation & hello world program in IntelliJ\nEclipse features',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Operators in Java',
                'summary': 'Master Java operators including arithmetic, decision-making operators, ternary operator, assignment operators, and if-else statements.',
                'learning_objectives': 'Understand arithmetic operators\nMake decisions with operators\nUse ternary operator\nApply assignment operators\nImplement if-else statements for decision making',
                'topics': 'Arithmetic operators\nMaking decisions with operators\nTernary operator\nAssignment operators\nMaking decisions with if-else',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Flow Control',
                'summary': 'Control program flow using switch case, loops (for, while, do-while), break and continue statements, nested loops, and modulo operator.',
                'learning_objectives': 'Use switch case statements\nImplement for, while, and do-while loops\nUnderstand break and continue statements\nWork with nested loops\nApply modulo operator\nSolve problems like sum of digits',
                'topics': 'Switch case\nFor loop\nWhile loop\nDo-while loop\nLoops revisited\nBreak and continue\nNested loops\nNested loops – exercise\nModulo operator\nSum of digit solution',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Methods in Java',
                'summary': 'Learn to create and use methods in Java. Understand method parameters, return types, and method overloading.',
                'learning_objectives': 'Create and call methods\nUnderstand method parameters and return types\nImplement method overloading\nWrite reusable code with methods',
                'topics': 'Methods\nMethods parameters and return types\nMethod overloading',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Good Coding Information',
                'summary': 'Learn Java coding best practices including code blocks, indentation, statements, and Java literals.',
                'learning_objectives': 'Understand code blocks and indentation\nLearn about Java statements\nMaster Java literals\nFollow coding best practices',
                'topics': 'Code Block, Indentation and statements\nJava literals',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Object-Oriented Programming Concepts',
                'summary': 'Dive deep into OOP concepts including classes, getters/setters, constructors, inheritance, composition, encapsulation, and polymorphism.',
                'learning_objectives': 'Create classes and objects\nImplement getters and setters\nUnderstand constructors (default and parameterized)\nMaster inheritance concepts\nLearn composition\nApply encapsulation\nUnderstand benefits of polymorphism',
                'topics': 'Classes – Introduction\nClasses – Getters and Setters introduction\nClasses – Getters and Setters\nClasses – Adding functionality\nConstructors – Introduction\nDefault constructor\nUsage of constructors\nUnderstanding inheritance\nWorking with inheritance\nTypes of inheritance – Exercise information\nComposition – Introduction\nComposition – Setting up\nWorking with composition\nAdding functionality\nEncapsulation\nBenefits of Polymorphism',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Core Java Concepts',
                'summary': 'Explore advanced Java concepts including interfaces, abstract classes, inner classes, static elements, final keyword, packages, scope, access modifiers, exception handling, and strings.',
                'learning_objectives': 'Understand interfaces and abstract classes\nLearn about inner classes and nested classes\nMaster static elements\nApply final keyword\nWork with packages\nUnderstand scope and access modifiers\nHandle exceptions effectively\nMaster string operations',
                'topics': 'Interfaces\nAbstract class – Introduction\nMultiple inheritance using interfaces\nInner classes\nTypes of nested class\nLocal inner class\nAnonymous object\nAnonymous inner class\nAdvantages of inner class\nUser input\nStatic elements\nStatic inner class\nFinal keyword\nFinal keyword with method and class\nPackages\nPackages continues\nScope\nAccess modifier\nException handling (Intro)\nException handling, multiple catch blocks\nFinally block\nThrow and throws\nUser defined exception\nChecked and unchecked exceptions\nStrings\nDifference between String literal and String Object\nString methods\nString formatting',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Arrays',
                'summary': 'Work with arrays in Java. Learn array initialization, foreach loop, call by value and reference, and understand array limitations.',
                'learning_objectives': 'Understand array overview\nInitialize arrays properly\nUse foreach loop\nUnderstand call by value and reference\nRecognize issues with arrays',
                'topics': 'Array overview\nHow to initialize array\nForeach loop\nMethods – Call by value and reference\nIssues with array',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Collections Framework',
                'summary': 'Master Java Collections Framework including ArrayList, autoboxing/unboxing, Stack, LinkedList, iterators, sorting, and Comparable interface.',
                'learning_objectives': 'Understand Collections Framework overview\nWork with ArrayList\nUnderstand autoboxing and unboxing\nUse Stack and LinkedList\nApply iterators\nSort and reverse elements\nImplement Comparable interface',
                'topics': 'Collections framework overview\nArrayList\nAutoboxing and unboxing\nArrayList and Stack overview\nStack methods\nLinkedList\nLinkedList operations\nIterators\nSorting and reversal of elements\nCompareTo method overview\nComparable interface',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'Generics',
                'summary': 'Learn Java Generics including type parameters, generic methods, bounded type parameters, wildcards, and Comparable interface with generics.',
                'learning_objectives': 'Understand generics overview\nUse type parameters\nCreate generic methods\nApply bounded type parameters\nUse wildcards in generics\nWork with Comparable interface and generics',
                'topics': 'Generics overview\nGetting started with generics\nUnderstanding generics\nType parameters\nGeneric method\nBounded type parameter\nComparable interface\nWildcards in Generics',
                'questions': self.get_module11_questions(),
            },
            {
                'order': 12,
                'title': 'Collections – Advanced',
                'summary': 'Explore advanced collections including Sets, custom sorting with Comparator, Queue, Dequeue, Maps, TreeMap, equals and hashCode methods.',
                'learning_objectives': 'Work with Sets and Set types\nImplement custom sorting using Comparator\nUse Queue and Dequeue\nMaster Maps and TreeMap\nUnderstand equals and hashCode methods\nSearch under Maps',
                'topics': 'Sets\nSet types\nCustom sorting using comparator\nQueue\nDequeue\nMaps\nTreeMap\nEquals and hashcode methods\nSearch under Maps',
                'questions': self.get_module12_questions(),
            },
            {
                'order': 13,
                'title': 'Lambda Overview',
                'summary': 'Master Lambda expressions in Java. Learn lambda syntax, predicates, and use lambdas with variables and iterations.',
                'learning_objectives': 'Understand lambda expression overview\nCreate lambda expressions\nUse lambda expressions with variables and iterations\nWork with Predicates\nApply functional programming concepts',
                'topics': 'Lambda expression overview\nLambda expression continued\nLambda expressions – something more\nLambda expressions – few more things\nLambda expressions with variables and iterations\nPredicates',
                'questions': self.get_module13_questions(),
            },
            {
                'order': 14,
                'title': 'File Handling in Java',
                'summary': 'Learn file operations in Java including data streams, creating files and directories, reading/writing files, serialization, and try-with-resources.',
                'learning_objectives': 'Understand data streams\nCreate files and directories\nWrite onto files\nRead files with BufferedReader and Scanner\nCompare Scanner vs BufferedReader\nDelete files\nUse try-with-resources\nSerialize and deserialize objects',
                'topics': 'Data streams\nCreating file on disk\nCreating a directory\nWriting onto files\nReading files with BufferedReader\nReading files with Scanner\nScanner vs BufferedReader\nFile deletion\nTry with resources\nSerialization of objects',
                'questions': self.get_module14_questions(),
            },
            {
                'order': 15,
                'title': 'Debugging',
                'summary': 'Learn debugging techniques in Java. Get started with debugging, update runtime variable values, and master debugging tools.',
                'learning_objectives': 'Get started with debugging\nUpdate runtime variable values during debugging\nMaster debugging techniques\nUse debugging tools effectively',
                'topics': 'Getting started with debugging\nDebugging, runtime variable value update\nDebugging continues',
                'questions': self.get_module15_questions(),
            },
            {
                'order': 16,
                'title': 'Git Basics',
                'summary': 'Learn Git version control basics. Understand Git overview, features, setup, and how to clone and import Git projects into Eclipse.',
                'learning_objectives': 'Understand Git overview and features\nSet up Git\nClone and import Git project into Eclipse\nClone Git project directly from Eclipse\nUse version control effectively',
                'topics': 'Before we go further\nGit overview\nGit features overview\nSetting up Git\nClone and import Git project into Eclipse\nClone Git project directly from Eclipse',
                'questions': self.get_module16_questions(),
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
                'question': 'What does JVM stand for?',
                'options': [
                    'Java Virtual Machine',
                    'Java Variable Machine',
                    'Java Version Manager',
                    'Java Visual Machine'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is a primitive data type in Java?',
                'options': [
                    'String',
                    'int',
                    'Array',
                    'Object'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default value of a boolean variable in Java?',
                'options': [
                    'true',
                    'false',
                    'null',
                    '0'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which class is used for precise decimal calculations?',
                'options': [
                    'Double',
                    'Float',
                    'BigDecimal',
                    'Decimal'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the correct syntax for the main method in Java?',
                'options': [
                    'public static void main(String[] args)',
                    'public void main(String[] args)',
                    'static void main(String[] args)',
                    'public static main(String[] args)'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions
    def get_module2_questions(self):
        return [
            {
                'question': 'Which IDE is commonly used for Java development?',
                'options': [
                    'Eclipse',
                    'Visual Studio',
                    'Xcode',
                    'All of the above'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does IDE stand for?',
                'options': [
                    'Integrated Development Environment',
                    'Internal Development Engine',
                    'Interactive Development Editor',
                    'Integrated Design Environment'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tool is used to compile Java source code?',
                'options': [
                    'javac',
                    'java',
                    'javadoc',
                    'jar'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions
    def get_module3_questions(self):
        return [
            {
                'question': 'Which operator is used for modulo operation?',
                'options': [
                    '%',
                    '/',
                    '*',
                    '&'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the ternary operator syntax?',
                'options': [
                    'condition ? value1 : value2',
                    'condition : value1 ? value2',
                    'value1 ? condition : value2',
                    'condition ? value1, value2'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which operator has the highest precedence?',
                'options': [
                    '+',
                    '*',
                    '()',
                    '='
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the result of: int x = 5; x++; System.out.println(x);',
                'options': [
                    '5',
                    '6',
                    '4',
                    'Error'
                ],
                'correct_answer': 2
            },
        ]

    # Module 4 Questions
    def get_module4_questions(self):
        return [
            {
                'question': 'Which statement is used to exit a loop prematurely?',
                'options': [
                    'exit',
                    'break',
                    'continue',
                    'return'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output of: for(int i=0; i<3; i++) { System.out.print(i); }',
                'options': [
                    '012',
                    '123',
                    '0123',
                    '321'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which loop executes at least once?',
                'options': [
                    'for loop',
                    'while loop',
                    'do-while loop',
                    'All of the above'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does the continue statement do?',
                'options': [
                    'Exits the loop',
                    'Skips the current iteration',
                    'Restarts the loop',
                    'Pauses execution'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does the modulo operator (%) return?',
                'options': [
                    'Quotient',
                    'Remainder',
                    'Product',
                    'Difference'
                ],
                'correct_answer': 2
            },
        ]

    # Module 5 Questions
    def get_module5_questions(self):
        return [
            {
                'question': 'What is method overloading?',
                'options': [
                    'Having multiple methods with the same name but different parameters',
                    'Having a method that calls itself',
                    'Having a method that overrides a parent method',
                    'Having a method with multiple return types'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Can a method have multiple return types in Java?',
                'options': [
                    'Yes',
                    'No',
                    'Only in abstract classes',
                    'Only in interfaces'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What keyword is used to return a value from a method?',
                'options': [
                    'return',
                    'exit',
                    'break',
                    'continue'
                ],
                'correct_answer': 1
            },
        ]

    # Module 6 Questions
    def get_module6_questions(self):
        return [
            {
                'question': 'What is a code block in Java?',
                'options': [
                    'A group of statements enclosed in braces {}',
                    'A single statement',
                    'A comment',
                    'A variable declaration'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is a Java literal?',
                'options': [
                    'int x = 5;',
                    '5',
                    'x',
                    'int'
                ],
                'correct_answer': 2
            },
        ]

    # Module 7 Questions
    def get_module7_questions(self):
        return [
            {
                'question': 'What is a constructor?',
                'options': [
                    'A method that returns a value',
                    'A special method to initialize objects',
                    'A variable in a class',
                    'A static method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which keyword is used for inheritance in Java?',
                'options': [
                    'inherits',
                    'extends',
                    'implements',
                    'super'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is encapsulation?',
                'options': [
                    'Hiding implementation details',
                    'Inheriting from a parent class',
                    'Creating multiple objects',
                    'Using static methods'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of getters and setters?',
                'options': [
                    'To access and modify private fields',
                    'To create objects',
                    'To inherit from classes',
                    'To handle exceptions'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is composition?',
                'options': [
                    'Inheritance relationship',
                    'HAS-A relationship',
                    'IS-A relationship',
                    'Polymorphism'
                ],
                'correct_answer': 2
            },
        ]

    # Module 8 Questions
    def get_module8_questions(self):
        return [
            {
                'question': 'Which keyword is used to implement an interface?',
                'options': [
                    'extends',
                    'implements',
                    'inherits',
                    'uses'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the parent class of all exceptions?',
                'options': [
                    'Error',
                    'RuntimeException',
                    'Throwable',
                    'Exception'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What does the final keyword do when applied to a class?',
                'options': [
                    'Makes it static',
                    'Prevents it from being extended',
                    'Makes it private',
                    'Makes it abstract'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between String literal and String Object?',
                'options': [
                    'String literal is stored in string pool, String Object is in heap',
                    'There is no difference',
                    'String literal is mutable, String Object is immutable',
                    'String literal cannot be created'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a static method?',
                'options': [
                    'A method that belongs to an instance',
                    'A method that belongs to the class',
                    'A method that cannot be overridden',
                    'A method that is final'
                ],
                'correct_answer': 2
            },
        ]

    # Module 9 Questions
    def get_module9_questions(self):
        return [
            {
                'question': 'How do you get the length of an array in Java?',
                'options': [
                    'array.length()',
                    'array.length',
                    'array.size()',
                    'array.size'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the index of the first element in an array?',
                'options': [
                    '0',
                    '1',
                    '-1',
                    'Depends on the array'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the enhanced for loop also known as?',
                'options': [
                    'for-each loop',
                    'while loop',
                    'do-while loop',
                    'traditional for loop'
                ],
                'correct_answer': 1
            },
            {
                'question': 'In Java, are primitive types passed by value or reference?',
                'options': [
                    'By value',
                    'By reference',
                    'Both',
                    'Neither'
                ],
                'correct_answer': 1
            },
        ]

    # Module 10 Questions
    def get_module10_questions(self):
        return [
            {
                'question': 'Which interface does ArrayList implement?',
                'options': [
                    'Set',
                    'List',
                    'Map',
                    'Queue'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is autoboxing?',
                'options': [
                    'Converting primitive to wrapper object automatically',
                    'Converting wrapper object to primitive automatically',
                    'Creating a box',
                    'Wrapping code'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between ArrayList and LinkedList?',
                'options': [
                    'ArrayList is faster for insertion, LinkedList for access',
                    'LinkedList is faster for insertion, ArrayList for access',
                    'They are the same',
                    'ArrayList cannot store objects'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of an Iterator?',
                'options': [
                    'To create collections',
                    'To iterate over collection elements',
                    'To sort collections',
                    'To filter collections'
                ],
                'correct_answer': 2
            },
        ]

    # Module 11 Questions
    def get_module11_questions(self):
        return [
            {
                'question': 'What is generics in Java?',
                'options': [
                    'A way to create generic classes',
                    'Type-safe collections',
                    'A programming language',
                    'A design pattern'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the syntax for creating a generic ArrayList?',
                'options': [
                    'ArrayList<> list = new ArrayList<>();',
                    'ArrayList list = new ArrayList();',
                    'ArrayList<String> list = new ArrayList<String>();',
                    'Both A and C'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What are wildcards in generics?',
                'options': [
                    '? symbol used to represent unknown type',
                    'A type parameter',
                    'A method',
                    'A class'
                ],
                'correct_answer': 1
            },
        ]

    # Module 12 Questions
    def get_module12_questions(self):
        return [
            {
                'question': 'Which collection does not allow duplicate elements?',
                'options': [
                    'List',
                    'Set',
                    'Map',
                    'Queue'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between HashSet and TreeSet?',
                'options': [
                    'HashSet is sorted, TreeSet is not',
                    'TreeSet is sorted, HashSet is not',
                    'They are the same',
                    'HashSet allows null, TreeSet does not'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which interface does HashMap implement?',
                'options': [
                    'List',
                    'Set',
                    'Map',
                    'Collection'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between Comparable and Comparator?',
                'options': [
                    'Comparable is in java.util, Comparator is in java.lang',
                    'Comparable defines natural ordering, Comparator defines custom ordering',
                    'They are the same',
                    'Comparable is for primitives, Comparator for objects'
                ],
                'correct_answer': 2
            },
        ]

    # Module 13 Questions
    def get_module13_questions(self):
        return [
            {
                'question': 'What is a lambda expression?',
                'options': [
                    'An anonymous function',
                    'A named function',
                    'A class',
                    'A variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the syntax for a lambda expression?',
                'options': [
                    '(parameters) -> expression',
                    'parameters -> expression',
                    '(parameters) => expression',
                    'lambda parameters: expression'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a Predicate in Java?',
                'options': [
                    'A functional interface that takes one argument and returns boolean',
                    'A class',
                    'A method',
                    'A variable'
                ],
                'correct_answer': 1
            },
        ]

    # Module 14 Questions
    def get_module14_questions(self):
        return [
            {
                'question': 'Which class is used to read characters from a file?',
                'options': [
                    'FileInputStream',
                    'FileReader',
                    'FileWriter',
                    'BufferedReader'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which class provides buffered reading?',
                'options': [
                    'FileReader',
                    'BufferedReader',
                    'FileInputStream',
                    'Reader'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is serialization in Java?',
                'options': [
                    'Converting object to byte stream',
                    'Converting byte stream to object',
                    'Reading from file',
                    'Writing to file'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which interface must be implemented for serialization?',
                'options': [
                    'Serializable',
                    'Cloneable',
                    'Comparable',
                    'Runnable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is try-with-resources?',
                'options': [
                    'A way to automatically close resources',
                    'A way to handle exceptions',
                    'A way to create files',
                    'A way to delete files'
                ],
                'correct_answer': 1
            },
        ]

    # Module 15 Questions
    def get_module15_questions(self):
        return [
            {
                'question': 'What is debugging?',
                'options': [
                    'Finding and fixing errors in code',
                    'Writing code',
                    'Compiling code',
                    'Running code'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a breakpoint?',
                'options': [
                    'A point where program execution pauses',
                    'A compilation error',
                    'A runtime error',
                    'A syntax error'
                ],
                'correct_answer': 1
            },
        ]

    # Module 16 Questions
    def get_module16_questions(self):
        return [
            {
                'question': 'What is Git?',
                'options': [
                    'A version control system',
                    'A programming language',
                    'An IDE',
                    'A database'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command is used to clone a Git repository?',
                'options': [
                    'git clone',
                    'git copy',
                    'git download',
                    'git get'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a repository in Git?',
                'options': [
                    'A storage location for your project',
                    'A file',
                    'A folder',
                    'A program'
                ],
                'correct_answer': 1
            },
        ]
