from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LearnerProfile(models.Model):
    """Extended profile for learners"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    joined_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Learner Profile'
        verbose_name_plural = 'Learner Profiles'
    
    def __str__(self):
        return f'{self.user.username} - Learner'


class AdminProfile(models.Model):
    """Extended profile for admins"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
    
    def __str__(self):
        return f'{self.user.username} - Admin'


class Course(models.Model):
    """Course/Topic model for suggestions"""
    CATEGORY_CHOICES = [
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('programming', 'Programming'),
        ('language', 'Language'),
        ('history', 'History'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1, help_text='Display order in course list (lower numbers appear first)')
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title


class Module(models.Model):
    """Modules that belong to a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    summary = models.TextField()
    order = models.PositiveSmallIntegerField(default=1)
    learning_objectives = models.TextField(help_text='Use bullet points separated by newline.', blank=True)
    topics = models.TextField(help_text='Topics covered inside the module, separated by newline.', blank=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
    
    def __str__(self):
        return f'{self.course.title} - Module {self.order}: {self.title}'
    
    def is_unlocked_for_user(self, user):
        """Check if this module is unlocked for a user"""
        if not user:
            return False
        
        # Admins and staff can access every module without restrictions
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or hasattr(user, 'admin_profile'):
            return True
        
        # First module (order=1) is always unlocked
        if self.order == 1:
            return True
        
        # Check if previous module's quiz was passed
        previous_module = Module.objects.filter(
            course=self.course,
            order=self.order - 1
        ).first()
        
        if not previous_module:
            return True  # If no previous module, unlock it
        
        # Check if previous module has a quiz
        if not hasattr(previous_module, 'quiz'):
            # If previous module has no quiz, lock this module until quiz is created
            return False
        
        previous_quiz = previous_module.quiz
        
        # Check if user passed the previous module's quiz
        passed_attempt = UserQuizAttempt.objects.filter(
            user=user,
            quiz=previous_quiz,
            passed=True
        ).first()
        
        return passed_attempt is not None


class ChatSession(models.Model):
    """Chat session model to store AI conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions')
    topic = models.CharField(max_length=200, blank=True, help_text='Specific topic this chat session is for')
    question = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'module', 'topic']),
        ]
    
    def __str__(self):
        context = f'{self.module.title}' if self.module else 'General'
        topic_str = f' - {self.topic}' if self.topic else ''
        return f'{self.user.username} - {context}{topic_str} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class Quiz(models.Model):
    """Quiz model for module assessments"""
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70, help_text='Minimum score percentage required to pass')
    time_limit = models.PositiveIntegerField(default=30, help_text='Time limit in minutes (0 for no limit)', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        module_str = f' - {self.module.title}' if self.module else ''
        return f'{self.title}{module_str}'
    
    def get_total_points(self):
        """Calculate total points for the quiz"""
        return sum(question.points for question in self.questions.all())


class QuizQuestion(models.Model):
    """Individual questions in a quiz - MCQ format only"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('multiple_choice', 'Multiple Choice (MCQ)'),
        ],
        default='multiple_choice'
    )
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveSmallIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.quiz.title} - Q{self.order}: {self.question_text[:50]}...'


class QuizOption(models.Model):
    """Options/choices for quiz questions"""
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.question.question_text[:30]}... - {self.option_text[:30]}...'


class UserQuizAttempt(models.Model):
    """Track user quiz attempts and scores"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.DecimalField(max_digits=5, decimal_places=2, help_text='Score as percentage')
    total_points = models.PositiveIntegerField()
    earned_points = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    auto_submitted = models.BooleanField(default=False, help_text='Whether quiz was auto-submitted due to violations')
    violation_count = models.PositiveIntegerField(default=0, help_text='Number of violations detected')
    violation_details = models.TextField(blank=True, help_text='Details of violations (tab switches, copy/paste, etc.)')
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'quiz']),
        ]
    
    def __str__(self):
        status = 'Passed' if self.passed else 'Failed'
        auto = ' (Auto-submitted)' if self.auto_submitted else ''
        return f'{self.user.username} - {self.quiz.title} - {status} ({self.score}%){auto}'


class QuizAttemptRequest(models.Model):
    """Request for additional quiz attempts after exhausting 3 attempts"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempt_requests')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempt_requests')
    reason = models.TextField(help_text='Reason for requesting additional attempt')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    used = models.BooleanField(default=False, help_text='Whether the approved request has been used for an attempt')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_attempt_requests')
    admin_notes = models.TextField(blank=True, help_text='Admin notes or comments')
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'quiz', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.quiz.title} - {self.status}'


class UserAnswer(models.Model):
    """Store individual answers for quiz attempts"""
    attempt = models.ForeignKey(UserQuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuizOption, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('attempt', 'question')
    
    def __str__(self):
        return f'{self.attempt.user.username} - {self.question.question_text[:30]}...'


class EnrollmentRequest(models.Model):
    """Track enrollment requests that need admin approval"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollment_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollment_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_enrollments')
    notes = models.TextField(blank=True, help_text='Admin notes for approval/rejection')
    
    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'course', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.course.title} ({self.status})'


class CourseEnrollment(models.Model):
    """Track approved user enrollments in courses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrollment_request = models.OneToOneField(EnrollmentRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollment')
    
    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['user', 'course']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
