from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Max

from .models import AdminProfile, Course, Module, Quiz, QuizQuestion, QuizOption
from .decorators import admin_required


def admin_login_view(request):
    """Admin login view"""
    if request.user.is_authenticated and hasattr(request.user, 'admin_profile'):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is admin
            if hasattr(user, 'admin_profile') or user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. Admin privileges required.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'learning/admin_login.html')


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard"""
    courses = Course.objects.all().order_by('-created_at')
    total_courses = courses.count()
    featured_courses = courses.filter(is_featured=True).count()
    
    context = {
        'courses': courses,
        'total_courses': total_courses,
        'featured_courses': featured_courses,
    }
    return render(request, 'learning/admin_dashboard.html', context)


@login_required
@admin_required
def admin_course_create(request):
    """Create new course"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        is_featured = request.POST.get('is_featured') == 'on'
        
        if title and description:
            course = Course.objects.create(
                title=title,
                description=description,
                category=category,
                is_featured=is_featured
            )
            messages.success(request, 'Course created successfully! You can now add modules to this course.')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Title and description are required.')
    
    return render(request, 'learning/admin_course_form.html', {'form_type': 'create'})


@login_required
@admin_required
def admin_course_edit(request, course_id):
    """Edit existing course"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.category = request.POST.get('category')
        course.is_featured = request.POST.get('is_featured') == 'on'
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('admin_dashboard')
    
    context = {
        'course': course,
        'form_type': 'edit',
    }
    return render(request, 'learning/admin_course_form.html', context)


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_course_delete(request, course_id):
    """Delete course"""
    course = get_object_or_404(Course, id=course_id)
    course_title = course.title
    course.delete()
    messages.success(request, f'Course "{course_title}" deleted successfully!')
    return redirect('admin_dashboard')


@login_required
@admin_required
def admin_modules_list(request, course_id):
    """List all modules for a course"""
    course = get_object_or_404(Course.objects.prefetch_related('modules'), id=course_id)
    modules = course.modules.all()
    
    context = {
        'course': course,
        'modules': modules,
    }
    return render(request, 'learning/admin_modules_list.html', context)


@login_required
@admin_required
def admin_module_create(request, course_id):
    """Create new module for a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        order = request.POST.get('order')
        learning_objectives = request.POST.get('learning_objectives', '')
        topics = request.POST.get('topics', '')
        
        if title and summary and order:
            try:
                order = int(order)
                # Check if order already exists for this course
                if Module.objects.filter(course=course, order=order).exists():
                    messages.error(request, f'Module with order {order} already exists for this course.')
                else:
                    Module.objects.create(
                        course=course,
                        title=title,
                        summary=summary,
                        order=order,
                        learning_objectives=learning_objectives,
                        topics=topics
                    )
                    messages.success(request, 'Module created successfully!')
                    return redirect('admin_modules_list', course_id=course.id)
            except ValueError:
                messages.error(request, 'Order must be a valid number.')
        else:
            messages.error(request, 'Title, summary, and order are required.')
    
    # Get the next available order number
    max_order = course.modules.aggregate(Max('order'))['order__max'] or 0
    next_order = max_order + 1
    
    context = {
        'course': course,
        'form_type': 'create',
        'next_order': next_order,
    }
    return render(request, 'learning/admin_module_form.html', context)


@login_required
@admin_required
def admin_module_edit(request, course_id, module_id):
    """Edit existing module"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if request.method == 'POST':
        module.title = request.POST.get('title')
        module.summary = request.POST.get('summary')
        order = request.POST.get('order')
        module.learning_objectives = request.POST.get('learning_objectives', '')
        module.topics = request.POST.get('topics', '')
        
        if module.title and module.summary and order:
            try:
                new_order = int(order)
                # Check if order already exists for this course (excluding current module)
                if new_order != module.order and Module.objects.filter(course=course, order=new_order).exists():
                    messages.error(request, f'Module with order {new_order} already exists for this course.')
                else:
                    module.order = new_order
                    module.save()
                    messages.success(request, 'Module updated successfully!')
                    return redirect('admin_modules_list', course_id=course.id)
            except ValueError:
                messages.error(request, 'Order must be a valid number.')
        else:
            messages.error(request, 'Title, summary, and order are required.')
    
    context = {
        'course': course,
        'module': module,
        'form_type': 'edit',
    }
    return render(request, 'learning/admin_module_form.html', context)


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_module_delete(request, course_id, module_id):
    """Delete module"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    module_title = module.title
    module.delete()
    messages.success(request, f'Module "{module_title}" deleted successfully!')
    return redirect('admin_modules_list', course_id=course.id)


