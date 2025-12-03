from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Max, Count, Avg, Q
from django.contrib.auth.models import User
import json

from .models import AdminProfile, Course, Module, Quiz, QuizQuestion, QuizOption, EnrollmentRequest, CourseEnrollment, UserQuizAttempt, QuizAttemptRequest
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
    from django.contrib.auth.models import User
    courses = Course.objects.all().order_by('order', '-created_at')
    total_courses = courses.count()
    featured_courses = courses.filter(is_featured=True).count()
    total_users = User.objects.count()
    pending_enrollments = EnrollmentRequest.objects.filter(status='pending').count()
    pending_attempt_requests = QuizAttemptRequest.objects.filter(status='pending').count()
    
    context = {
        'courses': courses,
        'total_courses': total_courses,
        'featured_courses': featured_courses,
        'total_users': total_users,
        'pending_enrollments': pending_enrollments,
        'pending_attempt_requests': pending_attempt_requests,
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
            # Get the next available order number
            max_order = Course.objects.aggregate(Max('order'))['order__max'] or 0
            next_order = max_order + 1
            
            course = Course.objects.create(
                title=title,
                description=description,
                category=category,
                is_featured=is_featured,
                order=next_order
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


@login_required
@admin_required
def admin_enrollment_requests(request):
    """List all enrollment requests"""
    pending_requests = EnrollmentRequest.objects.filter(status='pending').select_related('user', 'course').order_by('-requested_at')
    approved_requests = EnrollmentRequest.objects.filter(status='approved').select_related('user', 'course', 'reviewed_by').order_by('-reviewed_at')[:20]
    rejected_requests = EnrollmentRequest.objects.filter(status='rejected').select_related('user', 'course', 'reviewed_by').order_by('-reviewed_at')[:20]
    
    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'pending_count': pending_requests.count(),
    }
    return render(request, 'learning/admin_enrollment_requests.html', context)


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_approve_enrollment(request, request_id):
    """Approve an enrollment request"""
    enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id, status='pending')
    
    # Check if user is already enrolled
    if CourseEnrollment.objects.filter(user=enrollment_request.user, course=enrollment_request.course).exists():
        messages.warning(request, f'{enrollment_request.user.username} is already enrolled in {enrollment_request.course.title}.')
        enrollment_request.status = 'approved'
        enrollment_request.reviewed_at = timezone.now()
        enrollment_request.reviewed_by = request.user
        enrollment_request.save()
        return redirect('admin_enrollment_requests')
    
    # Create enrollment
    enrollment = CourseEnrollment.objects.create(
        user=enrollment_request.user,
        course=enrollment_request.course,
        enrollment_request=enrollment_request
    )
    
    # Update request status
    enrollment_request.status = 'approved'
    enrollment_request.reviewed_at = timezone.now()
    enrollment_request.reviewed_by = request.user
    enrollment_request.save()
    
    messages.success(request, f'Approved enrollment request for {enrollment_request.user.username} in {enrollment_request.course.title}.')
    return redirect('admin_enrollment_requests')


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_reject_enrollment(request, request_id):
    """Reject an enrollment request"""
    enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id, status='pending')
    notes = request.POST.get('notes', '').strip()
    
    enrollment_request.status = 'rejected'
    enrollment_request.reviewed_at = timezone.now()
    enrollment_request.reviewed_by = request.user
    if notes:
        enrollment_request.notes = notes
    enrollment_request.save()
    
    messages.success(request, f'Rejected enrollment request for {enrollment_request.user.username} in {enrollment_request.course.title}.')
    return redirect('admin_enrollment_requests')


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_course_reorder(request, course_id):
    """Reorder a course (move up or down)"""
    course = get_object_or_404(Course, id=course_id)
    direction = request.POST.get('direction')  # 'up' or 'down'
    
    if direction not in ['up', 'down']:
        return JsonResponse({'success': False, 'error': 'Invalid direction'}, status=400)
    
    # Get all courses ordered by current order
    all_courses = list(Course.objects.all().order_by('order', '-created_at'))
    
    # Find current course index
    try:
        current_index = next(i for i, c in enumerate(all_courses) if c.id == course.id)
    except StopIteration:
        return JsonResponse({'success': False, 'error': 'Course not found'}, status=404)
    
    # Calculate new index
    if direction == 'up' and current_index > 0:
        new_index = current_index - 1
    elif direction == 'down' and current_index < len(all_courses) - 1:
        new_index = current_index + 1
    else:
        return JsonResponse({'success': False, 'error': 'Cannot move course in that direction'}, status=400)
    
    # Swap the courses in the list
    all_courses[current_index], all_courses[new_index] = all_courses[new_index], all_courses[current_index]
    
    # Reassign orders sequentially (1, 2, 3, ...) to avoid gaps
    for index, c in enumerate(all_courses, start=1):
        c.order = index
        c.save(update_fields=['order'])
    
    return JsonResponse({'success': True, 'message': 'Course order updated successfully'})


