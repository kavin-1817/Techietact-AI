"""
Management command to seed Quantitative Aptitude course with complete modules and topics
Run with: python manage.py seed_quantitative_aptitude_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with Quantitative Aptitude course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get Quantitative Aptitude course
        course, created = Course.objects.get_or_create(
            title='QUANTITATIVE APTITUDE – Complete Course Structure',
            defaults={
                'description': 'Comprehensive Quantitative Aptitude course covering all fundamental and advanced concepts. Master number systems, arithmetic, algebra, geometry, data interpretation, probability, and placement exam patterns.',
                'category': 'aptitude',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated Quantitative Aptitude course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data with questions"""
        return [
            {
                'order': 1,
                'title': 'Number System & Basic Mathematics',
                'summary': 'Master the fundamentals of number systems, divisibility rules, LCM & HCF, factors, remainders, and basic mathematical operations.',
                'learning_objectives': 'Understand types of numbers\nMaster divisibility rules\nLearn LCM & HCF concepts\nUnderstand factors & multiples\nSolve remainder problems\nLearn digital sums\nMaster unit digit & last digit concepts\nApply simplification & approximation\nUnderstand BODMAS rules\nWork with fractions & decimals',
                'topics': 'Types of numbers\nDivisibility rules\nLCM & HCF\nFactors & multiples\nRemainders\nDigital sums\nUnit digit & last digit concepts\nSimplification & approximation\nBODMAS rules\nFractions & decimals',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Arithmetic – Fundamentals',
                'summary': 'Learn fundamental arithmetic concepts including ratio & proportion, percentage, averages, profit & loss, interest calculations, partnership, and time & work.',
                'learning_objectives': 'Master ratio & proportion\nCalculate percentages effectively\nUnderstand averages\nSolve profit, loss & discount problems\nCalculate simple & compound interest\nUnderstand partnership concepts\nLearn mixture & alligation\nSolve time & work problems\nMaster pipes & cisterns problems',
                'topics': 'Ratio & proportion\nPercentage\nAverages\nProfit, loss & discount\nSimple interest\nCompound interest\nPartnership\nMixture & alligation\nTime & work\nPipes & cisterns',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Speed, Time & Distance',
                'summary': 'Master speed, time, and distance problems including relative speed, trains, boats & streams, races, and circular tracks.',
                'learning_objectives': 'Understand basic formula conversions\nCalculate relative speed\nSolve train problems\nMaster boats & streams problems\nSolve races & games problems\nUnderstand circular tracks\nWork with time zones',
                'topics': 'Basic formula conversions\nRelative speed\nTrains problems\nBoats & streams\nRaces & games\nCircular tracks\nTime zones',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Algebra',
                'summary': 'Learn algebraic concepts including linear equations, quadratic equations, inequalities, surds, indices, polynomials, and algebraic identities.',
                'learning_objectives': 'Solve linear equations\nMaster quadratic equations\nUnderstand inequalities\nWork with surds & indices\nLearn polynomials\nApply algebraic identities',
                'topics': 'Linear equations\nQuadratic equations\nInequalities\nSurds & indices\nPolynomials\nAlgebraic identities',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Geometry & Mensuration',
                'summary': 'Master geometry fundamentals and mensuration including 2D and 3D shapes, area, perimeter, volume, and surface area calculations.',
                'learning_objectives': 'Understand points, lines, angles\nLearn triangle properties\nMaster circle concepts\nUnderstand quadrilaterals & polygons\nCalculate area & perimeter of 2D shapes\nCalculate volume & surface area of 3D shapes\nWork with cubes, cuboids, cylinders, cones, spheres\nUnderstand frustum',
                'topics': 'Points, lines, angles\nTriangles (properties, similarity, congruence)\nCircles (chords, tangents, arcs)\nQuadrilaterals\nPolygons\nArea & perimeter (2D shapes)\nVolume & surface area (3D shapes)\nCubes, cuboids, cylinders, cones, spheres\nFrustum',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Data Interpretation (DI)',
                'summary': 'Master data interpretation skills including tables, bar charts, line charts, pie charts, caselet DI, and mixed graphs.',
                'learning_objectives': 'Interpret tables\nRead bar charts effectively\nAnalyze line charts\nUnderstand pie charts\nSolve caselet DI problems\nWork with mixed graphs\nHandle missing DI\nSolve percentage-based DI\nMaster ratio-based DI',
                'topics': 'Tables\nBar charts\nLine charts\nPie charts\nCaselet DI\nMixed graphs\nMissing DI\nPercentage-based DI\nRatio-based DI',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Probability & Combinatorics',
                'summary': 'Learn probability and combinatorics including basic probability, permutations, combinations, and probability puzzles.',
                'learning_objectives': 'Understand basic probability\nLearn independent events\nMaster conditional probability\nSolve permutation problems\nCalculate combinations\nUnderstand circular permutations\nSolve probability puzzles',
                'topics': 'Basic probability\nIndependent events\nConditional probability\nPermutations\nCombinations\nCircular permutations\nProbability puzzles',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Logical Quantitative Applications',
                'summary': 'Apply quantitative skills to logical problems including ages, clocks, calendars, directions, and number-based puzzles.',
                'learning_objectives': 'Solve age-related problems\nWork with clock problems\nUnderstand calendar problems\nSolve direction problems\nMaster number-based puzzles\nLearn coding-decoding (number-based)\nUnderstand binary operations',
                'topics': 'Ages\nClocks\nCalendars\nDirections\nPuzzles based on numbers\nCoding-decoding (number-based)\nBinary operations',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Advanced Aptitude',
                'summary': 'Learn advanced aptitude concepts including logarithms, set theory, functions, coordinate geometry, matrices, and Venn diagrams.',
                'learning_objectives': 'Master logarithms\nUnderstand set theory\nLearn functions & graphs\nUnderstand coordinate geometry basics\nLearn matrices basics\nWork with Venn diagrams',
                'topics': 'Logarithms\nSet theory\nFunctions & graphs\nCoordinate geometry basics\nMatrices basics\nVenn diagrams',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Placement & Exam-Focused Practice',
                'summary': 'Prepare for placement exams and competitive tests with pattern-specific practice for TCS NQT, Infosys, Wipro, Capgemini, Bank exams, and SSC.',
                'learning_objectives': 'Understand TCS NQT aptitude pattern\nMaster Infosys aptitude pattern\nLearn Wipro/Capgemini pattern\nPrepare for Bank exam aptitude pattern\nUnderstand SSC aptitude pattern\nPractice mixed model tests\nImprove speed with drills',
                'topics': 'TCS NQT aptitude pattern\nInfosys aptitude pattern\nWipro/Capgemini pattern\nBank exam aptitude pattern\nSSC aptitude pattern\nMixed model tests\nSpeed improvement drills',
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

    # Module 1 Questions - Number System & Basic Mathematics
    def get_module1_questions(self):
        return [
            {
                'question': 'What is the LCM of 12 and 18?',
                'options': ['18', '36', '24', '12'],
                'correct_answer': 2
            },
            {
                'question': 'What is the HCF of 24 and 36?',
                'options': ['12', '24', '6', '18'],
                'correct_answer': 1
            },
            {
                'question': 'What is the unit digit of 7^25?',
                'options': ['7', '9', '3', '1'],
                'correct_answer': 1
            },
            {
                'question': 'Which of the following is divisible by 3?',
                'options': ['1234', '5678', '2345', '3456'],
                'correct_answer': 4
            },
            {
                'question': 'What is the remainder when 100 is divided by 7?',
                'options': ['1', '2', '3', '4'],
                'correct_answer': 2
            },
        ]

    # Module 2 Questions - Arithmetic – Fundamentals
    def get_module2_questions(self):
        return [
            {
                'question': 'If the ratio of A to B is 3:4 and B to C is 5:6, what is the ratio of A to C?',
                'options': ['5:8', '15:24', '3:6', '5:6'],
                'correct_answer': 1
            },
            {
                'question': 'What is 25% of 200?',
                'options': ['40', '50', '60', '75'],
                'correct_answer': 2
            },
            {
                'question': 'The average of 5 numbers is 20. If one number is removed, the average becomes 18. What is the removed number?',
                'options': ['26', '28', '30', '32'],
                'correct_answer': 2
            },
            {
                'question': 'A shopkeeper sells an item at 20% profit. If the cost price is Rs. 500, what is the selling price?',
                'options': ['Rs. 550', 'Rs. 600', 'Rs. 650', 'Rs. 700'],
                'correct_answer': 2
            },
            {
                'question': 'What is the simple interest on Rs. 1000 at 10% per annum for 2 years?',
                'options': ['Rs. 100', 'Rs. 200', 'Rs. 300', 'Rs. 400'],
                'correct_answer': 2
            },
        ]

    # Module 3 Questions - Speed, Time & Distance
    def get_module3_questions(self):
        return [
            {
                'question': 'A train 150m long passes a platform 300m long in 18 seconds. What is the speed of the train?',
                'options': ['90 km/h', '100 km/h', '110 km/h', '120 km/h'],
                'correct_answer': 1
            },
            {
                'question': 'A boat goes 30 km upstream in 2 hours and 40 km downstream in 2 hours. What is the speed of the boat in still water?',
                'options': ['15 km/h', '17.5 km/h', '20 km/h', '22.5 km/h'],
                'correct_answer': 2
            },
            {
                'question': 'Two trains are moving in opposite directions at 60 km/h and 40 km/h. What is their relative speed?',
                'options': ['20 km/h', '100 km/h', '80 km/h', '120 km/h'],
                'correct_answer': 2
            },
            {
                'question': 'A person covers a certain distance at 40 km/h and returns at 60 km/h. What is the average speed?',
                'options': ['48 km/h', '50 km/h', '52 km/h', '55 km/h'],
                'correct_answer': 1
            },
            {
                'question': 'How long will it take to cover 120 km at a speed of 60 km/h?',
                'options': ['1 hour', '2 hours', '3 hours', '4 hours'],
                'correct_answer': 2
            },
        ]

    # Module 4 Questions - Algebra
    def get_module4_questions(self):
        return [
            {
                'question': 'If 2x + 3 = 11, what is the value of x?',
                'options': ['2', '3', '4', '5'],
                'correct_answer': 3
            },
            {
                'question': 'What are the roots of the quadratic equation x² - 5x + 6 = 0?',
                'options': ['2 and 3', '1 and 6', '2 and 4', '3 and 4'],
                'correct_answer': 1
            },
            {
                'question': 'If a² - b² = 16 and a - b = 4, what is a + b?',
                'options': ['2', '4', '6', '8'],
                'correct_answer': 2
            },
            {
                'question': 'What is the value of (a + b)²?',
                'options': ['a² + b²', 'a² + 2ab + b²', 'a² - 2ab + b²', 'a² + ab + b²'],
                'correct_answer': 2
            },
            {
                'question': 'If 3^x = 27, what is the value of x?',
                'options': ['2', '3', '4', '5'],
                'correct_answer': 2
            },
        ]

    # Module 5 Questions - Geometry & Mensuration
    def get_module5_questions(self):
        return [
            {
                'question': 'What is the area of a circle with radius 7 cm? (Use π = 22/7)',
                'options': ['154 cm²', '44 cm²', '88 cm²', '176 cm²'],
                'correct_answer': 1
            },
            {
                'question': 'What is the area of a triangle with base 10 cm and height 8 cm?',
                'options': ['40 cm²', '50 cm²', '60 cm²', '80 cm²'],
                'correct_answer': 1
            },
            {
                'question': 'What is the volume of a cube with side 5 cm?',
                'options': ['125 cm³', '100 cm³', '150 cm³', '200 cm³'],
                'correct_answer': 1
            },
            {
                'question': 'What is the surface area of a cube with side 4 cm?',
                'options': ['64 cm²', '96 cm²', '128 cm²', '144 cm²'],
                'correct_answer': 2
            },
            {
                'question': 'What is the area of a rectangle with length 12 cm and breadth 8 cm?',
                'options': ['80 cm²', '96 cm²', '100 cm²', '120 cm²'],
                'correct_answer': 2
            },
        ]

    # Module 6 Questions - Data Interpretation (DI)
    def get_module6_questions(self):
        return [
            {
                'question': 'In a pie chart, if a sector represents 25% of the total, what is the angle of that sector?',
                'options': ['45°', '60°', '90°', '120°'],
                'correct_answer': 3
            },
            {
                'question': 'If a bar chart shows sales of Rs. 5000 for January, and the scale is 1 cm = Rs. 1000, how tall should the bar be?',
                'options': ['3 cm', '4 cm', '5 cm', '6 cm'],
                'correct_answer': 3
            },
            {
                'question': 'In a line graph, if the line goes upward from left to right, what does it indicate?',
                'options': ['Decreasing trend', 'Increasing trend', 'No change', 'Fluctuating trend'],
                'correct_answer': 2
            },
            {
                'question': 'If a table shows 30% increase from year 1 to year 2, and the value in year 1 is 100, what is the value in year 2?',
                'options': ['120', '130', '140', '150'],
                'correct_answer': 2
            },
            {
                'question': 'In a caselet DI, if total students are 200 and 40% are girls, how many are boys?',
                'options': ['80', '100', '120', '160'],
                'correct_answer': 3
            },
        ]

    # Module 7 Questions - Probability & Combinatorics
    def get_module7_questions(self):
        return [
            {
                'question': 'What is the probability of getting a head when tossing a fair coin?',
                'options': ['0.25', '0.5', '0.75', '1'],
                'correct_answer': 2
            },
            {
                'question': 'In how many ways can 3 people be arranged in a line?',
                'options': ['3', '6', '9', '12'],
                'correct_answer': 2
            },
            {
                'question': 'What is the number of ways to choose 2 items from 5 items?',
                'options': ['5', '10', '15', '20'],
                'correct_answer': 2
            },
            {
                'question': 'What is the probability of drawing an ace from a standard deck of 52 cards?',
                'options': ['1/13', '1/26', '1/52', '4/52'],
                'correct_answer': 1
            },
            {
                'question': 'In how many ways can 4 people sit around a circular table?',
                'options': ['6', '12', '24', '120'],
                'correct_answer': 1
            },
        ]

    # Module 8 Questions - Logical Quantitative Applications
    def get_module8_questions(self):
        return [
            {
                'question': 'If the present age of father is 40 years and son is 10 years, what will be the ratio of their ages after 5 years?',
                'options': ['3:1', '4:1', '5:1', '6:1'],
                'correct_answer': 1
            },
            {
                'question': 'At what time between 2 and 3 o\'clock will the hands of a clock be together?',
                'options': ['2:10', '2:11', '2:12', '2:13'],
                'correct_answer': 2
            },
            {
                'question': 'If January 1, 2024 is a Monday, what day will January 1, 2025 be?',
                'options': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
                'correct_answer': 3
            },
            {
                'question': 'A person walks 10 km North, then 5 km East. How far is he from the starting point?',
                'options': ['5√5 km', '10 km', '15 km', '5√13 km'],
                'correct_answer': 4
            },
            {
                'question': 'If in a number puzzle, 5 + 3 = 28, 9 + 1 = 810, what is 7 + 5?',
                'options': ['212', '122', '221', '112'],
                'correct_answer': 1
            },
        ]

    # Module 9 Questions - Advanced Aptitude
    def get_module9_questions(self):
        return [
            {
                'question': 'What is log₁₀(100)?',
                'options': ['1', '2', '10', '100'],
                'correct_answer': 2
            },
            {
                'question': 'If A = {1, 2, 3} and B = {3, 4, 5}, what is A ∩ B?',
                'options': ['{1, 2, 3, 4, 5}', '{3}', '{1, 2}', '{4, 5}'],
                'correct_answer': 2
            },
            {
                'question': 'What is the value of log₂(8)?',
                'options': ['2', '3', '4', '8'],
                'correct_answer': 2
            },
            {
                'question': 'If A = {1, 2, 3} and B = {3, 4, 5}, what is A ∪ B?',
                'options': ['{1, 2, 3, 4, 5}', '{3}', '{1, 2}', '{4, 5}'],
                'correct_answer': 1
            },
            {
                'question': 'In a Venn diagram, if 20 students like Math, 25 like Science, and 10 like both, how many students are there in total?',
                'options': ['35', '45', '55', '65'],
                'correct_answer': 1
            },
        ]

    # Module 10 Questions - Placement & Exam-Focused Practice
    def get_module10_questions(self):
        return [
            {
                'question': 'In TCS NQT pattern, what is typically the time limit for the Quantitative Aptitude section?',
                'options': ['20 minutes', '30 minutes', '40 minutes', '50 minutes'],
                'correct_answer': 3
            },
            {
                'question': 'Infosys aptitude test usually focuses on which type of problems?',
                'options': ['Only algebra', 'Only geometry', 'Mixed quantitative problems', 'Only data interpretation'],
                'correct_answer': 3
            },
            {
                'question': 'For speed improvement in aptitude tests, what is the recommended approach?',
                'options': ['Solve all questions slowly', 'Skip difficult questions', 'Practice with time limits', 'Only attempt easy questions'],
                'correct_answer': 3
            },
            {
                'question': 'Bank exam aptitude pattern typically includes questions on:',
                'options': ['Only arithmetic', 'Only data interpretation', 'Mixed topics including arithmetic, DI, and reasoning', 'Only algebra'],
                'correct_answer': 3
            },
            {
                'question': 'SSC aptitude pattern usually has how many questions in the quantitative section?',
                'options': ['20-25', '25-30', '30-35', '35-40'],
                'correct_answer': 2
            },
        ]

