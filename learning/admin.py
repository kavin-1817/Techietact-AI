from django.contrib import admin
from .models import LearnerProfile, AdminProfile, Course, Module, ChatSession


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'joined_date']
    list_filter = ['joined_date']
    search_fields = ['user__username', 'user__email']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ['order', 'title', 'summary', 'learning_objectives', 'topics']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'order', 'title']
    list_filter = ['course']
    search_fields = ['title', 'summary', 'course__title']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'question', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'module__title', 'question', 'response']
    readonly_fields = ['created_at']
