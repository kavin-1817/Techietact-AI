from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    LearnerProfile, AdminProfile, Course, Module, ChatSession, 
    CourseEnrollment, EnrollmentRequest, Quiz, QuizQuestion, 
    QuizOption, UserQuizAttempt, QuizAttemptRequest, UserAnswer
)

# Unregister the default User admin and register with extended admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_level', 'joined_date', 'phone_number', 'location']
    list_filter = ['skill_level', 'joined_date']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number', 'location']
    readonly_fields = ['joined_date']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'joined_date')
        }),
        ('Profile Information', {
            'fields': ('profile_image', 'bio', 'phone_number', 'location')
        }),
        ('Learning Preferences', {
            'fields': ('skill_level', 'interests', 'learning_goals', 'preferred_languages')
        }),
        ('Social Links', {
            'fields': ('github_username', 'linkedin_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ['order', 'title', 'summary', 'learning_objectives', 'topics']
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'order', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ModuleInline]
    ordering = ['order', '-created_at']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'order', 'title', 'has_quiz']
    list_filter = ['course', 'course__category']
    search_fields = ['title', 'summary', 'course__title']
    ordering = ['course', 'order']
    
    def has_quiz(self, obj):
        return hasattr(obj, 'quiz')
    has_quiz.boolean = True
    has_quiz.short_description = 'Has Quiz'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'topic', 'created_at']
    list_filter = ['created_at', 'module__course']
    search_fields = ['user__username', 'module__title', 'topic', 'question', 'response']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 2
    fields = ['order', 'option_text', 'is_correct']
    ordering = ['order']


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'order', 'question_text_short', 'points', 'question_type']
    list_filter = ['quiz', 'question_type']
    search_fields = ['question_text']
    inlines = [QuizOptionInline]
    ordering = ['quiz', 'order']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'passing_score', 'time_limit', 'question_count', 'created_at']
    list_filter = ['created_at', 'passing_score']
    search_fields = ['title', 'description', 'module__title', 'module__course__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(QuizOption)
class QuizOptionAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'option_text_short', 'is_correct']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['option_text', 'question__question_text']
    ordering = ['question', 'order']
    
    def option_text_short(self, obj):
        return obj.option_text[:50] + '...' if len(obj.option_text) > 50 else obj.option_text
    option_text_short.short_description = 'Option'


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ['question', 'selected_option', 'is_correct']
    can_delete = False


@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'passed', 'auto_submitted', 'violation_count', 'started_at']
    list_filter = ['passed', 'auto_submitted', 'started_at', 'quiz']
    search_fields = ['user__username', 'user__email', 'quiz__title', 'violation_details']
    readonly_fields = ['started_at', 'completed_at', 'violation_details']
    date_hierarchy = 'started_at'
    inlines = [UserAnswerInline]
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('user', 'quiz', 'started_at', 'completed_at')
        }),
        ('Results', {
            'fields': ('score', 'total_points', 'earned_points', 'passed')
        }),
        ('Proctoring Information', {
            'fields': ('auto_submitted', 'violation_count', 'violation_details'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_option', 'is_correct']
    list_filter = ['is_correct', 'attempt__quiz']
    search_fields = ['attempt__user__username', 'question__question_text']
    readonly_fields = ['attempt', 'question', 'selected_option', 'is_correct']


@admin.register(QuizAttemptRequest)
class QuizAttemptRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'status', 'used', 'requested_at', 'reviewed_at']
    list_filter = ['status', 'used', 'requested_at']
    search_fields = ['user__username', 'user__email', 'quiz__title', 'reason', 'admin_notes']
    readonly_fields = ['requested_at', 'reviewed_at', 'reviewed_by']
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'quiz', 'reason', 'status', 'used')
        }),
        ('Review Information', {
            'fields': ('requested_at', 'reviewed_at', 'reviewed_by', 'admin_notes')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status != 'pending':
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'requested_at', 'reviewed_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['user__username', 'user__email', 'course__title', 'notes']
    readonly_fields = ['requested_at', 'reviewed_at', 'reviewed_by']
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'course', 'status', 'notes')
        }),
        ('Review Information', {
            'fields': ('requested_at', 'reviewed_at', 'reviewed_by')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status != 'pending':
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)