@login_required
@admin_required
def admin_student_performance(request):
    """Track and display student performance metrics"""
    # Get all users excluding admins
    admin_user_ids = AdminProfile.objects.values_list('user_id', flat=True)
    students = User.objects.exclude(id__in=admin_user_ids).exclude(is_staff=True).exclude(is_superuser=True)
    
    # Get overall statistics
    total_students = students.count()
    total_enrollments = CourseEnrollment.objects.count()
    # Only count quiz attempts from students (exclude admins)
    total_quiz_attempts = UserQuizAttempt.objects.exclude(user_id__in=admin_user_ids).exclude(user__is_staff=True).exclude(user__is_superuser=True).count()
    
    # Calculate performance data for each student
    student_performance = []
    
    for student in students:
        # Get enrollments
        enrollments = CourseEnrollment.objects.filter(user=student).select_related('course')
        courses_enrolled = enrollments.count()
        
        # Calculate unlocked modules
        unlocked_modules_count = 0
        module_performances = []
        
        for enrollment in enrollments:
            course = enrollment.course
            modules = Module.objects.filter(course=course).order_by('order')
            
            for module in modules:
                is_unlocked = module.is_unlocked_for_user(student)
                if is_unlocked:
                    unlocked_modules_count += 1
                
                # Get quiz performance for this module
                quiz_performance = None
                if hasattr(module, 'quiz'):
                    quiz = module.quiz
                    attempts = UserQuizAttempt.objects.filter(
                        user=student,
                        quiz=quiz
                    ).order_by('-started_at')
                    
                    if attempts.exists():
                        best_attempt = attempts.first()
                        total_attempts = attempts.count()
                        passed_attempts = attempts.filter(passed=True).count()
                        
                        quiz_performance = {
                            'module_id': module.id,
                            'module_title': module.title,
                            'course_title': course.title,
                            'best_score': float(best_attempt.score),
                            'total_attempts': total_attempts,
                            'passed_attempts': passed_attempts,
                            'latest_attempt': best_attempt.started_at,
                            'is_passed': best_attempt.passed,
                            'is_unlocked': is_unlocked,
                        }
                    else:
                        quiz_performance = {
                            'module_id': module.id,
                            'module_title': module.title,
                            'course_title': course.title,
                            'best_score': None,
                            'total_attempts': 0,
                            'passed_attempts': 0,
                            'latest_attempt': None,
                            'is_passed': False,
                            'is_unlocked': is_unlocked,
                        }
                else:
                    quiz_performance = {
                        'module_id': module.id,
                        'module_title': module.title,
                        'course_title': course.title,
                        'best_score': None,
                        'total_attempts': 0,
                        'passed_attempts': 0,
                        'latest_attempt': None,
                        'is_passed': False,
                        'is_unlocked': is_unlocked,
                    }
                
                module_performances.append(quiz_performance)
        
        # Get overall quiz statistics
        all_attempts = UserQuizAttempt.objects.filter(user=student)
        total_quiz_attempts_student = all_attempts.count()
        passed_quizzes = all_attempts.filter(passed=True).count()
        
        avg_score = None
        if all_attempts.exists():
            avg_score = float(all_attempts.aggregate(Avg('score'))['score__avg'] or 0)
        
        student_performance.append({
            'student': student,
            'courses_enrolled': courses_enrolled,
            'unlocked_modules': unlocked_modules_count,
            'total_quiz_attempts': total_quiz_attempts_student,
            'passed_quizzes': passed_quizzes,
            'average_score': avg_score,
            'module_performances': module_performances,
        })
    
    # Sort by courses enrolled (descending), then by average score
    student_performance.sort(key=lambda x: (x['courses_enrolled'], x['average_score'] or 0), reverse=True)
    
    context = {
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'total_quiz_attempts': total_quiz_attempts,
        'student_performance': student_performance,
    }
    
    return render(request, 'learning/admin_student_performance.html', context)


