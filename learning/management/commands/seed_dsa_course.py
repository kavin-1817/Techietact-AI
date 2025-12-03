"""
Management command to seed Data Structures & Algorithms (DSA) course with complete modules and topics
Run with: python manage.py seed_dsa_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Data Structures & Algorithms (DSA) course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get DSA course
        course, created = Course.objects.get_or_create(
            title='DATA STRUCTURES & ALGORITHMS (DSA) – Course Structure',
            defaults={
                'description': 'Complete Data Structures & Algorithms course covering linear data structures, searching algorithms, sorting algorithms, and graph algorithms.',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Data Structures & Algorithms (DSA) course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data"""
        return [
            {
                'order': 1,
                'title': 'Linear Data Structures',
                'summary': 'Learn to implement fundamental linear data structures including ArrayList, String, Stack, Queue, and Linked List.',
                'learning_objectives': 'Implement ArrayList data structure\nImplement String data structure\nImplement Stack data structure\nImplement Queue data structure\nImplement Linked List data structure\nUnderstand operations and time complexity of each data structure',
                'topics': 'ArrayList implementation\nString implementation\nStack implementation\nQueue implementation\nLinked List implementation',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Searching Algorithms',
                'summary': 'Master searching algorithms including Linear Search, Binary Search, and Ternary Search. Understand their time complexity and use cases.',
                'learning_objectives': 'Implement Linear Search algorithm\nImplement Binary Search algorithm\nImplement Ternary Search algorithm\nUnderstand time complexity of each algorithm\nKnow when to use each searching algorithm',
                'topics': 'Linear Search\nBinary Search\nTernary Search',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Sorting Algorithms',
                'summary': 'Learn essential sorting algorithms including Bubble Sort, Selection Sort, Merge Sort, and Quick Sort. Understand their efficiency and implementation.',
                'learning_objectives': 'Implement Bubble Sort algorithm\nImplement Selection Sort algorithm\nImplement Merge Sort algorithm\nImplement Quick Sort algorithm\nUnderstand time and space complexity of each algorithm\nKnow when to use each sorting algorithm',
                'topics': 'Bubble Sort\nSelection Sort\nMerge Sort\nQuick Sort',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Graph Algorithms',
                'summary': 'Master graph algorithms including Depth First Search (DFS), Breadth First Search (BFS), and Dijkstra\'s Shortest Path Algorithm.',
                'learning_objectives': 'Implement Depth First Search (DFS) algorithm\nImplement Breadth First Search (BFS) algorithm\nImplement Dijkstra\'s Shortest Path Algorithm\nUnderstand graph traversal techniques\nSolve problems using graph algorithms',
                'topics': 'Depth First Search (DFS)\nBreadth First Search (BFS)\nDijkstra\'s Shortest Path Algorithm',
                'questions': self.get_module4_questions(),
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

    # Module 1 Questions - Linear Data Structures
    def get_module1_questions(self):
        return [
            {
                'question': 'What is the time complexity of accessing an element in an ArrayList by index?',
                'options': [
                    'O(1)',
                    'O(n)',
                    'O(log n)',
                    'O(n²)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the principle of Stack data structure?',
                'options': [
                    'LIFO (Last In First Out)',
                    'FIFO (First In First Out)',
                    'Random access',
                    'Sorted order'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the principle of Queue data structure?',
                'options': [
                    'FIFO (First In First Out)',
                    'LIFO (Last In First Out)',
                    'Random access',
                    'Sorted order'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of inserting at the beginning of a Linked List?',
                'options': [
                    'O(1)',
                    'O(n)',
                    'O(log n)',
                    'O(n²)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which data structure is best for implementing a browser\'s back button?',
                'options': [
                    'Stack',
                    'Queue',
                    'Linked List',
                    'ArrayList'
                ],
                'correct_answer': 1
            },
        ]

    # Module 2 Questions - Searching Algorithms
    def get_module2_questions(self):
        return [
            {
                'question': 'What is the time complexity of Linear Search?',
                'options': [
                    'O(n)',
                    'O(log n)',
                    'O(1)',
                    'O(n²)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of Binary Search?',
                'options': [
                    'O(log n)',
                    'O(n)',
                    'O(1)',
                    'O(n²)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a prerequisite for Binary Search?',
                'options': [
                    'Array must be sorted',
                    'Array must be unsorted',
                    'Array must be empty',
                    'Array must have duplicates'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of Ternary Search?',
                'options': [
                    'O(log₃ n)',
                    'O(n)',
                    'O(log n)',
                    'O(n²)'
                ],
                'correct_answer': 1
            },
        ]

    # Module 3 Questions - Sorting Algorithms
    def get_module3_questions(self):
        return [
            {
                'question': 'What is the time complexity of Bubble Sort in worst case?',
                'options': [
                    'O(n²)',
                    'O(n log n)',
                    'O(n)',
                    'O(log n)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of Merge Sort?',
                'options': [
                    'O(n log n)',
                    'O(n²)',
                    'O(n)',
                    'O(log n)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of Quick Sort in average case?',
                'options': [
                    'O(n log n)',
                    'O(n²)',
                    'O(n)',
                    'O(log n)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sorting algorithm is stable?',
                'options': [
                    'Merge Sort',
                    'Quick Sort',
                    'Heap Sort',
                    'Selection Sort'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sorting algorithm has the best average time complexity?',
                'options': [
                    'Quick Sort',
                    'Bubble Sort',
                    'Selection Sort',
                    'Insertion Sort'
                ],
                'correct_answer': 1
            },
        ]

    # Module 4 Questions - Graph Algorithms
    def get_module4_questions(self):
        return [
            {
                'question': 'What data structure is typically used to implement DFS?',
                'options': [
                    'Stack',
                    'Queue',
                    'Heap',
                    'Tree'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What data structure is typically used to implement BFS?',
                'options': [
                    'Queue',
                    'Stack',
                    'Heap',
                    'Tree'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of BFS?',
                'options': [
                    'O(V + E)',
                    'O(V × E)',
                    'O(V²)',
                    'O(E²)'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is Dijkstra\'s algorithm used for?',
                'options': [
                    'Finding shortest path in weighted graphs',
                    'Finding longest path',
                    'Finding all paths',
                    'Finding cycles'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the time complexity of Dijkstra\'s algorithm using a binary heap?',
                'options': [
                    'O((V + E) log V)',
                    'O(V + E)',
                    'O(V²)',
                    'O(E²)'
                ],
                'correct_answer': 1
            },
        ]

