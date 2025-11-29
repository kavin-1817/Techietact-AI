"""
Management command to seed initial data
Run with: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module


class Command(BaseCommand):
    help = 'Seeds the database with sample courses'

    def handle(self, *args, **options):
        courses_data = [
            {
                'title': 'Software Engineering Foundations',
                'description': 'Learn core programming concepts that translate across languages like JavaScript, TypeScript, Python, and Java. Perfect for beginners who want to start building modern applications.',
                'category': 'programming',
                'is_featured': True,
            },
            {
                'title': 'Algebra Basics',
                'description': 'Master the basics of algebraic equations, linear equations, quadratic equations, and polynomial expressions. Build a strong foundation in mathematics.',
                'category': 'math',
                'is_featured': True,
            },
            {
                'title': 'Web Development Fundamentals',
                'description': 'Build modern web applications using HTML, CSS, and JavaScript. Learn responsive design, DOM manipulation, and modern web development practices.',
                'category': 'programming',
                'is_featured': True,
            },
            {
                'title': 'Introduction to Machine Learning',
                'description': 'Explore the world of machine learning, neural networks, and AI. Learn about supervised and unsupervised learning, and build your first ML models.',
                'category': 'science',
                'is_featured': True,
            },
            {
                'title': 'World History Overview',
                'description': 'Journey through major historical events, civilizations, and movements that shaped our world. From ancient civilizations to modern times.',
                'category': 'history',
                'is_featured': True,
            },
            {
                'title': 'English Grammar Essentials',
                'description': 'Improve your English grammar skills with comprehensive lessons on tenses, parts of speech, sentence structure, and common grammar rules.',
                'category': 'language',
                'is_featured': False,
            },
            {
                'title': 'Calculus Fundamentals',
                'description': 'Dive into the world of calculus with limits, derivatives, and integrals. Essential for students pursuing mathematics, physics, or engineering.',
                'category': 'math',
                'is_featured': False,
            },
        ]

        created_count = 0
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults=course_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created course: {course.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Course already exists: {course.title}')
                )
            create_modules_if_missing(course)

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully seeded {created_count} new courses!')
        )


def create_modules_if_missing(course):
    if course.modules.exists():
        return
    
    base_templates = [
        ('Foundations', 'Break down the fundamentals and vocabulary for this topic.', 'Key concepts\nSyntax essentials\nMini challenges'),
        ('Hands-on Practice', 'Write code to apply the foundational ideas in practical scenarios.', 'Guided exercises\nDebugging walkthroughs\nReview questions'),
        ('Deep Dive Concepts', 'Explore intermediate ideas that extend the basics and prepare you for complexity.', 'Advanced patterns\nCommon pitfalls\nOptimization tips'),
        ('Real-world Applications', 'Connect the theory to real-world scenarios and projects.', 'Use cases\nProject scaffolds\nTesting considerations'),
        ('Capstone & Review', 'Consolidate everything you have learned in this course module.', 'Recap quiz\nCapstone project\nNext steps'),
    ]

    module_templates = list(base_templates)
    if course.category == 'programming':
        module_templates.extend([
            (
                'Mini Project Playground',
                'Apply new concepts through short, high-feedback builds with clear briefs.',
                'Project briefs\nTooling setup\nRetrospectives'
            ),
            (
                'End-to-End Delivery Lab',
                'Connect APIs, storage, and automation to simulate production launches.',
                'Architecture docs\nTesting matrix\nDeployment playbooks'
            ),
            (
                'Interview Readiness Sprint',
                'Translate course outcomes into coding, system design, and behavioral prep.',
                'Problem sets\nMock prompts\nStory frameworks'
            ),
        ])
    
    for order, (title, summary, objectives) in enumerate(module_templates, start=1):
        Module.objects.create(
            course=course,
            order=order,
            title=title,
            summary=summary,
            learning_objectives=objectives,
            topics="Introduction\nGuided practice\nReflection"
        )
    if hasattr(course, '_prefetched_objects_cache'):
        course._prefetched_objects_cache.pop('modules', None)
