from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Course learning experience
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('modules/<int:module_id>/', views.module_detail, name='module_detail'),
    path('practice/', views.practice_code_lab, name='practice_code'),
    path('modules/<int:module_id>/ask/', views.module_ask_api, name='module_ask_api'),
    path('modules/<int:module_id>/delete-memory/', views.module_delete_memory, name='module_delete_memory'),
    
    # Admin URLs
    path('admin/login/', admin_views.admin_login_view, name='admin_login'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/courses/create/', admin_views.admin_course_create, name='admin_course_create'),
    path('admin/courses/<int:course_id>/edit/', admin_views.admin_course_edit, name='admin_course_edit'),
    path('admin/courses/<int:course_id>/delete/', admin_views.admin_course_delete, name='admin_course_delete'),
    
    # Admin Module URLs
    path('admin/courses/<int:course_id>/modules/', admin_views.admin_modules_list, name='admin_modules_list'),
    path('admin/courses/<int:course_id>/modules/create/', admin_views.admin_module_create, name='admin_module_create'),
    path('admin/courses/<int:course_id>/modules/<int:module_id>/edit/', admin_views.admin_module_edit, name='admin_module_edit'),
    path('admin/courses/<int:course_id>/modules/<int:module_id>/delete/', admin_views.admin_module_delete, name='admin_module_delete'),
    
    # Admin Quiz URLs
    path('admin/courses/<int:course_id>/modules/<int:module_id>/quiz/create/', admin_views.admin_quiz_create, name='admin_quiz_create'),
    path('admin/courses/<int:course_id>/modules/<int:module_id>/quiz/edit/', admin_views.admin_quiz_edit, name='admin_quiz_edit'),
    path('admin/courses/<int:course_id>/modules/<int:module_id>/quiz/questions/', admin_views.admin_quiz_questions, name='admin_quiz_questions'),
    path('admin/courses/<int:course_id>/modules/<int:module_id>/quiz/questions/create/', admin_views.admin_question_create, name='admin_question_create'),
    path('admin/courses/<int:course_id>/modules/<int:module_id>/quiz/questions/<int:question_id>/delete/', admin_views.admin_question_delete, name='admin_question_delete'),
    
    # Quiz URLs
    path('modules/<int:module_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('modules/<int:module_id>/quiz/submit/', views.submit_quiz, name='submit_quiz'),
]

