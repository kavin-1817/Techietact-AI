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
            {
                'question': 'What does JDK stand for?',
                'options': [
                    'Java Development Kit',
                    'Java Deployment Kit',
                    'Java Design Kit',
                    'Java Debugging Kit'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does JRE stand for?',
                'options': [
                    'Java Runtime Environment',
                    'Java Runtime Engine',
                    'Java Runtime Extension',
                    'Java Runtime Execution'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between JDK and JRE?',
                'options': [
                    'JDK includes development tools, JRE only includes runtime',
                    'JRE includes development tools, JDK only includes runtime',
                    'They are identical',
                    'JDK is for servers, JRE is for clients'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is bytecode?',
                'options': [
                    'Intermediate code that JVM executes',
                    'Source code',
                    'Machine code',
                    'Assembly code'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of javac command?',
                'options': [
                    'To compile Java source code to bytecode',
                    'To run Java programs',
                    'To debug Java programs',
                    'To package Java programs'
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
            {
                'question': 'Which tool is used to run Java programs?',
                'options': [
                    'javac',
                    'java',
                    'javadoc',
                    'jar'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of Eclipse IDE?',
                'options': [
                    'To provide integrated development environment for Java',
                    'To compile Java code',
                    'To run Java programs',
                    'To debug Java programs'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a workspace in Eclipse?',
                'options': [
                    'A directory where projects are stored',
                    'A project',
                    'A file',
                    'A package'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of package explorer in Eclipse?',
                'options': [
                    'To navigate project structure',
                    'To compile code',
                    'To run programs',
                    'To debug programs'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of console in Eclipse?',
                'options': [
                    'To display program output',
                    'To write code',
                    'To compile code',
                    'To debug code'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of debugger in Eclipse?',
                'options': [
                    'To debug Java programs',
                    'To compile code',
                    'To run programs',
                    'To format code'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of code completion in IDE?',
                'options': [
                    'To suggest code while typing',
                    'To compile code',
                    'To run code',
                    'To debug code'
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
            {
                'question': 'What is the difference between == and equals()?',
                'options': [
                    '== compares references, equals() compares values',
                    'equals() compares references, == compares values',
                    'They are identical',
                    '== is for primitives, equals() is for objects'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the result of: 10 / 3?',
                'options': [
                    '3.33',
                    '3',
                    '3.0',
                    '4'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the result of: 10.0 / 3?',
                'options': [
                    '3',
                    '3.33',
                    '3.3333333333333335',
                    '4'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the logical AND operator?',
                'options': [
                    '&&',
                    '||',
                    '!',
                    '&'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the logical OR operator?',
                'options': [
                    '&&',
                    '||',
                    '!',
                    '&'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the NOT operator?',
                'options': [
                    '&&',
                    '||',
                    '!',
                    '&'
                ],
                'correct_answer': 3
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
            {
                'question': 'What is the syntax for a for loop?',
                'options': [
                    'for(initialization; condition; increment)',
                    'for(condition; initialization; increment)',
                    'for(increment; condition; initialization)',
                    'for(initialization; increment; condition)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the syntax for a while loop?',
                'options': [
                    'while(condition)',
                    'while(initialization)',
                    'while(increment)',
                    'while(statement)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the syntax for a do-while loop?',
                'options': [
                    'do { } while(condition);',
                    'do while(condition) { }',
                    'while(condition) do { }',
                    'do(condition) while { }'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a nested loop?',
                'options': [
                    'A loop inside another loop',
                    'A loop that is nested in a class',
                    'A loop that is nested in a method',
                    'A loop that cannot be executed'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an infinite loop?',
                'options': [
                    'A loop that never terminates',
                    'A loop that runs once',
                    'A loop that cannot start',
                    'A loop that is broken'
                ],
                'correct_answer': 1
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
            {
                'question': 'What is a void method?',
                'options': [
                    'A method that returns no value',
                    'A method that returns void',
                    'A method that is empty',
                    'A method that cannot be called'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is method signature?',
                'options': [
                    'Method name and parameter list',
                    'Method name only',
                    'Parameter list only',
                    'Return type only'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a parameter?',
                'options': [
                    'A variable passed to a method',
                    'A value returned from a method',
                    'A method name',
                    'A class name'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an argument?',
                'options': [
                    'A value passed to a method when calling it',
                    'A variable in a method',
                    'A return value',
                    'A method name'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between parameter and argument?',
                'options': [
                    'Parameter is in method definition, argument is in method call',
                    'Argument is in method definition, parameter is in method call',
                    'They are identical',
                    'Parameter is for primitives, argument is for objects'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a static method?',
                'options': [
                    'A method that belongs to the class',
                    'A method that belongs to an instance',
                    'A method that cannot be called',
                    'A method that is final'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an instance method?',
                'options': [
                    'A method that belongs to an instance',
                    'A method that belongs to the class',
                    'A method that cannot be called',
                    'A method that is static'
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
            {
                'question': 'What is a variable?',
                'options': [
                    'A named storage location',
                    'A method',
                    'A class',
                    'A package'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is variable scope?',
                'options': [
                    'The region where a variable is accessible',
                    'The type of a variable',
                    'The value of a variable',
                    'The name of a variable'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a local variable?',
                'options': [
                    'A variable declared in a class',
                    'A variable declared inside a method or block',
                    'A variable declared in a package',
                    'A variable declared globally'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is an instance variable?',
                'options': [
                    'A variable declared in a method',
                    'A variable declared in a class, outside methods',
                    'A variable declared in a block',
                    'A variable declared in a package'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a static variable?',
                'options': [
                    'A variable that belongs to an instance',
                    'A variable that belongs to the class',
                    'A variable that cannot change',
                    'A variable that is final'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is variable shadowing?',
                'options': [
                    'When a variable is hidden',
                    'When a local variable hides an instance variable',
                    'When a variable is deleted',
                    'When a variable is renamed'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of final keyword for variables?',
                'options': [
                    'To make a variable static',
                    'To make a variable constant',
                    'To make a variable public',
                    'To make a variable private'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is type casting?',
                'options': [
                    'Creating a new type',
                    'Converting one data type to another',
                    'Deleting a type',
                    'Renaming a type'
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
                    'Inheriting from a parent class',
                    'Hiding implementation details',
                    'Creating multiple objects',
                    'Using static methods'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of getters and setters?',
                'options': [
                    'To create objects',
                    'To access and modify private fields',
                    'To inherit from classes',
                    'To handle exceptions'
                ],
                'correct_answer': 2
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
            {
                'question': 'What is a default constructor?',
                'options': [
                    'A constructor with parameters',
                    'A constructor with no parameters',
                    'A constructor that is private',
                    'A constructor that is static'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a parameterized constructor?',
                'options': [
                    'A constructor with no parameters',
                    'A constructor that takes parameters',
                    'A constructor that is private',
                    'A constructor that is static'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of this keyword?',
                'options': [
                    'To refer to parent class',
                    'To refer to current object',
                    'To refer to child class',
                    'To refer to static members'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of super keyword?',
                'options': [
                    'To refer to current object',
                    'To refer to parent class',
                    'To refer to child class',
                    'To refer to static members'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is polymorphism?',
                'options': [
                    'Ability to create objects',
                    'Ability of an object to take many forms',
                    'Ability to delete objects',
                    'Ability to update objects'
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
                    'There is no difference',
                    'String literal is stored in string pool, String Object is in heap',
                    'String literal is mutable, String Object is immutable',
                    'String literal cannot be created'
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
                'question': 'What is an abstract class?',
                'options': [
                    'A class that can be instantiated',
                    'A class that cannot be instantiated',
                    'A class that is final',
                    'A class that is static'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is an interface?',
                'options': [
                    'A class with implementation',
                    'A contract that defines methods without implementation',
                    'A variable',
                    'A method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is method overriding?',
                'options': [
                    'Creating a new method',
                    'Providing a new implementation of a parent class method',
                    'Deleting a method',
                    'Renaming a method'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between abstract class and interface?',
                'options': [
                    'Interface can have implementation, abstract class cannot',
                    'Abstract class can have implementation, interface cannot (before Java 8)',
                    'They are identical',
                    'Abstract class is for primitives, interface is for objects'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of @Override annotation?',
                'options': [
                    'To create overrides',
                    'To indicate method overriding',
                    'To delete overrides',
                    'To update overrides'
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
                    '1',
                    '0',
                    '-1',
                    'Depends on the array'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the enhanced for loop also known as?',
                'options': [
                    'while loop',
                    'do-while loop',
                    'for-each loop',
                    'traditional for loop'
                ],
                'correct_answer': 3
            },
            {
                'question': 'In Java, are primitive types passed by value or reference?',
                'options': [
                    'By reference',
                    'Both',
                    'By value',
                    'Neither'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you declare an array?',
                'options': [
                    'int arr;',
                    'array int arr;',
                    'int[] arr; or int arr[];',
                    'int array arr;'
                ],
                'correct_answer': 3
            },
            {
                'question': 'How do you initialize an array?',
                'options': [
                    'int arr = new int[5];',
                    'int[] arr = int[5];',
                    'int[] arr = new int[5];',
                    'int arr = int[5];'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is ArrayIndexOutOfBoundsException?',
                'options': [
                    'Exception thrown when array is null',
                    'Exception thrown when array is empty',
                    'Exception thrown when accessing invalid array index',
                    'Exception thrown when array is full'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a multidimensional array?',
                'options': [
                    'A single array',
                    'A variable',
                    'An array of arrays',
                    'A method'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the syntax for enhanced for loop?',
                'options': [
                    'for(array : type variable)',
                    'for(variable : type array)',
                    'for(type variable : array)',
                    'for(type : variable array)'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Can you change the size of an array after creation?',
                'options': [
                    'Yes',
                    'Only if it is empty',
                    'No',
                    'Only if it is full'
                ],
                'correct_answer': 3
            },
        ]

    # Module 10 Questions
    def get_module10_questions(self):
        return [
            {
                'question': 'Which interface does ArrayList implement?',
                'options': [
                    'Set',
                    'Map',
                    'List',
                    'Queue'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is autoboxing?',
                'options': [
                    'Converting wrapper object to primitive automatically',
                    'Creating a box',
                    'Converting primitive to wrapper object automatically',
                    'Wrapping code'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between ArrayList and LinkedList?',
                'options': [
                    'ArrayList is faster for insertion, LinkedList for access',
                    'They are the same',
                    'LinkedList is faster for insertion, ArrayList for access',
                    'ArrayList cannot store objects'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of an Iterator?',
                'options': [
                    'To create collections',
                    'To sort collections',
                    'To iterate over collection elements',
                    'To filter collections'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is unboxing?',
                'options': [
                    'Converting primitive to wrapper object',
                    'Creating a box',
                    'Converting wrapper object to primitive',
                    'Deleting a box'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the Collection framework?',
                'options': [
                    'A single class',
                    'A single interface',
                    'A set of classes and interfaces for storing and manipulating groups of objects',
                    'A method'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between Collection and Collections?',
                'options': [
                    'Collections is an interface, Collection is a utility class',
                    'They are identical',
                    'Collection is an interface, Collections is a utility class',
                    'Collection is for primitives, Collections is for objects'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of add() method in ArrayList?',
                'options': [
                    'To remove an element',
                    'To get an element',
                    'To add an element to the list',
                    'To update an element'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of remove() method in ArrayList?',
                'options': [
                    'To add an element',
                    'To get an element',
                    'To remove an element from the list',
                    'To update an element'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of get() method in ArrayList?',
                'options': [
                    'To add an element',
                    'To remove an element',
                    'To get an element at a specific index',
                    'To update an element'
                ],
                'correct_answer': 3
            },
        ]

    # Module 11 Questions
    def get_module11_questions(self):
        return [
            {
                'question': 'What is generics in Java?',
                'options': [
                    'A way to create generic classes',
                    'A programming language',
                    'Type-safe collections',
                    'A design pattern'
                ],
                'correct_answer': 3
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
                    'A type parameter',
                    'A method',
                    '? symbol used to represent unknown type',
                    'A class'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of generics?',
                'options': [
                    'To create types',
                    'To delete types',
                    'To provide type safety and eliminate type casting',
                    'To update types'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a bounded type parameter?',
                'options': [
                    'A type parameter without restrictions',
                    'A type parameter that is null',
                    'A type parameter with restrictions',
                    'A type parameter that is void'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is <? extends T> wildcard?',
                'options': [
                    'Lower bounded wildcard',
                    'Unbounded wildcard',
                    'Upper bounded wildcard',
                    'No wildcard'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is <? super T> wildcard?',
                'options': [
                    'Upper bounded wildcard',
                    'Unbounded wildcard',
                    'Lower bounded wildcard',
                    'No wildcard'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is <?> wildcard?',
                'options': [
                    'Upper bounded wildcard',
                    'Lower bounded wildcard',
                    'Unbounded wildcard',
                    'No wildcard'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is type erasure?',
                'options': [
                    'Process of adding type information',
                    'Process of updating type information',
                    'Process of removing type information at runtime',
                    'Process of deleting type information'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Can you use primitives with generics?',
                'options': [
                    'Yes, directly',
                    'Only in some cases',
                    'No, only wrapper classes',
                    'Only with arrays'
                ],
                'correct_answer': 3
            },
        ]

    # Module 12 Questions
    def get_module12_questions(self):
        return [
            {
                'question': 'Which collection does not allow duplicate elements?',
                'options': [
                    'List',
                    'Map',
                    'Set',
                    'Queue'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between HashSet and TreeSet?',
                'options': [
                    'HashSet is sorted, TreeSet is not',
                    'They are the same',
                    'TreeSet is sorted, HashSet is not',
                    'HashSet allows null, TreeSet does not'
                ],
                'correct_answer': 3
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
                    'They are the same',
                    'Comparable is for primitives, Comparator for objects',
                    'Comparable defines natural ordering, Comparator defines custom ordering'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the difference between HashMap and Hashtable?',
                'options': [
                    'Hashtable is not synchronized, HashMap is synchronized',
                    'They are identical',
                    'HashMap is not synchronized, Hashtable is synchronized',
                    'HashMap is for primitives, Hashtable is for objects'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between HashMap and LinkedHashMap?',
                'options': [
                    'HashMap maintains insertion order',
                    'They are identical',
                    'LinkedHashMap maintains insertion order',
                    'LinkedHashMap is faster'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of put() method in Map?',
                'options': [
                    'To remove a key-value pair',
                    'To get a value',
                    'To update a key',
                    'To add a key-value pair'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of get() method in Map?',
                'options': [
                    'To add a key-value pair',
                    'To remove a key-value pair',
                    'To update a key',
                    'To get a value by key'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of keySet() method in Map?',
                'options': [
                    'To get all values',
                    'To get all entries',
                    'To get the size',
                    'To get all keys as a Set'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of values() method in Map?',
                'options': [
                    'To get all keys',
                    'To get all entries',
                    'To get the size',
                    'To get all values as a Collection'
                ],
                'correct_answer': 4
            },
        ]

    # Module 13 Questions
    def get_module13_questions(self):
        return [
            {
                'question': 'What is a lambda expression?',
                'options': [
                    'A named function',
                    'A class',
                    'A variable',
                    'An anonymous function'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the syntax for a lambda expression?',
                'options': [
                    'parameters -> expression',
                    '(parameters) => expression',
                    'lambda parameters: expression',
                    '(parameters) -> expression'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a Predicate in Java?',
                'options': [
                    'A class',
                    'A method',
                    'A variable',
                    'A functional interface that takes one argument and returns boolean'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a functional interface?',
                'options': [
                    'An interface with multiple methods',
                    'An interface with no methods',
                    'An interface that is final',
                    'An interface with exactly one abstract method'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is Stream API?',
                'options': [
                    'API for file processing',
                    'API for network processing',
                    'API for database processing',
                    'API for processing sequences of elements'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of filter() in Stream?',
                'options': [
                    'To create a stream',
                    'To delete a stream',
                    'To update a stream',
                    'To filter elements based on a condition'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of map() in Stream?',
                'options': [
                    'To create a stream',
                    'To delete a stream',
                    'To update a stream',
                    'To transform elements'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of forEach() in Stream?',
                'options': [
                    'To create a stream',
                    'To delete a stream',
                    'To update a stream',
                    'To perform an action on each element'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of collect() in Stream?',
                'options': [
                    'To create a stream',
                    'To delete a stream',
                    'To update a stream',
                    'To collect results into a collection'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is method reference?',
                'options': [
                    'A way to create methods',
                    'A way to delete methods',
                    'A way to update methods',
                    'A shorthand syntax for lambda expressions'
                ],
                'correct_answer': 4
            },
        ]

    # Module 14 Questions
    def get_module14_questions(self):
        return [
            {
                'question': 'Which class is used to read characters from a file?',
                'options': [
                    'FileInputStream',
                    'FileWriter',
                    'BufferedReader',
                    'FileReader'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which class provides buffered reading?',
                'options': [
                    'FileReader',
                    'FileInputStream',
                    'Reader',
                    'BufferedReader'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is serialization in Java?',
                'options': [
                    'Converting byte stream to object',
                    'Reading from file',
                    'Writing to file',
                    'Converting object to byte stream'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which interface must be implemented for serialization?',
                'options': [
                    'Cloneable',
                    'Comparable',
                    'Runnable',
                    'Serializable'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is try-with-resources?',
                'options': [
                    'A way to handle exceptions',
                    'A way to create files',
                    'A way to delete files',
                    'A way to automatically close resources'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which class is used to write characters to a file?',
                'options': [
                    'FileReader',
                    'FileInputStream',
                    'BufferedReader',
                    'FileWriter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which class provides buffered writing?',
                'options': [
                    'FileWriter',
                    'FileReader',
                    'FileInputStream',
                    'BufferedWriter'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is deserialization?',
                'options': [
                    'Converting object to byte stream',
                    'Reading from file',
                    'Writing to file',
                    'Converting byte stream to object'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of File class?',
                'options': [
                    'To read files',
                    'To write files',
                    'To delete files',
                    'To represent file and directory pathnames'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of Scanner class?',
                'options': [
                    'To scan files',
                    'To scan directories',
                    'To scan networks',
                    'To parse primitive types and strings'
                ],
                'correct_answer': 4
            },
        ]

    # Module 15 Questions
    def get_module15_questions(self):
        return [
            {
                'question': 'What is debugging?',
                'options': [
                    'Writing code',
                    'Compiling code',
                    'Running code',
                    'Finding and fixing errors in code'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a breakpoint?',
                'options': [
                    'A compilation error',
                    'A runtime error',
                    'A syntax error',
                    'A point where program execution pauses'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is step over in debugging?',
                'options': [
                    'Execute and enter method',
                    'Execute and exit method',
                    'Skip current line',
                    'Execute current line and move to next'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is step into in debugging?',
                'options': [
                    'Execute current line and move to next',
                    'Execute and exit method',
                    'Skip current line',
                    'Execute and enter method calls'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is step out in debugging?',
                'options': [
                    'Execute current line and move to next',
                    'Execute and enter method',
                    'Skip current line',
                    'Execute and exit current method'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a watch expression?',
                'options': [
                    'A way to watch code',
                    'A way to watch files',
                    'A way to watch directories',
                    'An expression to monitor variable values'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of debugger?',
                'options': [
                    'To compile code',
                    'To run code',
                    'To format code',
                    'To help find and fix bugs'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a stack trace?',
                'options': [
                    'A way to trace files',
                    'A way to trace directories',
                    'A way to trace networks',
                    'A list of method calls leading to an error'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of conditional breakpoint?',
                'options': [
                    'To pause execution always',
                    'To pause execution never',
                    'To pause execution randomly',
                    'To pause execution when condition is met'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of exception breakpoint?',
                'options': [
                    'To pause execution always',
                    'To pause execution never',
                    'To pause execution randomly',
                    'To pause execution when exception occurs'
                ],
                'correct_answer': 4
            },
        ]

    # Module 16 Questions
    def get_module16_questions(self):
        return [
            {
                'question': 'What is Git?',
                'options': [
                    'A programming language',
                    'An IDE',
                    'A database',
                    'A version control system'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which command is used to clone a Git repository?',
                'options': [
                    'git copy',
                    'git download',
                    'git get',
                    'git clone'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a repository in Git?',
                'options': [
                    'A file',
                    'A folder',
                    'A program',
                    'A storage location for your project'
                ],
                'correct_answer': 4
            },
        ]