@login_required
@admin_required
def admin_quiz_create(request, course_id, module_id):
    """Create quiz for a module"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if quiz already exists
    if hasattr(module, 'quiz'):
        messages.info(request, 'This module already has a quiz. You can edit it instead.')
        return redirect('admin_quiz_edit', course_id=course.id, module_id=module.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        passing_score = request.POST.get('passing_score', '70')
        time_limit = request.POST.get('time_limit', '30') or None
        
        if title:
            try:
                passing_score = int(passing_score)
                time_limit = int(time_limit) if time_limit else None
                
                quiz = Quiz.objects.create(
                    module=module,
                    title=title,
                    description=description,
                    passing_score=passing_score,
                    time_limit=time_limit
                )
                messages.success(request, 'Quiz created successfully! Now add questions to the quiz.')
                return redirect('admin_quiz_questions', course_id=course.id, module_id=module.id)
            except ValueError:
                messages.error(request, 'Passing score and time limit must be valid numbers.')
        else:
            messages.error(request, 'Quiz title is required.')
    
    context = {
        'course': course,
        'module': module,
        'form_type': 'create',
    }
    return render(request, 'learning/admin_quiz_form.html', context)


@login_required
@admin_required
def admin_quiz_edit(request, course_id, module_id):
    """Edit quiz for a module"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if not hasattr(module, 'quiz'):
        messages.error(request, 'This module does not have a quiz. Create one first.')
        return redirect('admin_modules_list', course_id=course.id)
    
    quiz = module.quiz
    
    if request.method == 'POST':
        quiz.title = request.POST.get('title')
        quiz.description = request.POST.get('description', '')
        passing_score = request.POST.get('passing_score', '70')
        time_limit = request.POST.get('time_limit', '30') or None
        
        try:
            quiz.passing_score = int(passing_score)
            quiz.time_limit = int(time_limit) if time_limit else None
            quiz.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('admin_quiz_questions', course_id=course.id, module_id=module.id)
        except ValueError:
            messages.error(request, 'Passing score and time limit must be valid numbers.')
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'form_type': 'edit',
    }
    return render(request, 'learning/admin_quiz_form.html', context)


@login_required
@admin_required
def admin_quiz_questions(request, course_id, module_id):
    """Manage quiz questions"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if not hasattr(module, 'quiz'):
        messages.error(request, 'This module does not have a quiz. Create one first.')
        return redirect('admin_modules_list', course_id=course.id)
    
    quiz = module.quiz
    questions = quiz.questions.all().prefetch_related('options')
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'learning/admin_quiz_questions.html', context)


@login_required
@admin_required
def admin_question_create(request, course_id, module_id):
    """Create a new question for a quiz"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    if not hasattr(module, 'quiz'):
        messages.error(request, 'This module does not have a quiz. Create one first.')
        return redirect('admin_modules_list', course_id=course.id)
    
    quiz = module.quiz
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = 'multiple_choice'  # Force MCQ format
        points = request.POST.get('points', '1')
        order = request.POST.get('order')
        
        if question_text:
            try:
                points = int(points)
                order = int(order) if order else quiz.questions.count() + 1
                
                question = QuizQuestion.objects.create(
                    quiz=quiz,
                    question_text=question_text,
                    question_type=question_type,
                    points=points,
                    order=order
                )
                
                # Handle options
                option_texts = request.POST.getlist('option_text')
                option_corrects = request.POST.getlist('option_correct')
                
                for idx, option_text in enumerate(option_texts):
                    if option_text.strip():
                        is_correct = str(idx) in option_corrects
                        QuizOption.objects.create(
                            question=question,
                            option_text=option_text.strip(),
                            is_correct=is_correct,
                            order=idx + 1
                        )
                
                messages.success(request, 'Question added successfully!')
                return redirect('admin_quiz_questions', course_id=course.id, module_id=module.id)
            except ValueError:
                messages.error(request, 'Points and order must be valid numbers.')
        else:
            messages.error(request, 'Question text is required.')
    
    # Get next order number
    next_order = quiz.questions.count() + 1
    
    context = {
        'course': course,
        'module': module,
        'quiz': quiz,
        'form_type': 'create',
        'next_order': next_order,
    }
    return render(request, 'learning/admin_question_form.html', context)


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_question_delete(request, course_id, module_id, question_id):
    """Delete a question"""
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    question = get_object_or_404(QuizQuestion, id=question_id, quiz=module.quiz)
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('admin_quiz_questions', course_id=course.id, module_id=module.id)

