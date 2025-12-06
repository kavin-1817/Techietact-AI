"""
Management command to seed English Communication course with modules and quizzes
Run with: python manage.py seed_english_course
"""
from django.core.management.base import BaseCommand
from learning.models import Course, Module, Quiz, QuizQuestion, QuizOption


class Command(BaseCommand):
    help = 'Seeds the database with English Communication course, modules, and quizzes with MCQ questions'

    def handle(self, *args, **options):
        # Create or get English Communication course
        course, created = Course.objects.get_or_create(
            title='English Communication Mastery',
            defaults={
                'description': 'Master English grammar from basics to advanced level and develop fluent speaking skills. This comprehensive course covers all aspects of English communication including grammar rules, sentence structure, tenses, vocabulary, pronunciation, and conversation skills to help you speak English confidently and fluently.',
                'category': 'language',
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
            self.style.SUCCESS(f'\nSuccessfully created/updated English Communication course with {len(modules_data)} modules and {total_questions} total questions!')
        )

    def get_modules_data(self):
        """Returns comprehensive module data with questions"""
        return [
            {
                'order': 1,
                'title': 'Parts of Speech and Basic Grammar',
                'summary': 'Learn the fundamental building blocks of English grammar. Understand nouns, verbs, adjectives, adverbs, pronouns, prepositions, conjunctions, and interjections.',
                'learning_objectives': 'Identify and use all eight parts of speech correctly\nUnderstand the function of each part of speech in sentences\nRecognize common grammar mistakes\nBuild a strong foundation for advanced grammar',
                'topics': 'Nouns (Common, Proper, Collective, Abstract)\nVerbs (Action, Linking, Helping)\nAdjectives and Adverbs\nPronouns (Personal, Possessive, Reflexive)\nPrepositions and Prepositional Phrases\nConjunctions (Coordinating, Subordinating)\nInterjections\nBasic Sentence Structure',
                'questions': self.get_module1_questions(),
            },
            {
                'order': 2,
                'title': 'Tenses: Present, Past, and Future',
                'summary': 'Master all English tenses including simple, continuous, perfect, and perfect continuous forms. Learn when and how to use each tense correctly.',
                'learning_objectives': 'Use all 12 tenses correctly in context\nUnderstand the difference between simple, continuous, perfect, and perfect continuous\nChoose the appropriate tense based on time and context\nAvoid common tense-related errors',
                'topics': 'Present Tenses (Simple, Continuous, Perfect, Perfect Continuous)\nPast Tenses (Simple, Continuous, Perfect, Perfect Continuous)\nFuture Tenses (Simple, Continuous, Perfect, Perfect Continuous)\nTime Expressions and Signal Words\nTense Consistency in Writing\nCommon Tense Mistakes',
                'questions': self.get_module2_questions(),
            },
            {
                'order': 3,
                'title': 'Sentence Structure and Types',
                'summary': 'Learn to construct proper sentences. Understand simple, compound, complex, and compound-complex sentences. Master subject-verb agreement and sentence patterns.',
                'learning_objectives': 'Construct grammatically correct sentences\nUnderstand different sentence types and structures\nMaintain subject-verb agreement\nIdentify and fix sentence fragments and run-ons',
                'topics': 'Simple Sentences\nCompound Sentences\nComplex Sentences\nCompound-Complex Sentences\nSubject-Verb Agreement\nSentence Patterns (SVO, SVC, etc.)\nSentence Fragments and Run-ons\nParallel Structure',
                'questions': self.get_module3_questions(),
            },
            {
                'order': 4,
                'title': 'Articles, Determiners, and Quantifiers',
                'summary': 'Master the use of articles (a, an, the), determiners, and quantifiers. Learn when to use each and avoid common mistakes.',
                'learning_objectives': 'Use articles (a, an, the) correctly\nUnderstand countable and uncountable nouns\nChoose appropriate determiners and quantifiers\nAvoid common article-related errors',
                'topics': 'Definite Article (the)\nIndefinite Articles (a, an)\nZero Article\nCountable vs Uncountable Nouns\nDeterminers (this, that, these, those)\nQuantifiers (some, any, many, much, few, little)\nCommon Article Mistakes',
                'questions': self.get_module4_questions(),
            },
            {
                'order': 5,
                'title': 'Modal Verbs and Conditionals',
                'summary': 'Learn to use modal verbs (can, could, may, might, must, should, etc.) and conditional sentences (if clauses) effectively.',
                'learning_objectives': 'Use modal verbs to express ability, possibility, obligation, and permission\nConstruct all types of conditional sentences\nUnderstand the difference between real and unreal conditionals\nExpress degrees of certainty and politeness',
                'topics': 'Modal Verbs (can, could, may, might, must, should, would, will)\nModal Verbs for Ability, Permission, Obligation\nZero, First, Second, Third Conditionals\nMixed Conditionals\nWishes and Regrets\nPolite Requests and Suggestions',
                'questions': self.get_module5_questions(),
            },
            {
                'order': 6,
                'title': 'Active and Passive Voice',
                'summary': 'Understand the difference between active and passive voice. Learn when to use each and how to transform sentences between voices.',
                'learning_objectives': 'Identify active and passive voice\nTransform sentences between active and passive\nChoose the appropriate voice based on context\nUnderstand when passive voice is preferred',
                'topics': 'Active Voice Structure\nPassive Voice Structure\nForming Passive Voice in All Tenses\nWhen to Use Passive Voice\nBy-phrase and Agent\nCommon Passive Voice Mistakes\nActive vs Passive in Writing',
                'questions': self.get_module6_questions(),
            },
            {
                'order': 7,
                'title': 'Direct and Indirect Speech',
                'summary': 'Learn to report what others have said. Master the rules of converting direct speech to indirect speech with proper tense changes.',
                'learning_objectives': 'Convert direct speech to indirect speech\nApply proper tense changes in reported speech\nUse appropriate reporting verbs\nReport questions, commands, and statements correctly',
                'topics': 'Direct Speech vs Indirect Speech\nTense Changes in Reported Speech\nReporting Statements\nReporting Questions (Yes/No and Wh-questions)\nReporting Commands and Requests\nTime and Place Changes\nReporting Verbs (say, tell, ask, etc.)',
                'questions': self.get_module7_questions(),
            },
            {
                'order': 8,
                'title': 'Vocabulary Building and Word Formation',
                'summary': 'Expand your vocabulary systematically. Learn word formation, prefixes, suffixes, synonyms, antonyms, and idioms.',
                'learning_objectives': 'Build a strong vocabulary foundation\nUnderstand word formation processes\nUse synonyms and antonyms effectively\nLearn common idioms and phrasal verbs',
                'topics': 'Word Formation (Prefixes, Suffixes, Root Words)\nSynonyms and Antonyms\nIdioms and Expressions\nPhrasal Verbs\nCollocations\nContext Clues for Vocabulary\nWord Families\nAcademic and Formal Vocabulary',
                'questions': self.get_module8_questions(),
            },
            {
                'order': 9,
                'title': 'Pronunciation and Speaking Skills',
                'summary': 'Improve your pronunciation and develop speaking confidence. Learn stress patterns, intonation, and common pronunciation rules.',
                'learning_objectives': 'Pronounce English sounds correctly\nUnderstand stress and intonation patterns\nSpeak with confidence and clarity\nOvercome common pronunciation challenges',
                'topics': 'English Phonetics and Phonemes\nWord Stress and Sentence Stress\nIntonation Patterns\nCommon Pronunciation Rules\nSilent Letters\nHomophones and Homographs\nSpeaking Practice Techniques\nBuilding Speaking Confidence',
                'questions': self.get_module9_questions(),
            },
            {
                'order': 10,
                'title': 'Conversation Skills and Fluency Development',
                'summary': 'Develop fluent conversation skills. Learn to engage in natural conversations, express opinions, agree/disagree, and maintain engaging dialogues.',
                'learning_objectives': 'Engage in natural English conversations\nExpress opinions and ideas clearly\nUse conversation fillers and connectors\nDevelop fluency through practice',
                'topics': 'Starting and Maintaining Conversations\nExpressing Opinions and Agreeing/Disagreeing\nAsking for Clarification and Repetition\nConversation Fillers and Connectors\nSmall Talk and Social Conversations\nFormal vs Informal Language\nBody Language and Non-verbal Communication\nFluency Practice Strategies',
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

    # Module 1 Questions
    def get_module1_questions(self):
        return [
            {
                'question': 'Which of the following is a proper noun?',
                'options': [
                    'city',
                    'London',
                    'country',
                    'place'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What part of speech is the word "quickly" in "She ran quickly"?',
                'options': [
                    'Adjective',
                    'Adverb',
                    'Noun',
                    'Verb'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence has a linking verb?',
                'options': [
                    'She runs every morning.',
                    'He is a teacher.',
                    'They play football.',
                    'I eat breakfast.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What type of pronoun is "myself" in "I did it myself"?',
                'options': [
                    'Personal pronoun',
                    'Possessive pronoun',
                    'Reflexive pronoun',
                    'Relative pronoun'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which word is a preposition in "The book is on the table"?',
                'options': [
                    'book',
                    'is',
                    'on',
                    'table'
                ],
                'correct_answer': 3
            },
            {
                'question': 'What part of speech is "and" in "Tom and Jerry are friends"?',
                'options': [
                    'Preposition',
                    'Conjunction',
                    'Adverb',
                    'Interjection'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which of the following is an abstract noun?',
                'options': [
                    'table',
                    'happiness',
                    'dog',
                    'car'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What type of adjective is "this" in "this book"?',
                'options': [
                    'Descriptive adjective',
                    'Demonstrative adjective',
                    'Possessive adjective',
                    'Quantitative adjective'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence contains an interjection?',
                'options': [
                    'Oh no! I forgot my keys.',
                    'She is very happy.',
                    'They went to the park.',
                    'I like coffee.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is the verb in "The students are studying"?',
                'options': [
                    'students',
                    'are',
                    'studying',
                    'are studying'
                ],
                'correct_answer': 4
            },
        ]

    # Module 2 Questions
    def get_module2_questions(self):
        return [
            {
                'question': 'Which sentence uses Present Perfect tense?',
                'options': [
                    'I go to school every day.',
                    'I have finished my homework.',
                    'I am going to school now.',
                    'I went to school yesterday.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What tense is "She will be traveling next week"?',
                'options': [
                    'Simple Future',
                    'Future Continuous',
                    'Future Perfect',
                    'Future Perfect Continuous'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence is in Past Perfect tense?',
                'options': [
                    'I had eaten before you arrived.',
                    'I ate dinner.',
                    'I was eating dinner.',
                    'I have eaten dinner.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What tense is "They have been waiting for two hours"?',
                'options': [
                    'Present Perfect',
                    'Present Perfect Continuous',
                    'Present Continuous',
                    'Past Perfect'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence uses Simple Past tense?',
                'options': [
                    'I play tennis.',
                    'I played tennis yesterday.',
                    'I am playing tennis.',
                    'I will play tennis.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What tense is "I was reading when you called"?',
                'options': [
                    'Simple Past',
                    'Past Continuous',
                    'Past Perfect',
                    'Present Continuous'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence uses Present Continuous tense?',
                'options': [
                    'I work here.',
                    'I am working here.',
                    'I have worked here.',
                    'I worked here.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What tense is "By next year, I will have completed my degree"?',
                'options': [
                    'Simple Future',
                    'Future Continuous',
                    'Future Perfect',
                    'Future Perfect Continuous'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence is grammatically correct?',
                'options': [
                    'I am living here for five years.',
                    'I have been living here for five years.',
                    'I live here for five years.',
                    'I lived here for five years.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What tense is "She had been working all day before she rested"?',
                'options': [
                    'Past Perfect',
                    'Past Perfect Continuous',
                    'Past Continuous',
                    'Present Perfect Continuous'
                ],
                'correct_answer': 2
            },
        ]

    # Module 3 Questions
    def get_module3_questions(self):
        return [
            {
                'question': 'Which is a simple sentence?',
                'options': [
                    'I like coffee, and she likes tea.',
                    'I like coffee.',
                    'I like coffee because it tastes good.',
                    'I like coffee, but she prefers tea, and we both enjoy our drinks.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which is a compound sentence?',
                'options': [
                    'I study hard.',
                    'I study hard, and I get good grades.',
                    'I study hard because I want good grades.',
                    'I study hard, which helps me get good grades, and I am happy.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which is a complex sentence?',
                'options': [
                    'I like reading.',
                    'I like reading, and I like writing.',
                    'I like reading because it expands my knowledge.',
                    'I like reading, and I like writing, but I prefer reading.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence has correct subject-verb agreement?',
                'options': [
                    'The students is studying.',
                    'The students are studying.',
                    'The students was studying.',
                    'The students be studying.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence is a fragment?',
                'options': [
                    'I went to the store.',
                    'Went to the store.',
                    'I went to the store and bought groceries.',
                    'I went to the store, and I bought groceries.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence has parallel structure?',
                'options': [
                    'She likes reading, to write, and swimming.',
                    'She likes reading, writing, and swimming.',
                    'She likes to read, writing, and to swim.',
                    'She likes reading, write, and swimming.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence is grammatically correct?',
                'options': [
                    'Neither the students nor the teacher were present.',
                    'Neither the students nor the teacher was present.',
                    'Neither the students nor the teacher are present.',
                    'Neither the students nor the teacher is present.'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What type of sentence is "Although it was raining, we went for a walk"?',
                'options': [
                    'Simple',
                    'Compound',
                    'Complex',
                    'Compound-Complex'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence has correct subject-verb agreement?',
                'options': [
                    'Each of the students have a book.',
                    'Each of the students has a book.',
                    'Each of the students are having a book.',
                    'Each of the students were having a book.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What type of sentence is "I finished my work, and then I went home"?',
                'options': [
                    'Simple',
                    'Compound',
                    'Complex',
                    'Compound-Complex'
                ],
                'correct_answer': 2
            },
        ]

    # Module 4 Questions
    def get_module4_questions(self):
        return [
            {
                'question': 'Which sentence uses the correct article?',
                'options': [
                    'I need a advice.',
                    'I need an advice.',
                    'I need the advice.',
                    'I need advice.'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which sentence is correct?',
                'options': [
                    'She is a honest person.',
                    'She is an honest person.',
                    'She is the honest person.',
                    'She is honest person.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence uses "the" correctly?',
                'options': [
                    'The sun rises in the east.',
                    'A sun rises in an east.',
                    'Sun rises in east.',
                    'The sun rises in an east.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What type of noun is "water"?',
                'options': [
                    'Countable',
                    'Uncountable',
                    'Both',
                    'Neither'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence is correct?',
                'options': [
                    'I have many informations.',
                    'I have much information.',
                    'I have many information.',
                    'I have much informations.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which determiner is correct? "I don\'t have _____ money."',
                'options': [
                    'many',
                    'much',
                    'few',
                    'little'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which sentence uses "few" correctly?',
                'options': [
                    'I have few friends.',
                    'I have few money.',
                    'I have few water.',
                    'I have few information.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sentence is correct?',
                'options': [
                    'Can I have some water?',
                    'Can I have any water?',
                    'Can I have many water?',
                    'Can I have few water?'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sentence uses "the" correctly?',
                'options': [
                    'I play the piano.',
                    'I play a piano.',
                    'I play piano.',
                    'I play an piano.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which quantifier is correct? "There are _____ books on the shelf."',
                'options': [
                    'much',
                    'little',
                    'many',
                    'a little'
                ],
                'correct_answer': 3
            },
        ]

    # Module 5 Questions
    def get_module5_questions(self):
        return [
            {
                'question': 'Which modal verb expresses possibility?',
                'options': [
                    'must',
                    'should',
                    'might',
                    'will'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence expresses obligation?',
                'options': [
                    'You can go now.',
                    'You might go now.',
                    'You must go now.',
                    'You could go now.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which is a zero conditional sentence?',
                'options': [
                    'If it rains, I will stay home.',
                    'If it rained, I would stay home.',
                    'If it rains, I stay home.',
                    'If it had rained, I would have stayed home.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which is a first conditional sentence?',
                'options': [
                    'If it rains, I stay home.',
                    'If it rained, I would stay home.',
                    'If it rains, I will stay home.',
                    'If it had rained, I would have stayed home.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which is a second conditional sentence?',
                'options': [
                    'If I have time, I will help you.',
                    'If I had had time, I would have helped you.',
                    'If I had time, I would help you.',
                    'If I have time, I help you.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which is a third conditional sentence?',
                'options': [
                    'If I study, I will pass.',
                    'If I studied, I would pass.',
                    'If I had studied, I would have passed.',
                    'If I study, I pass.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence expresses ability in the past?',
                'options': [
                    'I can swim.',
                    'I must swim.',
                    'I could swim when I was young.',
                    'I should swim.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence is a polite request?',
                'options': [
                    'Give me the book!',
                    'You must give me the book.',
                    'Could you give me the book?',
                    'You should give me the book.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence expresses advice?',
                'options': [
                    'You can study hard.',
                    'You must study hard.',
                    'You should study hard.',
                    'You will study hard.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which sentence expresses certainty?',
                'options': [
                    'It might rain.',
                    'It could rain.',
                    'It must be raining.',
                    'It may rain.'
                ],
                'correct_answer': 3
            },
        ]

    # Module 6 Questions
    def get_module6_questions(self):
        return [
            {
                'question': 'Which sentence is in passive voice?',
                'options': [
                    'The cat chased the mouse.',
                    'The cat is chasing the mouse.',
                    'The mouse was chased by the cat.',
                    'The cat will chase the mouse.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to passive: "They built this house."',
                'options': [
                    'This house was built by them.',
                    'This house is built by them.',
                    'This house built by them.',
                    'This house was build by them.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Convert to active: "The letter was written by John."',
                'options': [
                    'John wrote the letter.',
                    'John writes the letter.',
                    'John is writing the letter.',
                    'John will write the letter.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sentence is in passive voice?',
                'options': [
                    'She teaches English.',
                    'She is teaching English.',
                    'English is taught by her.',
                    'She will teach English.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to passive: "Someone stole my bike."',
                'options': [
                    'My bike was stolen.',
                    'My bike is stolen.',
                    'My bike stole.',
                    'My bike was steal.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sentence uses passive voice correctly?',
                'options': [
                    'The cake was eaten by the children.',
                    'The cake was eat by the children.',
                    'The cake was eating by the children.',
                    'The cake is eaten by the children.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'When is passive voice preferred?',
                'options': [
                    'When the doer is unknown or unimportant',
                    'When emphasizing the doer',
                    'When writing informally',
                    'When the action is not important'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Convert to passive: "They are painting the wall."',
                'options': [
                    'The wall is being painted by them.',
                    'The wall is painted by them.',
                    'The wall was being painted by them.',
                    'The wall will be painted by them.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which sentence is in active voice?',
                'options': [
                    'The problem was solved by the team.',
                    'The problem is being solved.',
                    'The team solved the problem.',
                    'The problem has been solved.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to passive: "She will finish the work."',
                'options': [
                    'The work will be finished by her.',
                    'The work is finished by her.',
                    'The work was finished by her.',
                    'The work will finish by her.'
                ],
                'correct_answer': 1
            },
        ]

    # Module 7 Questions
    def get_module7_questions(self):
        return [
            {
                'question': 'Convert to indirect speech: "I am tired," he said.',
                'options': [
                    'He said that he is tired.',
                    'He said that he will be tired.',
                    'He said that he was tired.',
                    'He said that he has been tired.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to indirect speech: "I will help you," she said.',
                'options': [
                    'She said that she will help me.',
                    'She said that she helps me.',
                    'She said that she would help me.',
                    'She said that she helped me.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to indirect speech: "What is your name?" he asked.',
                'options': [
                    'He asked what is my name.',
                    'He asked what was my name.',
                    'He asked what my name is.',
                    'He asked what my name was.'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Convert to indirect speech: "Do you like coffee?" she asked.',
                'options': [
                    'She asked if I like coffee.',
                    'She asked do I like coffee.',
                    'She asked if I liked coffee.',
                    'She asked that I like coffee.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to indirect speech: "Come here," he said.',
                'options': [
                    'He said to come here.',
                    'He said come here.',
                    'He told me to come here.',
                    'He told that come here.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to indirect speech: "I have finished," she said.',
                'options': [
                    'She said that she has finished.',
                    'She said that she finished.',
                    'She said that she had finished.',
                    'She said that she is finished.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Convert to indirect speech: "Where do you live?" he asked.',
                'options': [
                    'He asked where I live.',
                    'He asked where do I live.',
                    'He asked where did I live.',
                    'He asked where I lived.'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Convert to indirect speech: "Don\'t go there," she said.',
                'options': [
                    'She said don\'t go there.',
                    'She told me not to go there.',
                    'She said to not go there.',
                    'She told that don\'t go there.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Convert to indirect speech: "I was studying," he said.',
                'options': [
                    'He said that he is studying.',
                    'He said that he was studying.',
                    'He said that he studies.',
                    'He said that he had been studying.'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Convert to indirect speech: "Can you help me?" she asked.',
                'options': [
                    'She asked if I can help her.',
                    'She asked can I help her.',
                    'She asked that I can help her.',
                    'She asked if I could help her.'
                ],
                'correct_answer': 4
            },
        ]

    # Module 8 Questions
    def get_module8_questions(self):
        return [
            {
                'question': 'What is a synonym for "happy"?',
                'options': [
                    'sad',
                    'angry',
                    'tired',
                    'joyful'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is an antonym for "big"?',
                'options': [
                    'large',
                    'huge',
                    'enormous',
                    'small'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the idiom "break the ice" mean?',
                'options': [
                    'To make something cold',
                    'To break something',
                    'To freeze something',
                    'To start a conversation'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the phrasal verb "give up" mean?',
                'options': [
                    'To give something',
                    'To give away',
                    'To give back',
                    'To stop trying'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which prefix means "not" or "opposite"?',
                'options': [
                    'pre-',
                    're-',
                    'dis-',
                    'un-'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which suffix forms a noun meaning "the act of"?',
                'options': [
                    '-tion',
                    '-ly',
                    '-ful',
                    '-er'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What does the idiom "hit the nail on the head" mean?',
                'options': [
                    'To be exactly right',
                    'To hit something',
                    'To make a mistake',
                    'To be confused'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is a collocation?',
                'options': [
                    'Words that sound the same',
                    'Words with opposite meanings',
                    'Words with similar meanings',
                    'Words that are often used together'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What does the phrasal verb "look after" mean?',
                'options': [
                    'To look behind',
                    'To look for',
                    'To look at',
                    'To take care of'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which word formation process creates "unhappiness" from "happy"?',
                'options': [
                    'Compounding',
                    'Conversion',
                    'Blending',
                    'Derivation (prefix + suffix)'
                ],
                'correct_answer': 4
            },
        ]

    # Module 9 Questions
    def get_module9_questions(self):
        return [
            {
                'question': 'Which word has the stress on the first syllable?',
                'options': [
                    'about',
                    'above',
                    'before',
                    'begin'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which pair are homophones?',
                'options': [
                    'see, sea',
                    'book, look',
                    'cat, dog',
                    'big, small'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which letter is silent in "knight"?',
                'options': [
                    'k',
                    'n',
                    'g',
                    'h'
                ],
                'correct_answer': 1
            },
            {
                'question': 'In the sentence "I want to GO there," which word is stressed?',
                'options': [
                    'I',
                    'want',
                    'there',
                    'GO'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which word has a different vowel sound?',
                'options': [
                    'cat',
                    'hat',
                    'bat',
                    'late'
                ],
                'correct_answer': 4
            },
            {
                'question': 'What is intonation?',
                'options': [
                    'The rhythm of speech',
                    'The speed of speech',
                    'The volume of speech',
                    'The rise and fall of voice pitch'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which sentence has rising intonation?',
                'options': [
                    'I am happy.',
                    'I am not happy.',
                    'She is happy.',
                    'Are you happy?'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which letter is silent in "honest"?',
                'options': [
                    'h',
                    'o',
                    'n',
                    't'
                ],
                'correct_answer': 1
            },
            {
                'question': 'What is word stress?',
                'options': [
                    'Emphasizing certain syllables in a word',
                    'Emphasizing certain words in a sentence',
                    'The speed of pronunciation',
                    'The pitch of pronunciation'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which word has the stress on the second syllable?',
                'options': [
                    'happy',
                    'student',
                    'begin',
                    'teacher'
                ],
                'correct_answer': 4
            },
        ]

    # Module 10 Questions
    def get_module10_questions(self):
        return [
            {
                'question': 'Which phrase is appropriate for starting a conversation?',
                'options': [
                    'What do you want?',
                    'Tell me everything.',
                    'I need to talk.',
                    'How are you doing?'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which phrase expresses agreement?',
                'options': [
                    'I disagree.',
                    'I think so too.',
                    'That\'s not right.',
                    'I don\'t think so.'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which phrase is a conversation filler?',
                'options': [
                    'Let me think...',
                    'I am done.',
                    'That\'s all.',
                    'Goodbye.'
                ],
                'correct_answer': 1
            },
            {
                'question': 'Which phrase is appropriate for asking for clarification?',
                'options': [
                    'What?',
                    'I don\'t understand.',
                    'Could you please clarify?',
                    'I need more information.'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which phrase expresses an opinion politely?',
                'options': [
                    'You are wrong.',
                    'That\'s not right.',
                    'I disagree completely.',
                    'I think...'
                ],
                'correct_answer': 4
            },
            {
                'question': 'Which connector is used to add information?',
                'options': [
                    'but',
                    'however',
                    'furthermore',
                    'although'
                ],
                'correct_answer': 3
            },
            {
                'question': 'Which phrase is appropriate for small talk?',
                'options': [
                    'What\'s your salary?',
                    'Nice weather today, isn\'t it?',
                    'How much do you weigh?',
                    'Are you married?'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which phrase is formal?',
                'options': [
                    'Hey, what\'s up?',
                    'Good morning, how may I help you?',
                    'Hi there!',
                    'What\'s going on?'
                ],
                'correct_answer': 2
            },
            {
                'question': 'Which phrase expresses disagreement politely?',
                'options': [
                    'You\'re wrong!',
                    'I see your point, but...',
                    'That\'s ridiculous!',
                    'No, you\'re stupid!'
                ],
                'correct_answer': 2
            },
            {
                'question': 'What is fluency?',
                'options': [
                    'Speaking without any mistakes',
                    'Speaking smoothly and naturally',
                    'Speaking very fast',
                    'Speaking with perfect grammar'
                ],
                'correct_answer': 2
            },
        ]










