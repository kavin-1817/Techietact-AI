"""
Management command to seed Core Java course with modules and quizzes
Run with: python manage.py seed_java_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Core Java course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Core Java course
        course, created = Course.objects.get_or_create(
            title='Core Java Programming',
            defaults={
                'description': 'Master the fundamentals of Java programming language. Learn object-oriented programming, data structures, exception handling, and more. This comprehensive course covers everything from basic syntax to advanced concepts.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Core Java course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data with questions"""
        return [
            {
                'order': 1,
                'title': 'Introduction to Java',
                'summary': 'Get started with Java programming. Learn about Java history, platform independence, JVM, JDK, JRE, and write your first Java program.',
                'learning_objectives': 'Understand Java platform and architecture\nInstall and configure Java development environment\nWrite and compile your first Java program\nUnderstand Java naming conventions and coding standards',
                'topics': 'Java History and Features\nJava Virtual Machine (JVM)\nJDK vs JRE vs JVM\nSetting up Development Environment\nHello World Program\nJava Naming Conventions',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Java Fundamentals: Variables, Data Types, and Operators',
                'summary': 'Master the building blocks of Java programming. Learn about primitive data types, variables, constants, type conversion, and various operators.',
                'learning_objectives': 'Understand Java primitive and reference data types\nDeclare and initialize variables\nPerform type casting and conversion\nUse arithmetic, relational, logical, and bitwise operators',
                'topics': 'Primitive Data Types (byte, short, int, long, float, double, char, boolean)\nReference Data Types\nVariables and Constants\nType Conversion and Casting\nArithmetic Operators\nRelational and Logical Operators\nBitwise Operators\nOperator Precedence',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Control Flow: Conditionals and Loops',
                'summary': 'Learn to control program flow using conditional statements and loops. Master if-else, switch, for, while, and do-while constructs.',
                'learning_objectives': 'Use if-else and switch statements for decision making\nImplement for, while, and do-while loops\nUnderstand break and continue statements\nHandle nested control structures',
                'topics': 'If-else Statements\nSwitch Statements\nTernary Operator\nFor Loop\nWhile Loop\nDo-while Loop\nBreak and Continue Statements\nNested Loops',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Arrays and Strings',
                'summary': 'Work with arrays and strings in Java. Learn array declaration, initialization, manipulation, and string operations.',
                'learning_objectives': 'Declare and initialize arrays\nAccess and modify array elements\nUnderstand multi-dimensional arrays\nPerform string operations and manipulations',
                'topics': 'Array Declaration and Initialization\nArray Access and Modification\nMulti-dimensional Arrays\nString Class and Methods\nStringBuilder and StringBuffer\nString Comparison and Manipulation',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Object-Oriented Programming: Classes and Objects',
                'summary': 'Dive into object-oriented programming. Learn to create classes, instantiate objects, understand constructors, methods, and access modifiers.',
                'learning_objectives': 'Create classes and objects\nUnderstand constructors and method overloading\nUse access modifiers (public, private, protected)\nImplement getters, setters, and encapsulation',
                'topics': 'Classes and Objects\nConstructors (Default, Parameterized, Copy)\nMethod Overloading\nAccess Modifiers\nEncapsulation\nGetters and Setters\nStatic Members\nInstance vs Class Members',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Inheritance and Polymorphism',
                'summary': 'Explore inheritance, method overriding, and polymorphism. Understand the IS-A relationship, super keyword, and dynamic method dispatch.',
                'learning_objectives': 'Implement inheritance using extends keyword\nOverride methods in subclasses\nUnderstand polymorphism and dynamic binding\nUse super keyword effectively',
                'topics': 'Inheritance Concept\nMethod Overriding\nSuper Keyword\nPolymorphism\nDynamic Method Dispatch\nRuntime Polymorphism\nAbstract Classes\nFinal Keyword',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Interfaces and Abstract Classes',
                'summary': 'Learn about interfaces, abstract classes, and their differences. Understand when to use interfaces vs abstract classes.',
                'learning_objectives': 'Define and implement interfaces\nUnderstand abstract classes\nKnow the difference between interfaces and abstract classes\nImplement multiple inheritance using interfaces',
                'topics': 'Interface Declaration and Implementation\nDefault and Static Methods in Interfaces\nAbstract Classes\nAbstract Methods\nInterface vs Abstract Class\nMultiple Inheritance through Interfaces\nFunctional Interfaces',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Exception Handling',
                'summary': 'Master exception handling in Java. Learn about checked and unchecked exceptions, try-catch blocks, and custom exceptions.',
                'learning_objectives': 'Understand exception hierarchy\nHandle exceptions using try-catch-finally\nThrow and declare exceptions\nCreate custom exception classes',
                'topics': 'Exception Types (Checked, Unchecked, Error)\nTry-Catch-Finally Blocks\nThrow and Throws Keywords\nCustom Exceptions\nException Propagation\nBest Practices for Exception Handling',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Collections Framework',
                'summary': 'Work with Java Collections Framework. Learn about List, Set, Map interfaces and their implementations like ArrayList, HashSet, HashMap.',
                'learning_objectives': 'Understand Collections Framework hierarchy\nUse List, Set, and Map interfaces\nChoose appropriate collection types\nIterate over collections using iterators',
                'topics': 'Collections Framework Overview\nList Interface (ArrayList, LinkedList)\nSet Interface (HashSet, TreeSet)\nMap Interface (HashMap, TreeMap)\nIterator and ListIterator\nComparable and Comparator\nGenerics in Collections',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'File I/O and Streams',
                'summary': 'Learn file operations and I/O streams in Java. Read from and write to files using various stream classes.',
                'learning_objectives': 'Read and write files using FileReader/FileWriter\nUse BufferedReader and BufferedWriter\nWork with FileInputStream and FileOutputStream\nHandle file operations and exceptions',
                'topics': 'File Class\nFileReader and FileWriter\nBufferedReader and BufferedWriter\nFileInputStream and FileOutputStream\nByte Streams vs Character Streams\nNIO (New I/O) Package\nSerialization and Deserialization',
                'questions': self.get_module10_questions(),
            },
            {
                'order': 11,
                'title': 'Java Mini Project Workshop',
                'summary': 'Practice building focused Java mini projects that turn fresh concepts into working demos.',
                'learning_objectives': (
                    'Convert requirements into concise project briefs with Java-centric constraints\n'
                    'Choose between CLI, Spring Boot, or JavaFX for the fastest validation path\n'
                    'Instrument projects with tests, Checkstyle, and retrospectives'
                ),
                'topics': (
                    'Requirement cards & swimlanes\n'
                    'Choosing build tools (Maven vs Gradle)\n'
                    'JUnit + JaCoCo feedback loops\n'
                    'Lightweight retros and demo scripts'
                ),
                'questions': self.get_module11_questions(),
            },
            {
                'order': 12,
                'title': 'Java End-to-End Delivery Systems',
                'summary': 'Design production-grade Java services spanning REST APIs, messaging, persistence, and deployment pipelines.',
                'learning_objectives': (
                    'Model Spring Boot services with persistence, caching, and messaging\n'
                    'Apply layered testing (unit, integration, contract) plus static analysis\n'
                    'Automate delivery via Maven/Gradle builds, Docker images, and CI/CD gates'
                ),
                'topics': (
                    'Hexagonal architecture + DTO mapping\n'
                    'Spring Data JPA, Flyway, and Redis caching\n'
                    'Kafka/RabbitMQ message flows\n'
                    'GitHub Actions/Jenkins pipelines with Sonar and smoke tests'
                ),
                'questions': self.get_module12_questions(),
            },
            {
                'order': 13,
                'title': 'Java Interview Accelerator',
                'summary': 'Tailor your interview prep to the Java ecosystem across algorithms, system design, and behavioral loops.',
                'learning_objectives': (
                    'Solve DSA prompts using Java collections and concurrency primitives\n'
                    'Explain JVM tuning, microservice design, and scaling trade-offs\n'
                    'Craft STAR stories highlighting ownership, refactors, and on-call wins'
                ),
                'topics': (
                    'PriorityQueue, Deque, and Stream API patterns\n'
                    'JVM memory model, GC tuning, profiling\n'
                    'System design templates (payment, messaging, analytics)\n'
                    'Behavioral frameworks, negotiation, and follow-ups'
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
                'question': 'Which of the following is NOT a feature of Java?',
                'options': [
                    'Platform Independent',
                    'Object-Oriented',
                    'Compiled and Interpreted',
                    'Single Inheritance Only'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the extension of a Java source file?',
                'options': [
                    '.java',
                    '.class',
                    '.jar',
                    '.exe'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the entry point of a Java application?',
                'options': [
                    'main() method',
                    'start() method',
                    'run() method',
                    'init() method'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which command is used to compile a Java program?',
                'options': [
                    'javac',
                    'java',
                    'javadoc',
                    'jar'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does JDK stand for?',
                'options': [
                    'Java Development Kit',
                    'Java Deployment Kit',
                    'Java Debugging Kit',
                    'Java Design Kit'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is a valid Java identifier?',
                'options': [
                    '2variable',
                    '_variable',
                    'variable-name',
                    'variable name'
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
                'question': 'Which keyword is used to define a class in Java?',
                'options': [
                    'class',
                    'Class',
                    'CLASS',
                    'define'
                ],
                'correct_answer': 1
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
                'question': 'What is the size of an int in Java?',
                'options': [
                    '16 bits',
                    '32 bits',
                    '64 bits',
                    '8 bits'
                ],
                'correct_answer': 2
            },
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
                'question': 'What is the result of 5 / 2 in Java?',
                'options': [
                    '2.5',
                    '2',
                    '3',
                    '2.0'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which of the following is a valid way to declare a constant in Java?',
                'options': [
                    'const int VALUE = 10;',
                    'final int VALUE = 10;',
                    'static int VALUE = 10;',
                    'constant int VALUE = 10;'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default value of an int variable in Java?',
                'options': [
                    '0',
                    'null',
                    'undefined',
                    '-1'
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
            {
                'question': 'Which of the following is NOT a valid primitive data type?',
                'options': [
                    'byte',
                    'short',
                    'long',
                    'string'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the == operator compare for primitive types?',
                'options': [
                    'References',
                    'Values',
                    'Memory addresses',
                    'Types'
                ],
                'correct_answer': 2
            },
        ]

    # Module 3 Questions
    def get_module3_questions(self):
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
                'question': 'Which of the following is a valid switch case statement?',
                'options': [
                    'switch (x) { case 1: break; }',
                    'switch x { case 1: break; }',
                    'switch (x) { 1: break; }',
                    'switch (x) { case 1; break; }'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the result of: int x = 10; if(x > 5 && x < 15) System.out.println("Yes");',
                'options': [
                    'Yes',
                    'No output',
                    'Compilation error',
                    'Runtime error'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which operator is used for logical AND?',
                'options': [
                    '&',
                    '&&',
                    '|',
                    '||'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output: int i = 0; while(i < 3) { i++; } System.out.println(i);',
                'options': [
                    '0',
                    '3',
                    '2',
                    '4'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which statement is optional in a for loop?',
                'options': [
                    'Initialization',
                    'Condition',
                    'Increment',
                    'All are optional'
                ],
                'correct_answer': 4
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
        ]

    # Module 4 Questions
    def get_module4_questions(self):
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
                'question': 'Which of the following is a valid array declaration?',
                'options': [
                    'int[] arr = new int[5];',
                    'int arr[] = new int[5];',
                    'int[] arr = new int(5);',
                    'Both A and B'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the default value of an array element of type int?',
                'options': [
                    '0',
                    'null',
                    'undefined',
                    '-1'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which method is used to compare two strings in Java?',
                'options': [
                    'compare()',
                    'equals()',
                    'compareTo()',
                    'Both B and C'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the result of: String s = "Hello"; s.length();',
                'options': [
                    '4',
                    '5',
                    'Compilation error',
                    'Runtime error'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which class is mutable (can be modified)?',
                'options': [
                    'String',
                    'StringBuilder',
                    'Both',
                    'Neither'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the output: String s1 = "Java"; String s2 = "Java"; System.out.println(s1 == s2);',
                'options': [
                    'true',
                    'false',
                    'Compilation error',
                    'null'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you create a 2D array in Java?',
                'options': [
                    'int[][] arr = new int[3][4];',
                    'int arr[][] = new int[3][4];',
                    'int[] arr[] = new int[3][4];',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which method converts a string to uppercase?',
                'options': [
                    'toUpperCase()',
                    'upperCase()',
                    'toUpper()',
                    'upper()'
                ],
                'correct_answer': 1
            },
        ]

    # Module 5 Questions
    def get_module5_questions(self):
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
                'question': 'What is the default access modifier for a class member in Java?',
                'options': [
                    'public',
                    'private',
                    'protected',
                    'package-private'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which keyword is used to refer to the current object?',
                'options': [
                    'this',
                    'super',
                    'self',
                    'current'
                ],
                'correct_answer': 1
            },
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
                'question': 'Which access modifier allows access from anywhere?',
                'options': [
                    'private',
                    'protected',
                    'public',
                    'default'
                ],
                'correct_answer': 3
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
                'question': 'Can a constructor be private?',
                'options': [
                    'No, never',
                    'Yes, it can be',
                    'Only in abstract classes',
                    'Only in interfaces'
                ],
                'correct_answer': 2
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
                'question': 'Which of the following is true about constructors?',
                'options': [
                    'They have a return type',
                    'They have the same name as the class',
                    'They are called explicitly',
                    'They cannot be overloaded'
                ],
                'correct_answer': 2
            },
        ]

    # Module 6 Questions
    def get_module6_questions(self):
        return [
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
                'question': 'What is method overriding?',
                'options': [
                    'Having multiple methods with the same name',
                    'Redefining a method in a subclass',
                    'Calling a method multiple times',
                    'Hiding a method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is polymorphism?',
                'options': [
                    'Having multiple forms',
                    'Having multiple classes',
                    'Having multiple methods',
                    'Having multiple variables'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which keyword is used to call the parent class constructor?',
                'options': [
                    'this',
                    'super',
                    'parent',
                    'base'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is dynamic method dispatch?',
                'options': [
                    'Compile-time method resolution',
                    'Runtime method resolution',
                    'Static method calling',
                    'Method overloading'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Can a class extend multiple classes in Java?',
                'options': [
                    'Yes',
                    'No',
                    'Only abstract classes',
                    'Only interfaces'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the IS-A relationship?',
                'options': [
                    'Composition',
                    'Inheritance',
                    'Aggregation',
                    'Association'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does the final keyword do when applied to a method?',
                'options': [
                    'Makes it static',
                    'Prevents it from being overridden',
                    'Makes it private',
                    'Makes it abstract'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is an abstract class?',
                'options': [
                    'A class that cannot be instantiated',
                    'A class with only abstract methods',
                    'A class that must be extended',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the output of: Parent p = new Child(); p.method(); (assuming method is overridden)',
                'options': [
                    'Parent method is called',
                    'Child method is called',
                    'Compilation error',
                    'Runtime error'
                ],
                'correct_answer': 2
            },
        ]

    # Module 7 Questions
    def get_module7_questions(self):
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
                'question': 'Can an interface have instance variables?',
                'options': [
                    'Yes, any type',
                    'No, never',
                    'Yes, but only public static final',
                    'Yes, but only private'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between an interface and an abstract class?',
                'options': [
                    'Interfaces can have constructors, abstract classes cannot',
                    'Abstract classes can have constructors, interfaces cannot',
                    'Both can have constructors',
                    'Neither can have constructors'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Can a class implement multiple interfaces?',
                'options': [
                    'No',
                    'Yes',
                    'Only two',
                    'Only if they are related'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a functional interface?',
                'options': [
                    'An interface with multiple methods',
                    'An interface with exactly one abstract method',
                    'An interface with no methods',
                    'An abstract class'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which of the following is true about abstract classes?',
                'options': [
                    'They can be instantiated',
                    'They can have both abstract and concrete methods',
                    'They cannot have constructors',
                    'They cannot be extended'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default access modifier for interface methods?',
                'options': [
                    'private',
                    'protected',
                    'public',
                    'package-private'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Can an interface extend another interface?',
                'options': [
                    'No',
                    'Yes',
                    'Only one',
                    'Only abstract interfaces'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of default methods in interfaces?',
                'options': [
                    'To provide default implementation',
                    'To make methods optional',
                    'To prevent overriding',
                    'To create static methods'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following can have method bodies?',
                'options': [
                    'Abstract classes only',
                    'Interfaces only',
                    'Both abstract classes and interfaces (Java 8+)',
                    'Neither'
                ],
                'correct_answer': 3
            },
        ]

    # Module 8 Questions
    def get_module8_questions(self):
        return [
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
                'question': 'Which exceptions are checked exceptions?',
                'options': [
                    'RuntimeException and its subclasses',
                    'Error and its subclasses',
                    'Exception and its subclasses (except RuntimeException)',
                    'All exceptions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of the finally block?',
                'options': [
                    'To handle exceptions',
                    'To catch exceptions',
                    'To execute code regardless of exceptions',
                    'To throw exceptions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which keyword is used to throw an exception?',
                'options': [
                    'throws',
                    'throw',
                    'catch',
                    'try'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between throw and throws?',
                'options': [
                    'throw is used in method signature, throws is used in method body',
                    'throws is used in method signature, throw is used in method body',
                    'They are the same',
                    'throw is for checked, throws is for unchecked'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Can a try block exist without catch or finally?',
                'options': [
                    'Yes',
                    'No',
                    'Only in Java 7+',
                    'Only for unchecked exceptions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What happens if an exception is not caught?',
                'options': [
                    'The program continues normally',
                    'The program terminates',
                    'The exception is ignored',
                    'The exception is logged automatically'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which of the following is an unchecked exception?',
                'options': [
                    'IOException',
                    'SQLException',
                    'NullPointerException',
                    'FileNotFoundException'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you create a custom exception?',
                'options': [
                    'Extend Exception class',
                    'Extend RuntimeException class',
                    'Extend Throwable class',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is exception propagation?',
                'options': [
                    'Creating new exceptions',
                    'Exceptions moving up the call stack',
                    'Catching exceptions',
                    'Handling exceptions'
                ],
                'correct_answer': 2
            },
        ]

    # Module 9 Questions
    def get_module9_questions(self):
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
                'question': 'What is the purpose of an Iterator?',
                'options': [
                    'To create collections',
                    'To iterate over collection elements',
                    'To sort collections',
                    'To filter collections'
                ],
                'correct_answer': 2
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
            {
                'question': 'Which method is used to add an element to a List?',
                'options': [
                    'add()',
                    'put()',
                    'insert()',
                    'append()'
                ],
                'correct_answer': 1
            },
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
        ]

    # Module 10 Questions
    def get_module10_questions(self):
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
                'question': 'What is the difference between FileReader and FileInputStream?',
                'options': [
                    'FileReader reads bytes, FileInputStream reads characters',
                    'FileReader reads characters, FileInputStream reads bytes',
                    'They are the same',
                    'FileReader is for writing, FileInputStream for reading'
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
                'question': 'What is the purpose of the File class?',
                'options': [
                    'To read file contents',
                    'To write file contents',
                    'To represent file and directory paths',
                    'To delete files only'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which method is used to check if a file exists?',
                'options': [
                    'exists()',
                    'isFile()',
                    'isDirectory()',
                    'canRead()'
                ],
                'correct_answer': 1
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
                'question': 'What is the NIO package used for?',
                'options': [
                    'Network I/O',
                    'New I/O with better performance',
                    'Non-blocking I/O',
                    'All of the above'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which class is used to write characters to a file?',
                'options': [
                    'FileReader',
                    'FileWriter',
                    'FileInputStream',
                    'FileOutputStream'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What should you always do after file operations?',
                'options': [
                    'Nothing, Java handles it',
                    'Close the stream',
                    'Delete the file',
                    'Rename the file'
                ],
                'correct_answer': 2
            },
        ]

    # Module 11 Questions
    def get_module11_questions(self):
        return [
            {
                'question': 'Which document anchors scope for a Java mini project?',
                'options': [
                    'IDE workspace settings',
                    'A project brief outlining acceptance criteria and risks',
                    'The compiled JAR file',
                    'A screenshot of the console'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Why choose Gradle or Maven explicitly at project kickoff?',
                'options': [
                    'It determines the UI framework',
                    'It governs dependency management, plugins, and CI commands',
                    'It changes JVM bytecode',
                    'It replaces Git'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What ensures quick feedback when iterating on a Spring Boot mini service?',
                'options': [
                    'Running mvn test or ./gradlew test with JUnit each commit',
                    'Waiting for staging deploys',
                    'Rebuilding the IDE index',
                    'Rebasing main hourly'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which tool enforces style rules consistently across contributors?',
                'options': [
                    'Checkstyle',
                    'curl',
                    'scp',
                    'top'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What should every demo script include before sharing a mini project?',
                'options': [
                    'IDE color scheme',
                    'Steps to set up, run, and validate expected output',
                    'List of installed browsers',
                    'Company mission statement'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do Kanban swimlanes help mini projects stay focused?',
                'options': [
                    'They slow down delivery intentionally',
                    'They visualize state (todo/doing/done) to reduce multitasking',
                    'They replace status updates',
                    'They automate deployments'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Why capture a retro after each Java experiment?',
                'options': [
                    'To remove documentation',
                    'To record lessons, blockers, and actionable improvements',
                    'To archive binaries',
                    'To update HR files'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which testing library pairs with Mockito for service-layer verification?',
                'options': [
                    'JUnit 5',
                    'Selenium',
                    'GTest',
                    'PyTest'
                ],
                'correct_answer': 1
            },
            {
                'question': 'When should you consider upgrading a mini project into a roadmap item?',
                'options': [
                    'After adding dark mode',
                    'Once the prototype validates user value and technical feasibility',
                    'When the repo hits 5 stars',
                    'After merging to main once'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What keeps dependency versions reproducible in a Java lab?',
                'options': [
                    'Checking in target/ directory',
                    'Locking versions in pom.xml/build.gradle and using Maven Wrapper/Gradle Wrapper',
                    'Relying on latest snapshots',
                    'Copy-pasting jars manually'
                ],
                'correct_answer': 2
            },
        ]

    # Module 12 Questions
    def get_module12_questions(self):
        return [
            {
                'question': 'Which pattern isolates business logic from adapters in Java services?',
                'options': [
                    'Hexagonal (Ports and Adapters)',
                    'Singleton everywhere',
                    'Anemic domain model only',
                    'Big ball of mud'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Why run Flyway or Liquibase migrations as part of CI/CD?',
                'options': [
                    'They minify JavaScript',
                    'They keep database schema changes versioned and repeatable',
                    'They manage CSS variables',
                    'They restart servers'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which cache layer pairs naturally with Spring Boot for hot data?',
                'options': [
                    'Redis via Spring Data Redis',
                    'Local text files',
                    'Excel sheets',
                    'FTP servers'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does SonarQube/SpotBugs enforce in a Java pipeline?',
                'options': [
                    'UI snapshots',
                    'Static analysis, code smells, and coverage thresholds',
                    'Network firewall rules',
                    'Business KPIs'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Why adopt contract tests for REST endpoints?',
                'options': [
                    'They verify JSON/XML schemas stay backward compatible for consumers',
                    'They replace integration tests entirely',
                    'They improve CSS performance',
                    'They manage DNS'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which messaging technology is suited for event-driven Java services?',
                'options': [
                    'Kafka or RabbitMQ with Spring Cloud Stream',
                    'SMTP only',
                    'Telnet',
                    'Bluetooth'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of using docker build + Jib/Buildpacks in Java delivery?',
                'options': [
                    'Create reproducible container images without manual Dockerfiles',
                    'Generate UML diagrams',
                    'Bundle frontend assets',
                    'Manage HR reports'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you ensure graceful shutdown for Spring Boot services?',
                'options': [
                    'Enable actuator shutdown hooks and handle SIGTERM properly',
                    'Kill the JVM process',
                    'Disable logging',
                    'Increase heap size indefinitely'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which testing layers validate persistence logic with an in-memory database?',
                'options': [
                    '@DataJpaTest integration tests',
                    'Unit tests only',
                    'UI tests',
                    'Load tests exclusively'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Why document runbooks alongside deployment manifests?',
                'options': [
                    'They teach CSS',
                    'They provide on-call steps for failures and recovery',
                    'They replace RFCs',
                    'They speed up package downloads'
                ],
                'correct_answer': 2
            },
        ]

    # Module 13 Questions
    def get_module13_questions(self):
        return [
            {
                'question': 'Which Java collection is ideal for implementing a priority queue in interviews?',
                'options': [
                    'PriorityQueue<E>',
                    'LinkedList<E>',
                    'HashSet<E>',
                    'Vector<E>'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How can you discuss JVM tuning in a system design conversation?',
                'options': [
                    'Explain GC selection (G1, ZGC) and heap sizing strategies',
                    'List IDE shortcuts',
                    'Share favorite fonts',
                    'Avoid runtime topics'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Why restate requirements before coding a Java solution?',
                'options': [
                    'To stall for time',
                    'To confirm inputs, outputs, and corner cases with the interviewer',
                    'To showcase memory',
                    'To change the question'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which concurrency primitive showcases Java multithreading knowledge?',
                'options': [
                    'CompletableFuture or ExecutorService',
                    'console.log',
                    'Thread.sleep alone',
                    'goto statements'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the STAR framework stand for?',
                'options': [
                    'Strategy, Tactics, Actions, Results',
                    'Situation, Task, Action, Result',
                    'Start, Talk, Answer, Repeat',
                    'Statement, Timing, Action, Reflection'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How can mock interviews improve Java system design readiness?',
                'options': [
                    'They reveal blind spots in architecture reasoning and terminology',
                    'They replace practice entirely',
                    'They guarantee offers',
                    'They cover salary negotiation only'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which metric should you communicate after solving a performance-focused coding prompt?',
                'options': [
                    'Time and space complexity in Big-O terms',
                    'Favorite debugger',
                    'IDE theme',
                    'Current weather'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a solid follow-up question after finishing a system design plan?',
                'options': [
                    'Ask if there are specific areas to deep dive such as caching, scaling, or failure modes',
                    'Request a job offer immediately',
                    'Discuss vacation plans',
                    'Change the topic to frontend design'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Why maintain a log of solved interview problems with reflections?',
                'options': [
                    'It tracks progress, mistakes, and patterns to revisit',
                    'It replaces LinkedIn',
                    'It impresses recruiters automatically',
                    'It stores passwords'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How should you respond when you spot a bug mid-interview?',
                'options': [
                    'Hide it and hope it is missed',
                    'Call it out, explain impact, and fix it collaboratively',
                    'Restart the interview',
                    'Blame the interviewer'
                ],
                'correct_answer': 2
            },
        ]



