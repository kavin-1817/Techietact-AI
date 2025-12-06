"""
Management command to ensure every quiz has at least 10 questions
Run with: python manage.py ensure_min_quiz_questions
"""
import re
import random
from django.core.management.base import BaseCommand
from django.db.models import Max
from learning.models import Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Ensures every quiz has at least 10 questions by generating questions based on module content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-questions',
            type=int,
            default=10,
            help='Minimum number of questions required (default: 10)',
        )

    def handle(self, *args, **options):
        min_questions = options['min_questions']
        
        # Get all quizzes
        quizzes = Quiz.objects.select_related('module', 'module__course').all()
        
        if not quizzes.exists():
            self.stdout.write(self.style.WARNING('No quizzes found in the database.'))
            return
        
        total_quizzes_updated = 0
        total_questions_added = 0
        
        for quiz in quizzes:
            current_question_count = quiz.questions.count()
            
            if current_question_count < min_questions:
                questions_needed = min_questions - current_question_count
                self.stdout.write(
                    self.style.WARNING(
                        f'Quiz "{quiz.title}" (Module: {quiz.module.title if quiz.module else "N/A"}) '
                        f'has only {current_question_count} questions. Generating {questions_needed} questions...'
                    )
                )
                
                # Get the highest order number for existing questions
                max_order = quiz.questions.aggregate(Max('order'))['order__max'] or 0
                
                # Generate questions based on module content
                generated_questions = self.generate_questions(quiz, questions_needed)
                
                # Add generated questions
                for i, question_data in enumerate(generated_questions):
                    question_order = max_order + i + 1
                    
                    # Create question
                    question = QuizQuestion.objects.create(
                        quiz=quiz,
                        question_text=question_data['question'],
                        question_type='multiple_choice',
                        points=1,
                        order=question_order
                    )
                    
                    # Create options
                    for opt_num, option_text in enumerate(question_data['options'], start=1):
                        is_correct = (opt_num == question_data['correct_answer'])
                        QuizOption.objects.create(
                            question=question,
                            option_text=option_text,
                            is_correct=is_correct,
                            order=opt_num
                        )
                    
                    total_questions_added += 1
                
                total_quizzes_updated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Generated {questions_needed} questions for quiz "{quiz.title}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Quiz "{quiz.title}" (Module: {quiz.module.title if quiz.module else "N/A"}) '
                        f'has {current_question_count} questions (✓)'
                    )
                )
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  • Total quizzes checked: {quizzes.count()}')
        self.stdout.write(f'  • Quizzes updated: {total_quizzes_updated}')
        self.stdout.write(f'  • Total questions added: {total_questions_added}')
        self.stdout.write('='*60)

    def generate_questions(self, quiz, count):
        """Generate questions based on module content"""
        module = quiz.module
        if not module:
            return self.generate_generic_questions(count)
        
        course = module.course
        category = course.category if course else 'other'
        course_title = course.title if course else ''
        
        # Extract content from module
        title = module.title
        summary = module.summary
        topics = module.topics.split('\n') if module.topics else []
        learning_objectives = module.learning_objectives.split('\n') if module.learning_objectives else []
        
        # Filter out empty strings
        topics = [t.strip() for t in topics if t.strip()]
        learning_objectives = [lo.strip() for lo in learning_objectives if lo.strip()]
        
        # Generate questions based on category
        questions = []
        
        if category == 'programming':
            questions = self.generate_programming_questions(
                title, summary, topics, learning_objectives, count, course_title
            )
        elif category == 'language':
            questions = self.generate_language_questions(
                title, summary, topics, learning_objectives, count, course_title
            )
        elif category == 'math':
            questions = self.generate_math_questions(
                title, summary, topics, learning_objectives, count
            )
        elif category == 'science':
            questions = self.generate_science_questions(
                title, summary, topics, learning_objectives, count
            )
        else:
            questions = self.generate_generic_questions(
                title, summary, topics, learning_objectives, count
            )
        
        return questions[:count]  # Ensure we return exactly the requested count

    def generate_programming_questions(self, title, summary, topics, learning_objectives, count, course_title):
        """Generate programming-related questions"""
        questions = []
        main_concept = self.extract_main_concept(title)
        
        # Question 1: About the main concept
        if main_concept and main_concept != 'this topic':
            questions.append({
                'question': f'What is the primary purpose of {main_concept}?',
                'options': [
                    summary[:120] + '...' if len(summary) > 120 else summary or f'To implement {main_concept.lower()} functionality',
                    f'To replace {main_concept.lower()} with alternatives',
                    f'To remove {main_concept.lower()} from the system',
                    f'To ignore {main_concept.lower()} completely'
                ],
                'correct_answer': 1
            })
        
        # Questions from topics
        topic_questions = []
        for topic in topics[:min(7, len(topics))]:
            if topic and len(topic.strip()) > 3:
                clean_topic = topic.strip()
                # Create question about the topic
                topic_questions.append({
                    'question': f'What is {clean_topic} used for?',
                    'options': [
                        f'To implement {clean_topic.lower()} functionality',
                        f'To replace {clean_topic.lower()}',
                        f'To remove {clean_topic.lower()}',
                        f'To ignore {clean_topic.lower()}'
                    ],
                    'correct_answer': 1
                })
                
                # Create definition question
                topic_questions.append({
                    'question': f'Which statement best describes {clean_topic}?',
                    'options': [
                        f'{clean_topic} is a key concept in {course_title or "programming"}',
                        f'{clean_topic} is not used in programming',
                        f'{clean_topic} is only for beginners',
                        f'{clean_topic} is outdated'
                    ],
                    'correct_answer': 1
                })
        
        questions.extend(topic_questions)
        
        # Questions from learning objectives
        for lo in learning_objectives[:min(5, len(learning_objectives))]:
            if lo and len(lo.strip()) > 10:
                clean_lo = lo.strip()
                # Extract key terms
                key_terms = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+\b', clean_lo)
                if key_terms:
                    main_term = key_terms[0] if key_terms else 'concepts'
                    questions.append({
                        'question': f'Which of the following is related to "{clean_lo[:60]}..."?',
                        'options': [
                            f'Understanding {main_term.lower()}',
                            f'Avoiding {main_term.lower()}',
                            f'Replacing {main_term.lower()}',
                            f'Ignoring {main_term.lower()}'
                        ],
                        'correct_answer': 1
                    })
        
        # Fill with generic programming questions if needed
        generic_templates = [
            {
                'question': f'In {course_title or "programming"}, what is a best practice?',
                'options': [
                    'Writing clean and readable code',
                    'Using complex code structures',
                    'Avoiding comments',
                    'Ignoring error handling'
                ],
                'correct_answer': 1
            },
            {
                'question': f'What is important when working with {main_concept}?',
                'options': [
                    'Understanding the fundamentals',
                    'Memorizing all syntax',
                    'Avoiding practice',
                    'Skipping examples'
                ],
                'correct_answer': 1
            },
            {
                'question': f'Which approach is recommended for learning {main_concept}?',
                'options': [
                    'Practice with hands-on exercises',
                    'Only reading documentation',
                    'Avoiding code examples',
                    'Skipping fundamentals'
                ],
                'correct_answer': 1
            }
        ]
        
        while len(questions) < count:
            template = random.choice(generic_templates)
            questions.append(template)
        
        return questions[:count]

    def generate_language_questions(self, title, summary, topics, learning_objectives, count, course_title):
        """Generate language learning questions"""
        questions = []
        main_concept = self.extract_main_concept(title)
        
        # Questions from topics
        for topic in topics[:min(5, len(topics))]:
            if topic and len(topic.strip()) > 3:
                clean_topic = topic.strip()
                questions.append({
                    'question': f'What is the correct usage of {clean_topic}?',
                    'options': [
                        f'Proper grammatical form of {clean_topic.lower()}',
                        f'Incorrect form 1',
                        f'Incorrect form 2',
                        f'Incorrect form 3'
                    ],
                    'correct_answer': 1
                })
        
        # Questions from learning objectives
        for lo in learning_objectives[:min(5, len(learning_objectives))]:
            if lo and len(lo.strip()) > 10:
                clean_lo = lo.strip()
                questions.append({
                    'question': f'Which statement relates to "{clean_lo[:60]}..."?',
                    'options': [
                        f'Understanding {clean_lo.lower()[:40]}',
                        f'Avoiding {clean_lo.lower()[:40]}',
                        f'Replacing {clean_lo.lower()[:40]}',
                        f'Ignoring {clean_lo.lower()[:40]}'
                    ],
                    'correct_answer': 1
                })
        
        # Fill with generic language questions
        generic_templates = [
            {
                'question': f'What is important when learning {main_concept}?',
                'options': [
                    'Understanding grammar rules',
                    'Memorizing without practice',
                    'Avoiding examples',
                    'Skipping fundamentals'
                ],
                'correct_answer': 1
            },
            {
                'question': f'Which approach helps in mastering {main_concept}?',
                'options': [
                    'Regular practice and application',
                    'Only reading theory',
                    'Avoiding exercises',
                    'Skipping practice'
                ],
                'correct_answer': 1
            }
        ]
        
        while len(questions) < count:
            template = random.choice(generic_templates)
            questions.append(template)
        
        return questions[:count]

    def generate_math_questions(self, title, summary, topics, learning_objectives, count):
        """Generate mathematics questions"""
        questions = []
        main_concept = self.extract_main_concept(title)
        
        # Questions from topics
        for topic in topics[:min(5, len(topics))]:
            if topic and len(topic.strip()) > 3:
                clean_topic = topic.strip()
                questions.append({
                    'question': f'What is a key concept in {clean_topic}?',
                    'options': [
                        f'Understanding {clean_topic.lower()} principles',
                        f'Avoiding {clean_topic.lower()}',
                        f'Replacing {clean_topic.lower()}',
                        f'Ignoring {clean_topic.lower()}'
                    ],
                    'correct_answer': 1
                })
        
        # Fill with generic math questions
        while len(questions) < count:
            questions.append({
                'question': f'What is important when working with {main_concept}?',
                'options': [
                    'Understanding the mathematical principles',
                    'Memorizing formulas only',
                    'Avoiding practice problems',
                    'Skipping examples'
                ],
                'correct_answer': 1
            })
        
        return questions[:count]

    def generate_science_questions(self, title, summary, topics, learning_objectives, count):
        """Generate science questions"""
        questions = []
        main_concept = self.extract_main_concept(title)
        
        # Questions from topics
        for topic in topics[:min(5, len(topics))]:
            if topic and len(topic.strip()) > 3:
                clean_topic = topic.strip()
                questions.append({
                    'question': f'What is the main principle behind {clean_topic}?',
                    'options': [
                        f'Understanding {clean_topic.lower()} concepts',
                        f'Avoiding {clean_topic.lower()}',
                        f'Replacing {clean_topic.lower()}',
                        f'Ignoring {clean_topic.lower()}'
                    ],
                    'correct_answer': 1
                })
        
        # Fill with generic science questions
        while len(questions) < count:
            questions.append({
                'question': f'What is important when studying {main_concept}?',
                'options': [
                    'Understanding scientific principles',
                    'Memorizing facts only',
                    'Avoiding experiments',
                    'Skipping observations'
                ],
                'correct_answer': 1
            })
        
        return questions[:count]

    def generate_generic_questions(self, title, summary, topics, learning_objectives, count):
        """Generate generic questions when category is unknown"""
        questions = []
        main_concept = self.extract_main_concept(title)
        
        # Questions from topics
        for topic in topics[:min(5, len(topics))]:
            if topic and len(topic.strip()) > 3:
                clean_topic = topic.strip()
                questions.append({
                    'question': f'What is an important aspect of {clean_topic}?',
                    'options': [
                        f'Understanding {clean_topic.lower()} concepts',
                        f'Avoiding {clean_topic.lower()}',
                        f'Replacing {clean_topic.lower()}',
                        f'Ignoring {clean_topic.lower()}'
                    ],
                    'correct_answer': 1
                })
        
        # Fill with generic questions
        while len(questions) < count:
            questions.append({
                'question': f'What is important when learning about {main_concept}?',
                'options': [
                    'Understanding key concepts',
                    'Memorizing all details',
                    'Ignoring fundamentals',
                    'Skipping practice'
                ],
                'correct_answer': 1
            })
        
        return questions[:count]

    def extract_main_concept(self, text):
        """Extract main concept from text"""
        if not text:
            return 'this topic'
        
        # Remove common words
        common_words = ['introduction', 'to', 'the', 'of', 'and', 'or', 'in', 'on', 'at', 'for', 'with', 'about']
        words = [w for w in text.split() if w.lower() not in common_words and len(w) > 2]
        
        if words:
            # Return first significant word, capitalized
            return words[0].capitalize()
        
        return 'this topic'