@login_required
@admin_required
def admin_exam_violations(request):
    """Display all exam violations"""
    # Get all users excluding admins
    admin_user_ids = AdminProfile.objects.values_list('user_id', flat=True)
    
    # Get all violations from quiz attempts
    all_violations = []
    violation_attempts = UserQuizAttempt.objects.exclude(
        user_id__in=admin_user_ids
    ).exclude(
        user__is_staff=True
    ).exclude(
        user__is_superuser=True
    ).filter(
        violation_count__gt=0
    ).select_related('user', 'quiz', 'quiz__module', 'quiz__module__course').order_by('-started_at')
    
    for attempt in violation_attempts:
        # Parse violation details
        violation_list = []
        if attempt.violation_details:
            try:
                parsed = json.loads(attempt.violation_details)
                # Handle both list and dict formats
                if isinstance(parsed, list):
                    violation_list = parsed
                elif isinstance(parsed, dict):
                    violation_list = [parsed]
                else:
                    violation_list = [{'type': 'unknown', 'details': str(parsed)}]
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, try to parse as string
                violation_list = [{'type': 'unknown', 'details': str(attempt.violation_details)}]
        
        # Calculate attempt number for this quiz
        attempt_number = UserQuizAttempt.objects.filter(
            user=attempt.user,
            quiz=attempt.quiz,
            started_at__lte=attempt.started_at
        ).count()
        
        all_violations.append({
            'student': attempt.user,
            'student_username': attempt.user.username,
            'student_email': attempt.user.email,
            'quiz': attempt.quiz,
            'quiz_title': attempt.quiz.title,
            'module': attempt.quiz.module if hasattr(attempt.quiz, 'module') else None,
            'module_title': attempt.quiz.module.title if hasattr(attempt.quiz, 'module') else 'N/A',
            'course': attempt.quiz.module.course if hasattr(attempt.quiz, 'module') and hasattr(attempt.quiz.module, 'course') else None,
            'course_title': attempt.quiz.module.course.title if hasattr(attempt.quiz, 'module') and hasattr(attempt.quiz.module, 'course') else 'N/A',
            'attempt_number': attempt_number,
            'violation_count': attempt.violation_count,
            'violation_details': violation_list,
            'auto_submitted': attempt.auto_submitted,
            'score': float(attempt.score),
            'passed': attempt.passed,
            'started_at': attempt.started_at,
            'completed_at': attempt.completed_at,
        })
    
    # Get statistics
    total_violations = len(all_violations)
    total_auto_submitted = sum(1 for v in all_violations if v['auto_submitted'])
    unique_students_with_violations = len(set(v['student'].id for v in all_violations))
    
    context = {
        'all_violations': all_violations,
        'total_violations': total_violations,
        'total_auto_submitted': total_auto_submitted,
        'unique_students_with_violations': unique_students_with_violations,
    }
    
    return render(request, 'learning/admin_exam_violations.html', context)


@login_required
@admin_required
def admin_quiz_attempt_requests(request):
    """View and manage quiz attempt requests"""
    # Get all pending requests
    pending_requests = QuizAttemptRequest.objects.filter(
        status='pending'
    ).select_related('user', 'quiz', 'quiz__module', 'quiz__module__course').order_by('-requested_at')
    
    # Get all requests (for history)
    all_requests = QuizAttemptRequest.objects.all().select_related(
        'user', 'quiz', 'quiz__module', 'quiz__module__course', 'reviewed_by'
    ).order_by('-requested_at')
    
    # Statistics
    total_pending = pending_requests.count()
    total_approved = QuizAttemptRequest.objects.filter(status='approved').count()
    total_rejected = QuizAttemptRequest.objects.filter(status='rejected').count()
    
    context = {
        'pending_requests': pending_requests,
        'all_requests': all_requests,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
    }
    
    return render(request, 'learning/admin_quiz_attempt_requests.html', context)


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_approve_attempt_request(request, request_id):
    """Approve a quiz attempt request"""
    attempt_request = get_object_or_404(QuizAttemptRequest, id=request_id)
    
    if attempt_request.status != 'pending':
        messages.error(request, 'This request has already been reviewed.')
        return redirect('admin_quiz_attempt_requests')
    
    from django.utils import timezone
    attempt_request.status = 'approved'
    attempt_request.reviewed_at = timezone.now()
    attempt_request.reviewed_by = request.user
    attempt_request.save()
    
    messages.success(request, f'Attempt request from {attempt_request.user.username} has been approved.')
    return redirect('admin_quiz_attempt_requests')


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_reject_attempt_request(request, request_id):
    """Reject a quiz attempt request"""
    attempt_request = get_object_or_404(QuizAttemptRequest, id=request_id)
    
    if attempt_request.status != 'pending':
        messages.error(request, 'This request has already been reviewed.')
        return redirect('admin_quiz_attempt_requests')
    
    admin_notes = request.POST.get('admin_notes', '').strip()
    
    from django.utils import timezone
    attempt_request.status = 'rejected'
    attempt_request.reviewed_at = timezone.now()
    attempt_request.reviewed_by = request.user
    if admin_notes:
        attempt_request.admin_notes = admin_notes
    attempt_request.save()
    
    messages.success(request, f'Attempt request from {attempt_request.user.username} has been rejected.')
    return redirect('admin_quiz_attempt_requests')

