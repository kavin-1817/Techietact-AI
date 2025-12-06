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
            {
                'question': 'What is the main advantage of Virtual DOM?',
                'options': [
                    'Faster updates by minimizing DOM manipulation',
                    'Smaller file size',
                    'Better security',
                    'Easier debugging'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Who created React?',
                'options': [
                    'Google',
                    'Microsoft',
                    'Facebook',
                    'Twitter'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is React used for?',
                'options': [
                    'Building user interfaces',
                    'Building databases',
                    'Building servers',
                    'Building operating systems'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between React and React Native?',
                'options': [
                    'React is for web, React Native is for mobile',
                    'React Native is for web, React is for mobile',
                    'They are identical',
                    'React is newer than React Native'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of Babel in React?',
                'options': [
                    'To transpile JSX to JavaScript',
                    'To compile JavaScript',
                    'To minify code',
                    'To bundle code'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is one-way data binding in React?',
                'options': [
                    'Data flows from parent to child components',
                    'Data flows from child to parent',
                    'Data flows both ways',
                    'Data doesn\'t flow'
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
            {
                'question': 'What command is used to start a React development server?',
                'options': [
                    'npm start',
                    'npm run',
                    'npm serve',
                    'npm dev'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What command is used to build a React app for production?',
                'options': [
                    'npm build',
                    'npm run build',
                    'npm compile',
                    'npm package'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the default port for React development server?',
                'options': [
                    '3000',
                    '8080',
                    '5000',
                    '8000'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is webpack used for in React?',
                'options': [
                    'To bundle and transpile code',
                    'To create components',
                    'To manage state',
                    'To handle routing'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of package.json in React?',
                'options': [
                    'To define project dependencies and scripts',
                    'To define components',
                    'To define state',
                    'To define routes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of node_modules folder?',
                'options': [
                    'To store installed npm packages',
                    'To store components',
                    'To store state',
                    'To store routes'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of .gitignore file?',
                'options': [
                    'To exclude files from version control',
                    'To include files in version control',
                    'To track files',
                    'To delete files'
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
                    'Use global variables',
                    'Keep components small and focused',
                    'Avoid using functions',
                    'Write all code in one file'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What naming convention is used for React components?',
                'options': [
                    'camelCase',
                    'PascalCase',
                    'snake_case',
                    'kebab-case'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of React.StrictMode?',
                'options': [
                    'To identify potential problems in the application',
                    'To make code faster',
                    'To reduce file size',
                    'To add features'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of React.Fragment?',
                'options': [
                    'To group elements without adding extra DOM nodes',
                    'To create fragments',
                    'To split components',
                    'To combine components'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the difference between React.createElement and JSX?',
                'options': [
                    'JSX is syntactic sugar for React.createElement',
                    'They are different languages',
                    'React.createElement is newer',
                    'JSX is faster'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of React.memo?',
                'options': [
                    'To memoize components and prevent unnecessary re-renders',
                    'To create memory',
                    'To delete memory',
                    'To manage memory'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of React.PureComponent?',
                'options': [
                    'To optimize class components with shallow comparison',
                    'To create pure components',
                    'To delete components',
                    'To update components'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of PropTypes?',
                'options': [
                    'To validate component props',
                    'To create props',
                    'To delete props',
                    'To update props'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of defaultProps?',
                'options': [
                    'To set default values for props',
                    'To create props',
                    'To delete props',
                    'To update props'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the purpose of React.Children?',
                'options': [
                    'To create children',
                    'To manipulate and work with child components',
                    'To delete children',
                    'To update children'
                ],
                'correct_answer': 2
            },
        ]

    # Module 4 Questions - Components
    def get_module4_questions(self):
        return [
            {
                'question': 'What is a component in React?',
                'options': [
                    'A function',
                    'A reusable piece of UI',
                    'A variable',
                    'A class'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between state and props?',
                'options': [
                    'They are the same',
                    'State is internal, props are passed from parent',
                    'Props are internal, state is passed',
                    'State is for functions, props for classes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'How do you pass data from parent to child component?',
                'options': [
                    'Using state',
                    'Using props',
                    'Using context',
                    'Using refs'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of keys in React lists?',
                'options': [
                    'To encrypt data',
                    'To help React identify which items have changed',
                    'To sort items',
                    'To filter items'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the difference between functional and class components?',
                'options': [
                    'Class components are faster',
                    'Functional components use functions, class components use classes',
                    'Functional components are deprecated',
                    'They are identical'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a controlled component?',
                'options': [
                    'A component that controls other components',
                    'A component whose value is controlled by React state',
                    'A component that cannot be controlled',
                    'A component with no state'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is an uncontrolled component?',
                'options': [
                    'A component that cannot be controlled',
                    'A component whose value is controlled by the DOM',
                    'A component with no props',
                    'A component with no state'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of refs?',
                'options': [
                    'To create references',
                    'To access DOM elements directly',
                    'To delete references',
                    'To update references'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of forwardRef?',
                'options': [
                    'To create refs',
                    'To forward refs to child components',
                    'To delete refs',
                    'To update refs'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is the purpose of React.cloneElement?',
                'options': [
                    'To create elements',
                    'To clone and modify React elements',
                    'To delete elements',
                    'To update elements'
                ],
                'correct_answer': 2
            },
        ]

    # Module 5 Questions - React Hooks
    def get_module5_questions(self):
        return [
            {
                'question': 'What are React Hooks?',
                'options': [
                    'Event handlers',
                    'Functions that let you use state and lifecycle features',
                    'CSS hooks',
                    'Database hooks'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What does useState return?',
                'options': [
                    'Just the state value',
                    'Just the setter function',
                    'An array with state value and setter function',
                    'An object'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is useEffect used for?',
                'options': [
                    'To create effects',
                    'To handle events',
                    'To perform side effects in functional components',
                    'To manage state'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a rule of hooks?',
                'options': [
                    'Call hooks in loops',
                    'Call hooks conditionally',
                    'Only call hooks at the top level',
                    'Call hooks in regular functions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is useContext used for?',
                'options': [
                    'To create context',
                    'To access React context',
                    'To delete context',
                    'To update context'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is useReducer used for?',
                'options': [
                    'To create reducers',
                    'To manage complex state logic',
                    'To delete reducers',
                    'To update reducers'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is useMemo used for?',
                'options': [
                    'To create memory',
                    'To memoize expensive calculations',
                    'To delete memory',
                    'To manage memory'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is useCallback used for?',
                'options': [
                    'To create callbacks',
                    'To memoize callback functions',
                    'To delete callbacks',
                    'To update callbacks'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is useRef used for?',
                'options': [
                    'To create refs',
                    'To create mutable references',
                    'To delete refs',
                    'To update refs'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is a custom hook?',
                'options': [
                    'A built-in hook',
                    'A function that uses other hooks',
                    'A component hook',
                    'A service hook'
                ],
                'correct_answer': 2
            },
        ]

    # Module 6 Questions - Routing & Forms
    def get_module6_questions(self):
        return [
            {
                'question': 'Which library is commonly used for routing in React?',
                'options': [
                    'React Route',
                    'React Navigation',
                    'React Router',
                    'React Link'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is useParams used for?',
                'options': [
                    'To set parameters',
                    'To delete parameters',
                    'To access route parameters',
                    'To validate parameters'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a Single Page Application (SPA)?',
                'options': [
                    'An application with one component',
                    'An application with one route',
                    'An application that loads a single HTML page',
                    'An application with one user'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is BrowserRouter used for?',
                'options': [
                    'To disable routing',
                    'To enable routing with HTML5 history API',
                    'To create routes',
                    'To delete routes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is Route component used for?',
                'options': [
                    'To create routes',
                    'To define a route',
                    'To delete routes',
                    'To update routes'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is Link component used for?',
                'options': [
                    'To create links',
                    'To navigate between routes',
                    'To delete links',
                    'To update links'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is useNavigate used for?',
                'options': [
                    'To create navigation',
                    'To programmatically navigate',
                    'To delete navigation',
                    'To update navigation'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is useLocation used for?',
                'options': [
                    'To create location',
                    'To delete location',
                    'To access current location object',
                    'To update location'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a route parameter?',
                'options': [
                    'A static segment',
                    'A query parameter',
                    'A dynamic segment in the URL',
                    'A hash parameter'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of form handling in React?',
                'options': [
                    'To create forms',
                    'To delete forms',
                    'To manage form state and submission',
                    'To update forms'
                ],
                'correct_answer': 3
            },
        ]

    # Module 7 Questions - Styling in React
    def get_module7_questions(self):
        return [
            {
                'question': 'What are styled components?',
                'options': [
                    'Pre-styled components',
                    'CSS files',
                    'CSS-in-JS library for styling React components',
                    'Inline styles'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the advantage of CSS modules?',
                'options': [
                    'Global styles',
                    'Faster rendering',
                    'Smaller file size',
                    'Scoped CSS that prevents style conflicts'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is inline styling in React?',
                'options': [
                    'Styling using CSS files',
                    'Styling using external stylesheets',
                    'Styling using style prop with JavaScript objects',
                    'Styling using HTML attributes'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of className in React?',
                'options': [
                    'To create classes',
                    'To delete classes',
                    'To apply CSS classes',
                    'To update classes'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the difference between className and class?',
                'options': [
                    'class is used in React, className is reserved',
                    'They are identical',
                    'className is used in React, class is reserved keyword',
                    'className is for components, class is for elements'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is CSS-in-JS?',
                'options': [
                    'Writing JavaScript in CSS',
                    'Writing CSS in HTML',
                    'Writing CSS styles in JavaScript',
                    'Writing HTML in CSS'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of emotion library?',
                'options': [
                    'State management',
                    'Routing',
                    'CSS-in-JS library for styling',
                    'Form handling'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of Tailwind CSS with React?',
                'options': [
                    'Component library',
                    'State management',
                    'Utility-first CSS framework',
                    'Routing library'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of Material-UI?',
                'options': [
                    'CSS framework',
                    'State management',
                    'React component library with Material Design',
                    'Routing library'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of Sass/SCSS in React?',
                'options': [
                    'JavaScript preprocessor',
                    'HTML preprocessor',
                    'CSS preprocessor for better styling',
                    'React preprocessor'
                ],
                'correct_answer': 3
            },
        ]

    # Module 8 Questions - Redux
    def get_module8_questions(self):
        return [
            {
                'question': 'What is Redux?',
                'options': [
                    'A component library',
                    'A routing library',
                    'A styling library',
                    'A state management library'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What are the three principles of Redux?',
                'options': [
                    'Multiple sources, mutable state, impure functions',
                    'No state, read-write state, functions',
                    'Global state, local state, mixed state',
                    'Single source of truth, state is read-only, changes are made with pure functions'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is an action in Redux?',
                'options': [
                    'A function',
                    'A component',
                    'A state',
                    'An object that describes what happened'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is a reducer in Redux?',
                'options': [
                    'A component',
                    'A service',
                    'A pure function that takes state and action, returns new state',
                    'A directive'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is a store in Redux?',
                'options': [
                    'A component',
                    'A service',
                    'An object that holds application state',
                    'A directive'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is dispatch used for in Redux?',
                'options': [
                    'To create actions',
                    'To delete actions',
                    'To send actions to the store',
                    'To update actions'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is useSelector used for?',
                'options': [
                    'To create selectors',
                    'To delete selectors',
                    'To extract data from Redux store',
                    'To update selectors'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is useDispatch used for?',
                'options': [
                    'To create dispatches',
                    'To delete dispatches',
                    'To dispatch actions in functional components',
                    'To update dispatches'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is Redux Toolkit?',
                'options': [
                    'A component library',
                    'A routing library',
                    'Official toolset for efficient Redux development',
                    'A styling library'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What is the purpose of createSlice in Redux Toolkit?',
                'options': [
                    'To create slices',
                    'To delete slices',
                    'To update slices',
                    'To create reducers and actions together'
                ],
                'correct_answer': 4
            },
        ]

    # Module 9 Questions - Developer Tools
    def get_module9_questions(self):
        return [
            {
                'question': 'What is React Profiler used for?',
                'options': [
                    'To profile users',
                    'To create profiles',
                    'To manage profiles',
                    'To measure performance of React components'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is React.lazy used for?',
                'options': [
                    'To create lazy components',
                    'To delay rendering',
                    'To skip rendering',
                    'To lazy load components'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is React DevTools?',
                'options': [
                    'A component library',
                    'A routing library',
                    'A styling library',
                    'Browser extension for debugging React applications'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of Suspense?',
                'options': [
                    'To create suspense',
                    'To delete suspense',
                    'To update suspense',
                    'To handle loading states for lazy components'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is code splitting?',
                'options': [
                    'Splitting components',
                    'Splitting state',
                    'Splitting props',
                    'Splitting code into smaller chunks for better performance'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of React.memo?',
                'options': [
                    'To create memos',
                    'To delete memos',
                    'To update memos',
                    'To prevent unnecessary re-renders'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of useMemo?',
                'options': [
                    'To create memory',
                    'To delete memory',
                    'To manage memory',
                    'To memoize expensive calculations'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of useCallback?',
                'options': [
                    'To create callbacks',
                    'To delete callbacks',
                    'To update callbacks',
                    'To memoize callback functions'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of React.ErrorBoundary?',
                'options': [
                    'To create errors',
                    'To delete errors',
                    'To update errors',
                    'To catch and handle errors in component tree'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of React.StrictMode?',
                'options': [
                    'To create strict mode',
                    'To delete strict mode',
                    'To update strict mode',
                    'To identify potential problems in development'
                ],
                'correct_answer': 4
            },
        ]

    # Module 10 Questions - Integration
    def get_module10_questions(self):
        return [
            {
                'question': 'What is the most common way to make HTTP requests in React?',
                'options': [
                    'XMLHttpRequest only',
                    'jQuery only',
                    'WebSocket only',
                    'fetch API or axios'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is CORS?',
                'options': [
                    'Cross-Origin Request Sharing',
                    'Cross-Origin Response Sharing',
                    'Cross-Origin Resource Request',
                    'Cross-Origin Resource Sharing'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is axios?',
                'options': [
                    'A component library',
                    'A routing library',
                    'A styling library',
                    'Promise-based HTTP client library'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of useEffect for API calls?',
                'options': [
                    'To create API calls',
                    'To delete API calls',
                    'To update API calls',
                    'To fetch data when component mounts or updates'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of async/await in React?',
                'options': [
                    'To create async functions',
                    'To delete async functions',
                    'To update async functions',
                    'To handle asynchronous operations'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of loading states?',
                'options': [
                    'To create loading',
                    'To delete loading',
                    'To update loading',
                    'To show loading indicators during data fetching'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of error handling in API calls?',
                'options': [
                    'To create errors',
                    'To delete errors',
                    'To update errors',
                    'To handle and display errors'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of React Query?',
                'options': [
                    'To create queries',
                    'To delete queries',
                    'To update queries',
                    'To simplify data fetching and caching'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of SWR?',
                'options': [
                    'A component library',
                    'A routing library',
                    'A styling library',
                    'Data fetching library with caching and revalidation'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is the purpose of environment variables in React?',
                'options': [
                    'To create environments',
                    'To delete environments',
                    'To update environments',
                    'To store configuration values'
                ],
                'correct_answer': 4
            },
        ]

