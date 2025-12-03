"""
Management command to seed ReactJS course with complete modules and topics
Run with: python manage.py seed_reactjs_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with ReactJS course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get ReactJS course
        course, created = Course.objects.get_or_create(
            title='REACTJS COURSE – Complete Modules & Topics',
            defaults={
                'description': 'Complete ReactJS course covering React overview, environment setup, components, hooks, routing, forms, styling, Redux, developer tools, and integration.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated ReactJS course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'React Overview',
                'summary': 'Introduction to React framework. Learn about React, Virtual DOM, JSX, React features, and advantages of JSX.',
                'learning_objectives': 'Understand React framework\nLearn about Virtual DOM\nMaster JSX syntax\nUnderstand React features\nLearn advantages of JSX',
                'topics': 'React Introduction\nReact Virtual DOM\nJSX in React\nReact Features\nAdvantage of JSX',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Environment Setup',
                'summary': 'Set up React development environment. Install ReactJS, configure IDE, and build your first React application.',
                'learning_objectives': 'Set up development environment\nInstall ReactJS\nConfigure IDE for React development\nBuild React applications',
                'topics': 'Environment setup\nInstallation of ReactJS\nIDE setup\nBuilding React App',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'React Essentials',
                'summary': 'Learn React essential features, syntaxes, best practices, and coding standards for building React applications.',
                'learning_objectives': 'Understand React essential features\nMaster React syntaxes\nFollow best practices\nAdhere to coding standards',
                'topics': 'React essential features\nSyntaxes\nBest practices\nCoding standards',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Components',
                'summary': 'Master React components. Learn to build components, work with state and props, pass data between components, conditional rendering, event handling, and lists.',
                'learning_objectives': 'Understand React components\nBuild components\nWork with state and props\nPass props from parent to child\nPass data from child to parent\nImplement conditional rendering\nHandle React events\nWork with lists and keys',
                'topics': 'React Component\nBuilding components\nState and props\nPassing props from parent to child\nPassing data from child to parent\nConditional rendering\nReact Event Handling\nReact List and Keys',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'React Hooks',
                'summary': 'Learn React Hooks. Master useState, useEffect, create custom hooks, and understand rules of hooks.',
                'learning_objectives': 'Understand React Hooks\nUse useState hook\nUse useEffect hook\nCreate custom hooks\nFollow rules of hooks',
                'topics': 'Hooks introduction\nuseState\nuseEffect\nCustom hooks\nRules of hooks',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Routing & Forms',
                'summary': 'Master React routing and forms. Learn component lifecycle, Route and Switch components, useParams hook, dynamic routes, form validation, and build SPAs.',
                'learning_objectives': 'Understand React Component Lifecycle\nUse Route and Switch components\nWork with useParams hook\nCreate dynamic routes\nBuild React forms\nImplement form validation\nDesign Single Page Applications',
                'topics': 'React Component Lifecycle\nRoute and Switch components\nuseParams hook\nDynamic routes\nReact forms\nForm validation\nDesigning a Single Page Application',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Styling in React',
                'summary': 'Learn different styling approaches in React including styled components, inline styling, CSS stylesheets, and CSS modules.',
                'learning_objectives': 'Understand styling in React\nUse styled components\nApply inline styling\nUse CSS stylesheets\nWork with CSS modules',
                'topics': 'What is styling\nStyled components\nInline styling\nCSS stylesheet\nCSS modules',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Redux',
                'summary': 'Master Redux for state management. Learn Redux introduction, state management, Redux lifecycle, React with Redux, and error handling.',
                'learning_objectives': 'Understand Redux\nMaster state management with Redux\nUnderstand Redux lifecycle\nIntegrate React with Redux\nHandle React errors',
                'topics': 'Redux introduction\nState management\nRedux lifecycle\nReact with Redux\nReact Error Handling',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Developer Tools',
                'summary': 'Learn React developer tools. Use React Profiler API, implement lazy loading, and optimize React applications.',
                'learning_objectives': 'Use React developer tools\nWork with React Profiler API\nImplement React Lazy Loading\nOptimize React applications',
                'topics': 'Developer tools\nReact Profiler API\nReact Lazy Loading',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Integration',
                'summary': 'Learn to integrate React with backend services. Understand HTTP protocol and integrate React with Spring Boot.',
                'learning_objectives': 'Understand integration concepts\nWork with HTTP protocol\nIntegrate React with Spring Boot\nConnect frontend with backend',
                'topics': 'Integration introduction\nHTTP protocol\nSpring Boot integration',
                'questions': self.get_module10_questions(),
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

    # Module 1 Questions - React Overview
    def get_module1_questions(self):
        return [
            {
                'question': 'What is React?',
                'options': [
                    'A JavaScript library for building user interfaces',
                    'A database',
                    'A web server',
                    'A programming language'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is Virtual DOM?',
                'options': [
                    'A lightweight copy of the real DOM',
                    'A virtual machine',
                    'A database',
                    'A server'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does JSX stand for?',
                'options': [
                    'JavaScript XML',
                    'JavaScript Extension',
                    'Java XML',
                    'JavaScript Syntax'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the main advantage of JSX?',
                'options': [
                    'It allows writing HTML-like syntax in JavaScript',
                    'It makes code faster',
                    'It reduces file size',
                    'It eliminates JavaScript'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - Environment Setup
    def get_module2_questions(self):
        return [
            {
                'question': 'Which tool is commonly used to create React applications?',
                'options': [
                    'Create React App',
                    'React Builder',
                    'React Generator',
                    'React Maker'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What command is used to create a new React app?',
                'options': [
                    'npx create-react-app',
                    'npm create-react',
                    'react create app',
                    'create react app'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which package manager is commonly used with React?',
                'options': [
                    'npm or yarn',
                    'pip',
                    'maven',
                    'gradle'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions - React Essentials
    def get_module3_questions(self):
        return [
            {
                'question': 'What is a key React best practice?',
                'options': [
                    'Keep components small and focused',
                    'Use global variables',
                    'Avoid using functions',
                    'Write all code in one file'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What naming convention is used for React components?',
                'options': [
                    'PascalCase',
                    'camelCase',
                    'snake_case',
                    'kebab-case'
                ],
                'correct_answer': 1
            },
        ]

    # Module 4 Questions - Components
    def get_module4_questions(self):
        return [
            {
                'question': 'What is a component in React?',
                'options': [
                    'A reusable piece of UI',
                    'A function',
                    'A variable',
                    'A class'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between state and props?',
                'options': [
                    'State is internal, props are passed from parent',
                    'They are the same',
                    'Props are internal, state is passed',
                    'State is for functions, props for classes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'How do you pass data from parent to child component?',
                'options': [
                    'Using props',
                    'Using state',
                    'Using context',
                    'Using refs'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of keys in React lists?',
                'options': [
                    'To help React identify which items have changed',
                    'To encrypt data',
                    'To sort items',
                    'To filter items'
                ],
                'correct_answer': 1
            },
        ]

    # Module 5 Questions - React Hooks
    def get_module5_questions(self):
        return [
            {
                'question': 'What are React Hooks?',
                'options': [
                    'Functions that let you use state and lifecycle features',
                    'Event handlers',
                    'CSS hooks',
                    'Database hooks'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does useState return?',
                'options': [
                    'An array with state value and setter function',
                    'Just the state value',
                    'Just the setter function',
                    'An object'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is useEffect used for?',
                'options': [
                    'To perform side effects in functional components',
                    'To create effects',
                    'To handle events',
                    'To manage state'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a rule of hooks?',
                'options': [
                    'Only call hooks at the top level',
                    'Call hooks in loops',
                    'Call hooks conditionally',
                    'Call hooks in regular functions'
                ],
                'correct_answer': 1
            },
        ]

    # Module 6 Questions - Routing & Forms
    def get_module6_questions(self):
        return [
            {
                'question': 'Which library is commonly used for routing in React?',
                'options': [
                    'React Router',
                    'React Route',
                    'React Navigation',
                    'React Link'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is useParams used for?',
                'options': [
                    'To access route parameters',
                    'To set parameters',
                    'To delete parameters',
                    'To validate parameters'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a Single Page Application (SPA)?',
                'options': [
                    'An application that loads a single HTML page',
                    'An application with one component',
                    'An application with one route',
                    'An application with one user'
                ],
                'correct_answer': 1
            },
        ]

    # Module 7 Questions - Styling in React
    def get_module7_questions(self):
        return [
            {
                'question': 'What are styled components?',
                'options': [
                    'CSS-in-JS library for styling React components',
                    'Pre-styled components',
                    'CSS files',
                    'Inline styles'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the advantage of CSS modules?',
                'options': [
                    'Scoped CSS that prevents style conflicts',
                    'Global styles',
                    'Faster rendering',
                    'Smaller file size'
                ],
                'correct_answer': 1
            },
        ]

    # Module 8 Questions - Redux
    def get_module8_questions(self):
        return [
            {
                'question': 'What is Redux?',
                'options': [
                    'A state management library',
                    'A component library',
                    'A routing library',
                    'A styling library'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What are the three principles of Redux?',
                'options': [
                    'Single source of truth, state is read-only, changes are made with pure functions',
                    'Multiple sources, mutable state, impure functions',
                    'No state, read-write state, functions',
                    'Global state, local state, mixed state'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is an action in Redux?',
                'options': [
                    'An object that describes what happened',
                    'A function',
                    'A component',
                    'A state'
                ],
                'correct_answer': 1
            },
        ]

    # Module 9 Questions - Developer Tools
    def get_module9_questions(self):
        return [
            {
                'question': 'What is React Profiler used for?',
                'options': [
                    'To measure performance of React components',
                    'To profile users',
                    'To create profiles',
                    'To manage profiles'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is React.lazy used for?',
                'options': [
                    'To lazy load components',
                    'To create lazy components',
                    'To delay rendering',
                    'To skip rendering'
                ],
                'correct_answer': 1
            },
        ]

    # Module 10 Questions - Integration
    def get_module10_questions(self):
        return [
            {
                'question': 'What is the most common way to make HTTP requests in React?',
                'options': [
                    'fetch API or axios',
                    'XMLHttpRequest only',
                    'jQuery only',
                    'WebSocket only'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is CORS?',
                'options': [
                    'Cross-Origin Resource Sharing',
                    'Cross-Origin Request Sharing',
                    'Cross-Origin Response Sharing',
                    'Cross-Origin Resource Request'
                ],
                'correct_answer': 1
            },
        ]

