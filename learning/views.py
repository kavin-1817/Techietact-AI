from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import os
import subprocess
import tempfile
from django.utils.http import url_has_allowed_host_and_scheme

from .models import LearnerProfile, Course, Module, ChatSession, AdminProfile, Quiz, QuizQuestion, QuizOption, UserQuizAttempt, UserAnswer, CourseEnrollment, EnrollmentRequest, QuizAttemptRequest


def _run_python_code(source: str) -> tuple[str, str]:
    """Execute Python source in a temporary file and return stdout/stderr."""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as temp_file:
        temp_file.write(source)
        temp_path = temp_file.name
    try:
        completed = subprocess.run(
            ['python', temp_path],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return completed.stdout, completed.stderr
    except subprocess.TimeoutExpired:
        return '', 'Execution timed out after 5 seconds.'
    except FileNotFoundError:
        return '', 'Python runtime is not available on the server.'
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _run_java_code(source: str) -> tuple[str, str]:
    """Compile and execute Java source inside a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        java_file = os.path.join(temp_dir, 'Main.java')
        with open(java_file, 'w', encoding='utf-8') as file:
            file.write(source)
        try:
            compile_process = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except FileNotFoundError:
            return '', 'Java compiler/runtime is not available on the server.'
        except subprocess.TimeoutExpired:
            return '', 'Compilation timed out after 5 seconds.'
        if compile_process.returncode != 0:
            return '', compile_process.stderr
        try:
            run_process = subprocess.run(
                ['java', '-cp', temp_dir, 'Main'],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return run_process.stdout, run_process.stderr
        except subprocess.TimeoutExpired:
            return '', 'Execution timed out after 5 seconds.'
        except FileNotFoundError:
            return '', 'Java runtime is not available on the server.'


def home(request):
    """Home page - landing page"""
    return render(request, 'learning/home.html')


def about(request):
    """About page"""
    return render(request, 'learning/about.html')


def signup_view(request):
    """User signup view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create learner profile
            LearnerProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'learning/signup.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, 'admin_profile') or user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'learning/login.html')


@login_required
def logout_view(request):
    """Logout the current user and redirect to home"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Dashboard view after login"""
    # Get or create learner profile
    profile, created = LearnerProfile.objects.get_or_create(user=request.user)
    
    # Get recent module sessions
    recent_sessions = (
        ChatSession.objects.filter(user=request.user, module__isnull=False)
        .select_related('module', 'module__course')
        [:5]
    )
    
    # Featured and available courses
    featured_courses = Course.objects.filter(is_featured=True).prefetch_related('modules')[:5]
    all_courses = Course.objects.prefetch_related('modules')[:8]
    
    # Calculate unlocked modules count for the user
    unlocked_modules_count = 0
    if request.user.is_authenticated:
        # Get all enrolled courses
        enrolled_courses = CourseEnrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
        # Get all modules from enrolled courses
        enrolled_modules = Module.objects.filter(course_id__in=enrolled_courses)
        # Count unlocked modules
        for module in enrolled_modules:
            if module.is_unlocked_for_user(request.user):
                unlocked_modules_count += 1
    
    context = {
        'profile': profile,
        'recent_sessions': recent_sessions,
        'featured_courses': featured_courses,
        'all_courses': all_courses,
        'unlocked_modules_count': unlocked_modules_count,
    }
    return render(request, 'learning/dashboard.html', context)


def courses_list(request):
    """List all available courses"""
    courses = Course.objects.prefetch_related('modules').all()
    
    # Check enrollment status and pending requests for logged-in users
    enrolled_course_ids = set()
    pending_request_ids = set()
    if request.user.is_authenticated:
        enrolled_course_ids = set(
            CourseEnrollment.objects.filter(user=request.user)
            .values_list('course_id', flat=True)
        )
        pending_request_ids = set(
            EnrollmentRequest.objects.filter(
                user=request.user,
                status='pending'
            ).values_list('course_id', flat=True)
        )
    
    # Add enrollment status to each course
    for course in courses:
        course.is_enrolled = course.id in enrolled_course_ids
        course.has_pending_request = course.id in pending_request_ids
    
    return render(request, 'learning/courses_list.html', {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids,
    })


def course_detail(request, course_id):
    """Display course details and its modules"""
    course = get_object_or_404(Course.objects.prefetch_related('modules'), id=course_id)
    modules = course.modules.all()
    
    # Check if user is enrolled and pending request status
    is_enrolled = False
    has_pending_request = False
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
        has_pending_request = EnrollmentRequest.objects.filter(
            user=request.user,
            course=course,
            status='pending'
        ).exists()
    
    # Check which modules are unlocked for the user and which have quizzes
    module_status = {}
    module_has_quiz = {}
    module_attempt_info = {}  # Store attempt info for each module
    for module in modules:
        # If user is not enrolled, lock all modules
        if not is_enrolled:
            is_unlocked = False
        else:
            is_unlocked = module.is_unlocked_for_user(request.user)
        # Use integer key - template filter can handle it
        module_status[module.id] = is_unlocked
        # Check if module has a quiz
        module_has_quiz[module.id] = hasattr(module, 'quiz')
        
        # Get attempt information for each module with a quiz
        if is_enrolled and hasattr(module, 'quiz'):
            quiz = module.quiz
            attempt_count = UserQuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
            has_pending_request = QuizAttemptRequest.objects.filter(
                user=request.user,
                quiz=quiz,
                status='pending'
            ).exists()
            has_approved_unused_request = QuizAttemptRequest.objects.filter(
                user=request.user,
                quiz=quiz,
                status='approved',
                used=False
            ).exists()
            
            module_attempt_info[module.id] = {
                'attempt_count': attempt_count,
                'has_pending_request': has_pending_request,
                'has_approved_unused_request': has_approved_unused_request,
                'can_take_quiz': attempt_count < 3 or has_approved_unused_request,
            }
    
    return render(request, 'learning/course_detail.html', {
        'course': course,
        'modules': modules,
        'module_status': module_status,
        'module_has_quiz': module_has_quiz,
        'module_attempt_info': module_attempt_info,
        'is_enrolled': is_enrolled,
        'has_pending_request': has_pending_request,
    })


@login_required
def module_detail(request, module_id):
    """Display a module and interactive learning assistant"""
    module = get_object_or_404(Module.objects.select_related('course'), id=module_id)
    
    # Check if user is enrolled in the course
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=module.course).exists()
    
    if not is_enrolled:
        messages.error(request, 'You must enroll in this course to access its modules.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if module is unlocked for user
    is_unlocked = module.is_unlocked_for_user(request.user)
    course_category = module.course.category
    is_programming_course = course_category == 'programming'
    is_language_course = course_category == 'language'
    
    if not is_unlocked:
        # Get previous module info for lock message
        previous_module = Module.objects.filter(
            course=module.course,
            order=module.order - 1
        ).first()
        
        return render(request, 'learning/module_detail.html', {
            'module': module,
            'is_unlocked': False,
            'previous_module': previous_module,
            'course_category': course_category,
            'is_programming_course': is_programming_course,
            'is_language_course': is_language_course,
        })
    
    # Get the selected topic from query parameter (if any)
    # URL decode it properly (handles double encoding like Print%2520statements)
    from urllib.parse import unquote
    selected_topic_raw = request.GET.get('topic', '').strip()
    selected_topic = unquote(selected_topic_raw) if selected_topic_raw else ''
    # Handle double encoding
    if selected_topic and '%' in selected_topic:
        selected_topic = unquote(selected_topic)
    
    # Filter history by topic if a specific topic is selected
    if selected_topic:
        history = (
            ChatSession.objects.filter(user=request.user, module=module, topic=selected_topic)
            .order_by('created_at')
        )
    else:
        # If no topic selected, show all history (for backward compatibility)
        history = (
            ChatSession.objects.filter(user=request.user, module=module)
            .order_by('created_at')
        )
    
    # Get all topics from the module
    topic_items = []
    if module.topics:
        topic_items = [obj.strip() for obj in module.topics.splitlines() if obj.strip()]
    
    # Get chat history count per topic
    topic_chat_counts = {}
    for topic in topic_items:
        count = ChatSession.objects.filter(user=request.user, module=module, topic=topic).count()
        topic_chat_counts[topic] = count
    
    return render(request, 'learning/module_detail.html', {
        'module': module,
        'history': history,
        'selected_topic': selected_topic,
        'topic_items': topic_items,
        'topic_chat_counts': topic_chat_counts,
        'is_unlocked': True,
        'course_category': course_category,
        'is_programming_course': is_programming_course,
        'is_language_course': is_language_course,
    })


@login_required
def practice_code_lab(request):
    """Interactive coding lab for running Python or Java snippets."""
    languages = {
        'python': {
            'label': 'Python 3.11',
            'boilerplate': 'print("Hello from Techietact Practice Lab!")',
            'note': 'Python code runs with a 5 second timeout. Use print statements to inspect values.',
        },
        'java': {
            'label': 'Java 17',
            'boilerplate': (
                'public class Main {\n'
                '  public static void main(String[] args) {\n'
                '    System.out.println("Hello from Techietact Practice Lab!");\n'
                '  }\n'
                '}'
            ),
            'note': 'Define a public class named Main with a main method.',
        },
    }
    
    def _resolve_previous_url() -> tuple[str | None, str]:
        candidate = request.GET.get('from') or request.META.get('HTTP_REFERER')
        label = request.GET.get('from_label', '').strip() or 'Previous page'
        if candidate and url_has_allowed_host_and_scheme(candidate, allowed_hosts={request.get_host()}):
            return candidate, label
        return None, label
    
    language = request.POST.get('language', 'python')
    if language not in languages:
        language = 'python'
    
    code = request.POST.get('code') or languages[language]['boilerplate']
    output = ''
    error = ''
    executed = False
    
    if request.method == 'POST':
        executed = True
        if language == 'python':
            output, error = _run_python_code(code)
        else:
            output, error = _run_java_code(code)
    
    previous_url, previous_label = _resolve_previous_url()
    
    context = {
        'languages': languages,
        'language_boilerplates': {key: meta['boilerplate'] for key, meta in languages.items()},
        'selected_language_meta': languages[language],
        'selected_language': language,
        'code': code,
        'output': output,
        'error': error,
        'executed': executed,
        'previous_url': previous_url,
        'previous_label': previous_label,
    }
    return render(request, 'learning/practice_code.html', context)


@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
def module_ask_api(request, module_id):
    """API endpoint for module-based AI tutoring"""
    module = get_object_or_404(Module.objects.select_related('course'), id=module_id)
    
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        specific_topic = data.get('topic', '').strip()  # Get specific topic if provided
        
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)
        
        # Get conversation history for this module, user, and specific topic (if provided)
        if specific_topic:
            history = ChatSession.objects.filter(
                user=request.user,
                module=module,
                topic=specific_topic
            ).order_by('created_at')[:10]  # Last 10 messages for context
        else:
            # If no topic specified, get all history for the module
            history = ChatSession.objects.filter(
                user=request.user,
                module=module
            ).order_by('created_at')[:10]  # Last 10 messages for context
        
        response = ask_ai(question, module=module, history=history, specific_topic=specific_topic)
        
        error_indicators = (
            'I encountered an issue', 'Could not', 'I\'ve reached', 'No available',
            'Gemini model not found', '⚠️', '🔑', '🚫', '❌', 'Rate Limit',
            'API Key Error', 'Access Denied', 'Error Generating'
        )
        if any(response.startswith(indicator) for indicator in error_indicators):
            return JsonResponse({
                'response': response,
                'is_error': True,
            })
        
        # Extract suggestions from the response
        suggestions = []
        response_text = response
        
        # Check for suggestions markers (case-insensitive and handle variations)
        start_marker = '[SUGGESTIONS_START]'
        end_marker = '[SUGGESTIONS_END]'
        
        # Find markers (case-insensitive search)
        start_idx = -1
        end_idx = -1
        
        # Try case-sensitive first
        if start_marker in response:
            start_idx = response.find(start_marker)
        if end_marker in response:
            end_idx = response.find(end_marker)
        
        # If not found, try case-insensitive
        if start_idx == -1 or end_idx == -1:
            response_lower = response.lower()
            start_marker_lower = start_marker.lower()
            end_marker_lower = end_marker.lower()
            
            if start_idx == -1 and start_marker_lower in response_lower:
                start_idx = response_lower.find(start_marker_lower)
            if end_idx == -1 and end_marker_lower in response_lower:
                end_idx = response_lower.find(end_marker_lower)
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            # Extract suggestions section
            suggestions_text = response[start_idx + len(start_marker):end_idx].strip()
            # Split by newlines and clean up
            raw_suggestions = suggestions_text.split('\n')
            suggestions = []
            for s in raw_suggestions:
                cleaned = s.strip()
                # Skip empty lines, markers, and invalid entries
                if (cleaned and 
                    cleaned.lower() != start_marker.lower() and 
                    cleaned.lower() != end_marker.lower() and
                    not cleaned.lower().startswith('[suggestions') and 
                    not cleaned.lower().endswith(']') and
                    len(cleaned) > 5):  # Minimum length for a valid suggestion
                    suggestions.append(cleaned)
            
            # Remove the suggestions section from the response text
            response_text = (response[:start_idx] + response[end_idx + len(end_marker):]).strip()
            # Clean up any extra newlines or whitespace
            response_text = response_text.strip()
            # Remove trailing newlines
            while response_text.endswith('\n') or response_text.endswith('\r'):
                response_text = response_text.rstrip('\n\r')
            response_text = response_text.strip()
        
        # CRITICAL: Ensure markers are completely removed from response_text (safety check)
        # Remove any remaining markers that might have slipped through
        import re
        response_text = re.sub(r'\[SUGGESTIONS_START\].*?\[SUGGESTIONS_END\]', '', response_text, flags=re.IGNORECASE | re.DOTALL)
        response_text = re.sub(r'\[SUGGESTIONS_START\]', '', response_text, flags=re.IGNORECASE)
        response_text = re.sub(r'\[SUGGESTIONS_END\]', '', response_text, flags=re.IGNORECASE)
        response_text = response_text.strip()
        
        # Store the full response (with suggestions) in the database for history
        chat_session = ChatSession.objects.create(
            user=request.user,
            module=module,
            topic=specific_topic if specific_topic else '',
            question=question,
            response=response  # Store full response including suggestions for history
        )
        
        return JsonResponse({
            'response': response_text,  # Send cleaned response (without suggestions) to frontend
            'suggestions': suggestions,  # Send suggestions separately
            'timestamp': chat_session.created_at.isoformat(),
        })
    except Exception as exc:
        return JsonResponse({
            'error': 'An unexpected error occurred. Please try again.',
            'details': str(exc),
            'is_error': True
        }, status=500)


@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
def module_delete_memory(request, module_id):
    """Delete all conversation history for a user in a specific module and topic"""
    module = get_object_or_404(Module.objects.select_related('course'), id=module_id)
    
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        
        # Delete chat sessions for this user, module, and topic (if specified)
        if topic:
            deleted_count = ChatSession.objects.filter(
                user=request.user,
                module=module,
                topic=topic
            ).delete()[0]
        else:
            # If no topic specified, delete all sessions for this module
            deleted_count = ChatSession.objects.filter(
                user=request.user,
                module=module
            ).delete()[0]
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} conversation(s).'
        })
    except Exception as exc:
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred while deleting conversation history.',
            'details': str(exc)
        }, status=500)


@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
def module_delete_memory(request, module_id):
    """API endpoint to delete all chat history for a module"""
    module = get_object_or_404(Module, id=module_id)
    
    try:
        # Delete all chat sessions for this user and module
        deleted_count, _ = ChatSession.objects.filter(
            user=request.user,
            module=module
        ).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Chat history deleted successfully',
            'deleted_count': deleted_count
        })
    except Exception as exc:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while deleting chat history.',
            'details': str(exc)
        }, status=500)


@login_required
def take_quiz(request, module_id):
    """Display quiz for a module"""
    module = get_object_or_404(Module.objects.select_related('course'), id=module_id)
    
    # Check if user is enrolled in the course
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=module.course).exists()
    if not is_enrolled:
        messages.error(request, 'You must enroll in this course to access its quizzes.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if module is unlocked
    if not module.is_unlocked_for_user(request.user):
        messages.error(request, 'You must complete the previous module\'s quiz to access this module.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if module has a quiz
    if not hasattr(module, 'quiz'):
        messages.info(request, 'This module does not have a quiz yet.')
        return redirect('module_detail', module_id=module.id)
    
    quiz = module.quiz
    
    # Check if user is admin (admins have unlimited attempts)
    is_admin = request.user.is_staff or hasattr(request.user, 'admin_profile')
    
    # Check attempt limit (max 3 attempts) - skip for admins
    attempt_count = UserQuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    
    # Check if user has an approved and unused request for additional attempts
    approved_request = QuizAttemptRequest.objects.filter(
        user=request.user,
        quiz=quiz,
        status='approved',
        used=False
    ).first()
    
    if not is_admin and attempt_count >= 3 and not approved_request:
        messages.error(request, 'You have reached the maximum number of attempts (3) for this quiz. Please request additional attempts if needed.')
        return redirect('module_detail', module_id=module.id)
    
    # Get questions with options
    questions = quiz.questions.all().prefetch_related('options')
    
    if not questions.exists():
        messages.info(request, 'This quiz does not have any questions yet.')
        return redirect('module_detail', module_id=module.id)
    
    # Calculate remaining attempts (unlimited for admins)
    remaining_attempts = float('inf') if is_admin else (3 - attempt_count)
    
    return render(request, 'learning/take_quiz.html', {
        'module': module,
        'quiz': quiz,
        'questions': questions,
        'attempt_count': attempt_count,
        'remaining_attempts': remaining_attempts,
    })


@login_required
@require_http_methods(['POST'])
def submit_quiz(request, module_id):
    """Submit quiz answers and calculate score"""
    module = get_object_or_404(Module.objects.select_related('course'), id=module_id)
    
    # Check if user is enrolled in the course
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=module.course).exists()
    if not is_enrolled:
        messages.error(request, 'You must enroll in this course to submit quizzes.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if module is unlocked
    if not module.is_unlocked_for_user(request.user):
        messages.error(request, 'You must complete the previous module\'s quiz to access this module.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if module has a quiz
    if not hasattr(module, 'quiz'):
        messages.error(request, 'This module does not have a quiz.')
        return redirect('module_detail', module_id=module.id)
    
    quiz = module.quiz
    questions = quiz.questions.all().prefetch_related('options')
    
    if not questions.exists():
        messages.error(request, 'This quiz does not have any questions.')
        return redirect('module_detail', module_id=module.id)
    
    # Check if user is admin (admins have unlimited attempts)
    is_admin = request.user.is_staff or hasattr(request.user, 'admin_profile')
    
    # Check attempt limit - skip for admins
    attempt_count = UserQuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    
    # Check if user has an approved and unused request for additional attempts
    approved_request = QuizAttemptRequest.objects.filter(
        user=request.user,
        quiz=quiz,
        status='approved',
        used=False
    ).first()
    
    if not is_admin and attempt_count >= 3 and not approved_request:
        messages.error(request, 'You have reached the maximum number of attempts (3) for this quiz. Please request additional attempts if needed.')
        return redirect('module_detail', module_id=module.id)
    
    # Get violation data
    auto_submitted = request.POST.get('auto_submitted') == 'true'
    violation_count = int(request.POST.get('violation_count', 0))
    violation_details = request.POST.get('violation_details', '')
    
    # Calculate score
    total_points = quiz.get_total_points()
    earned_points = 0
    
    # Create quiz attempt
    from django.utils import timezone
    attempt = UserQuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        total_points=total_points,
        earned_points=0,
        score=0,
        passed=False,
        auto_submitted=auto_submitted,
        violation_count=violation_count,
        violation_details=violation_details,
    )
    
    # Process answers
    for question in questions:
        selected_option_id = request.POST.get(f'question_{question.id}')
        
        if selected_option_id:
            try:
                selected_option = QuizOption.objects.get(id=selected_option_id, question=question)
                is_correct = selected_option.is_correct
                
                # Create user answer
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected_option,
                    is_correct=is_correct,
                )
                
                # Add points if correct
                if is_correct:
                    earned_points += question.points
            except QuizOption.DoesNotExist:
                pass
    
    # Calculate score percentage
    score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = score_percentage >= quiz.passing_score
    
    # Update attempt
    attempt.earned_points = earned_points
    attempt.score = score_percentage
    attempt.passed = passed
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # Mark approved request as used if this was an additional attempt
    if not is_admin and attempt_count >= 3:
        approved_request = QuizAttemptRequest.objects.filter(
            user=request.user,
            quiz=quiz,
            status='approved',
            used=False
        ).first()
        if approved_request:
            approved_request.used = True
            approved_request.save()
    
    # Show result
    if auto_submitted:
        messages.error(request, f'Your quiz was automatically submitted due to exam rule violations. Score: {score_percentage:.1f}%')
        if violation_count > 0:
            messages.warning(request, f'Violations detected: {violation_count}. Please review the exam rules before your next attempt.')
    else:
        messages.success(request, f'Quiz completed! Your score: {score_percentage:.1f}%')
    
    if passed:
        messages.success(request, f'Congratulations! You passed with {score_percentage:.1f}%. The next module is now unlocked!')
    else:
        # Check if user is admin
        is_admin = request.user.is_staff or hasattr(request.user, 'admin_profile')
        if is_admin:
            messages.warning(request, f'You scored {score_percentage:.1f}%. You need {quiz.passing_score}% to pass. As an admin, you have unlimited attempts.')
        else:
            remaining = 3 - attempt_count - 1
            if remaining > 0:
                messages.warning(request, f'You scored {score_percentage:.1f}%. You need {quiz.passing_score}% to pass. You have {remaining} attempt(s) remaining.')
            else:
                messages.error(request, f'You scored {score_percentage:.1f}%. You need {quiz.passing_score}% to pass. You have no attempts remaining.')
    
    return render(request, 'learning/quiz_result.html', {
        'module': module,
        'quiz': quiz,
        'attempt': attempt,
        'score_percentage': score_percentage,
        'passed': passed,
        'questions': questions,
    })


@login_required
def request_additional_attempt(request, module_id):
    """Request additional quiz attempt after exhausting 3 attempts"""
    module = get_object_or_404(Module.objects.select_related('course'), id=module_id)
    
    # Check if user is enrolled
    is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=module.course).exists()
    if not is_enrolled:
        messages.error(request, 'You must enroll in this course to request additional attempts.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if module has a quiz
    if not hasattr(module, 'quiz'):
        messages.error(request, 'This module does not have a quiz.')
        return redirect('module_detail', module_id=module.id)
    
    quiz = module.quiz
    
    # Check if user has exhausted attempts
    attempt_count = UserQuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    if attempt_count < 3:
        messages.info(request, 'You still have attempts remaining. You can take the quiz directly.')
        return redirect('take_quiz', module_id=module.id)
    
    # Check if there's already a pending request
    existing_request = QuizAttemptRequest.objects.filter(
        user=request.user,
        quiz=quiz,
        status='pending'
    ).first()
    
    if existing_request:
        messages.info(request, 'You already have a pending request for additional attempts.')
        return redirect('course_detail', course_id=module.course.id)
    
    # Check if there's an approved and unused request
    approved_request = QuizAttemptRequest.objects.filter(
        user=request.user,
        quiz=quiz,
        status='approved',
        used=False
    ).first()
    
    if approved_request:
        messages.success(request, 'Your request for additional attempts has been approved! You can now take the quiz.')
        return redirect('take_quiz', module_id=module.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a reason for requesting additional attempts.')
        else:
            # Create the request
            QuizAttemptRequest.objects.create(
                user=request.user,
                quiz=quiz,
                reason=reason
            )
            messages.success(request, 'Your request for additional attempts has been submitted. An admin will review it shortly.')
            return redirect('course_detail', course_id=module.course.id)
    
    return render(request, 'learning/request_attempt.html', {
        'module': module,
        'quiz': quiz,
        'attempt_count': attempt_count,
    })


def ask_ai(prompt, module=None, history=None, specific_topic=None):
    """
    Gemini API integration for AI responses.
    Uses Google's Gemini model to provide intelligent tutoring responses.
    Teaches step-by-step, topic-by-topic, focusing only on the module's topics.
    
    Args:
        prompt: The user's question or request
        module: The Module object (optional)
        history: List of ChatSession objects for conversation history (optional)
        specific_topic: If provided, teach only this specific topic (optional)
    """
    import os
    from django.conf import settings
    
    # Get API key from settings or environment variable
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        module_line = ""
        if module:
            module_line = (
                f"\n\nCurrent module: {module.title}\n"
                f"Course: {module.course.title}\n"
                f"Summary: {module.summary[:200]}..."
            )
        return (
            f"I'd be happy to help you with '{prompt}'{module_line}! "
            "To enable AI-powered responses, please configure your Gemini API key in the settings. "
            "Once the key is added, Techietact will provide detailed, module-aware lessons powered by Gemini."
        )
    
    try:
        import google.generativeai as genai
        
        course_category = module.course.category if module else None
        is_language_course = course_category == 'language'
        is_programming_course = course_category == 'programming'
        
        def apply_language_overrides(value: str | None) -> str | None:
            """Adjust prompt copy for language-focused courses."""
            if not (is_language_course and value):
                return value
            replacements = [
                ('**Syntax**', '**Sentence Pattern**'),
                ('Syntax', 'Sentence Pattern'),
                ('syntax', 'sentence pattern'),
                ('code syntax', 'sentence pattern'),
                ('code example', 'sample sentence example'),
                ('code examples', 'sample sentences'),
                ('code block', 'example list'),
                ('code blocks', 'example lists'),
                ('code snippets', 'sentence practice examples'),
                ('code snippet', 'sentence practice example'),
                ('If code is involved', 'If structured practice is involved'),
                ('code is involved', 'structured practice is involved'),
                ('code.', 'language pattern.'),
                ('code,', 'language pattern,'),
            ]
            adjusted = value
            for old, new in replacements:
                adjusted = adjusted.replace(old, new)
            return adjusted
        
        def build_category_guidelines() -> str:
            if is_language_course:
                return (
                    "CATEGORY CONTEXT: LANGUAGE & GRAMMAR COURSE\n"
                    "• This module teaches communication, vocabulary, and grammar—not programming.\n"
                    "• Do NOT output programming code, pseudo-code, compilers, or IDE references.\n"
                    "• Interpret any later mention of 'syntax' as 'Sentence Pattern & Rules'.\n"
                    "• Replace programming 'Example' sections with real-world usage sentences, dialogues, or pronunciation cues.\n"
                    "• Provide practice through fill-in-the-blank items, translation prompts, speaking drills, or error corrections.\n"
                    "• Use plain text lists or tables; avoid fenced code blocks entirely.\n"
                    "• If a learner explicitly requests code, politely explain that this course focuses on language mastery and provide language-focused guidance instead.\n"
                    "• When giving feedback, emphasize tone, context, culture, and pronunciation tips.\n\n"
                )
            if is_programming_course:
                return (
                    "CATEGORY CONTEXT: PROGRAMMING COURSE\n"
                    "• Lean into code samples, syntax breakdowns, debugging tips, and real-world engineering scenarios.\n"
                    "• Always provide runnable snippets and highlight best practices for efficiency and readability.\n\n"
                )
            return (
                "CATEGORY CONTEXT: GENERAL LEARNING COURSE\n"
                "• Provide structured explanations tailored to the subject matter without assuming it's programming.\n\n"
            )
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # List all available models and try to find one that works
        model = None
        available_model_names = []
        last_error = None
        
        # First, try gemini-2.0-flash-lite directly (most likely to work)
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
        except Exception:
            try:
                model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
            except Exception:
                pass
        
        # If direct attempt failed, list all available models
        if model is None:
            try:
                # Get list of all available models first
                all_models = list(genai.list_models())
                
                # Collect all models that support generateContent
                supported_models = []
                for m in all_models:
                    if 'generateContent' in m.supported_generation_methods:
                        model_name = m.name
                        model_short = model_name.split('/')[-1] if '/' in model_name else model_name
                        available_model_names.append(model_short)
                        supported_models.append((model_name, model_short))
                
                # Try models in order of preference - gemini-2.0-flash-lite first
                preferred_order = [
                    'gemini-2.0-flash-lite',
                    'gemini-2.0-flash',
                    'gemini-pro',
                    'gemini-1.0-pro',
                    'gemini-1.5-pro',
                    'gemini-1.5-flash',
                ]
                
                # First, try preferred models
                for preferred in preferred_order:
                    for model_name, model_short in supported_models:
                        if preferred.lower() in model_short.lower() or preferred.lower() in model_name.lower():
                            try:
                                # Try with full name first
                                model = genai.GenerativeModel(model_name)
                                break
                            except Exception as e:
                                last_error = e
                                try:
                                    # Try with short name
                                    model = genai.GenerativeModel(model_short)
                                    break
                                except Exception as e2:
                                    last_error = e2
                                    continue
                        if model:
                            break
                    if model:
                        break
                
                # If no preferred model worked, try any available model
                if model is None:
                    for model_name, model_short in supported_models:
                        # Skip experimental models that might have permission issues
                        if 'exp' not in model_short.lower() and 'experimental' not in model_short.lower():
                            try:
                                model = genai.GenerativeModel(model_name)
                                break
                            except Exception as e:
                                last_error = e
                                try:
                                    model = genai.GenerativeModel(model_short)
                                    break
                                except Exception as e2:
                                    last_error = e2
                                    continue
                        if model:
                            break
                
                # Last resort: try all models including experimental ones
                if model is None:
                    for model_name, model_short in supported_models:
                        try:
                            model = genai.GenerativeModel(model_name)
                            break
                        except Exception as e:
                            last_error = e
                            try:
                                model = genai.GenerativeModel(model_short)
                                break
                            except Exception as e2:
                                last_error = e2
                                continue
                        if model:
                            break
            except Exception as list_error:
                # If listing models fails, try direct model initialization with gemini-2.0-flash-lite first
                for test_name in ['gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-pro', 'gemini-1.0-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']:
                    try:
                        model = genai.GenerativeModel(test_name)
                        break
                    except Exception as e:
                        last_error = e
                        continue
                
                if model is None:
                    error_msg = str(list_error)
                if "permission" in error_msg.lower() or "access" in error_msg.lower() or "denied" in error_msg.lower():
                    return (
                        "🔑 API Permission Issue\n\n"
                        "Your API key doesn't have permission to access the requested model. "
                        "Please check your API key permissions at https://makersuite.google.com/app/apikey\n\n"
                        "Common solutions:\n"
                        "• Make sure your API key is enabled\n"
                        "• Check if you need to enable specific models in Google AI Studio\n"
                        "• Try regenerating your API key\n"
                        f"Error: {error_msg[:200]}"
                    )
                return (
                    f"Could not connect to Gemini API. Please check your API key. "
                    f"Error: {error_msg[:200]}"
                )
        
        if model is None:
            error_msg = str(last_error) if last_error else "Unknown error"
            if "permission" in error_msg.lower() or "access" in error_msg.lower() or "denied" in error_msg.lower():
                return (
                    "🔑 API Permission Issue\n\n"
                    "Your API key doesn't have permission to access the available models. "
                    "Please check your API key permissions at https://makersuite.google.com/app/apikey\n\n"
                    f"Available models found: {', '.join(available_model_names[:5]) if available_model_names else 'None'}\n"
                    "Try enabling these models in Google AI Studio or use a different API key."
                )
            return (
                f"Could not find an available Gemini model. "
                f"Available models found: {', '.join(available_model_names[:5]) if available_model_names else 'None'}. "
                f"Error: {error_msg[:200]}"
            )
        
        # Build comprehensive module context
        module_context = ""
        conversation_context = ""
        
        if module:
            # Extract topics from module
            topic_items = []
            if module.topics:
                topic_items = [obj.strip() for obj in module.topics.splitlines() if obj.strip()]
            
            # Extract learning objectives
            objectives = ""
            if module.learning_objectives:
                bullets = [obj.strip() for obj in module.learning_objectives.splitlines() if obj.strip()]
                if bullets:
                    objectives = "\n".join(f"- {b}" for b in bullets)
            
            # Build topics list for teaching
            topics_list = ""
            if topic_items:
                topics_list = "\n".join([f"{i+1}. {topic}" for i, topic in enumerate(topic_items)])
            
            # CRITICAL: If specific_topic is provided, this is a TOPIC-SPECIFIC CHAT
            # The AI must ONLY teach this topic and nothing else
            if specific_topic:
                # URL decode the topic if needed
                from urllib.parse import unquote
                specific_topic = unquote(specific_topic.strip())
                # Handle double encoding
                if '%' in specific_topic:
                    specific_topic = unquote(specific_topic)
                
                # Verify the topic is in the module's topic list - use EXACT match first
                topic_found = False
                exact_topic_name = specific_topic
                
                # First try exact match (case-insensitive)
                for topic in topic_items:
                    if topic.lower().strip() == specific_topic.lower().strip():
                        exact_topic_name = topic  # Use the exact topic name from the list
                        topic_found = True
                        break
                
                # If no exact match, try partial match (but be more strict)
                if not topic_found:
                    for topic in topic_items:
                        # Only match if the specific_topic is a complete word/phrase within the topic
                        topic_lower = topic.lower().strip()
                        specific_lower = specific_topic.lower().strip()
                        # Check if specific_topic matches the beginning or is contained as a whole word
                        if (topic_lower.startswith(specific_lower) or 
                            topic_lower == specific_lower or
                            (specific_lower in topic_lower and len(specific_lower) > 3)):
                            exact_topic_name = topic
                            topic_found = True
                            break
                
                if topic_found:
                    # Build list of other topics to check against
                    other_topics = [t for t in topic_items if t.lower() != exact_topic_name.lower()]
                    other_topics_list = ', '.join([f"'{t}'" for t in other_topics]) if other_topics else 'any other topic'
                    
                    conversation_context = (
                        f"\n\n⚠️⚠️⚠️ CRITICAL: TOPIC-SPECIFIC CHAT SESSION ⚠️⚠️⚠️\n"
                        f"This is a DEDICATED chat session for the topic '{exact_topic_name}' ONLY.\n"
                        f"The student is in a topic-specific chat where you MUST teach ONLY '{exact_topic_name}'.\n"
                        f"\n🚨🚨🚨 ABSOLUTE RESTRICTION - NEVER VIOLATE THIS 🚨🚨🚨\n"
                        f"You are in a chat dedicated to '{exact_topic_name}' ONLY.\n"
                        f"Other topics in this module include: {other_topics_list}\n"
                        f"YOU MUST NEVER teach or explain ANY of these other topics in this chat.\n"
                        f"\nCRITICAL RULES FOR THIS CHAT:\n"
                        f"1. FIRST: Check the student's question - does it mention or ask about '{exact_topic_name}'?\n"
                        f"   - If YES: Teach '{exact_topic_name}' using the full structured format\n"
                        f"   - If NO: The student is asking about a different topic - you MUST redirect them\n"
                        f"2. If the student's question mentions ANY other topic (like {other_topics_list}), "
                        f"you MUST immediately redirect them with this EXACT message:\n"
                        f"   'This chat is dedicated to {exact_topic_name} only. I can only teach {exact_topic_name} here. "
                        f"Please select the topic you want to learn from the sidebar to start a dedicated chat for it.'\n"
                        f"3. DO NOT teach any other topics from the module, even if:\n"
                        f"   - The question mentions them\n"
                        f"   - The question asks to explain them\n"
                        f"   - The question asks 'what is [other topic]'\n"
                        f"   - The question asks 'explain [other topic]'\n"
                        f"   - The question asks 'teach me [other topic]'\n"
                        f"   - The question asks about differences between topics\n"
                        f"   - The question asks to compare topics\n"
                        f"   In ALL these cases, redirect them to use the sidebar.\n"
                        f"4. DO NOT mention other topics unless redirecting the student\n"
                        f"5. Focus ALL your responses on '{exact_topic_name}' and related concepts ONLY\n"
                        f"6. The conversation history you see is ONLY for '{exact_topic_name}' - do not reference other topics\n"
                        f"7. DO NOT say 'shall we move to the next topic' - this is a topic-specific chat, there is no 'next topic'\n"
                        f"8. Instead of asking about next topics, drive the conversation naturally by:\n"
                        f"   - Asking if they understood the concept\n"
                        f"   - Asking if they want to practice with examples\n"
                        f"   - Asking if they have questions about specific aspects\n"
                        f"   - Suggesting related concepts within this topic\n"
                        f"   - Checking their understanding with questions\n"
                        f"\nTOPIC DETECTION LOGIC:\n"
                        f"Before responding, check if the student's question mentions:\n"
                        f"- '{exact_topic_name}' or variations → Teach '{exact_topic_name}'\n"
                        f"- Any other topic from the module → Redirect immediately\n"
                        f"- Generic questions about programming → Relate to '{exact_topic_name}' only\n"
                        f"- Questions about 'data types', 'operators', 'variables', 'string operations', 'type casting' → Redirect\n"
                        f"\nRESPONSE FORMAT (ONLY if question is about '{exact_topic_name}'):\n"
                        f"When teaching '{exact_topic_name}', use the COMPLETE full structured format:\n"
                        f"1. Topic introduction (e.g., 'Let's learn about {exact_topic_name}')\n"
                        f"2. Brief overview of what {exact_topic_name} is and why it's important\n"
                        f"3. **Explanation** (as bold header) - detailed step-by-step explanation of {exact_topic_name}\n"
                        f"4. **Real World Example** (as bold header) - real-world analogy for {exact_topic_name}\n"
                        f"5. **Syntax** (as bold header) - code syntax for {exact_topic_name}\n"
                        f"6. **Example** (as bold header) - code example demonstrating {exact_topic_name}\n"
                        f"7. Natural conversational closing - ask engaging questions to continue the conversation\n"
                        f"   Examples of good closings:\n"
                        f"   - 'Does this make sense? Try writing a simple example yourself and see how it works!'\n"
                        f"   - 'What part would you like to explore more? We can dive deeper into any aspect.'\n"
                        f"   - 'Want to practice? I can give you a small exercise to test your understanding.'\n"
                        f"   - 'Any questions about {exact_topic_name}? Feel free to ask - I'm here to help!'\n"
                        f"   - 'How do you think you'd use this in a real project? Let's discuss some practical scenarios.'\n"
                        f"   DO NOT say: 'Shall we move to the next topic?' or 'Do you want to learn the next topic?'\n"
                        f"\nCRITICAL ORDER: Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Natural Conversational Closing\n"
                        f"CRITICAL: You MUST use **Explanation**, **Real World Example**, **Syntax**, and **Example** as bold headers.\n"
                        f"CRITICAL: Stay focused on '{exact_topic_name}' - this is a dedicated chat for this topic only.\n"
                        f"CRITICAL: Be conversational, engaging, and drive the conversation naturally like a real tutor would.\n"
                        f"\n🚨 FINAL REMINDER: If the student asks about ANY topic other than '{exact_topic_name}', "
                        f"redirect them immediately. DO NOT teach that topic. DO NOT explain it. Just redirect.\n"
                    )
                else:
                    # Topic not found in list, but still try to teach it
                    conversation_context = (
                        f"\n\n⚠️ IMPORTANT: TOPIC-SPECIFIC CHAT SESSION\n"
                        f"This is a dedicated chat for '{specific_topic}'.\n"
                        f"Note: This topic may not be in the module's official topic list, but teach it anyway.\n"
                        f"Focus ONLY on '{specific_topic}' in this chat. Do not teach other topics.\n"
                        f"Use the full structured format to teach '{specific_topic}' completely.\n"
                    )
            
            # Build conversation history context
            if history and len(history) > 0 and not specific_topic:
                covered_topics = []
                conversation_summary = []
                last_ai_response = ""
                current_topic_being_discussed = ""
                
                # Process history in reverse to get the most recent first
                for session in reversed(history):
                    # Try to identify which topics were discussed
                    q_lower = session.question.lower()
                    r_lower = session.response.lower()
                    for topic in topic_items:
                        topic_lower = topic.lower()
                        # More comprehensive matching - check if topic appears in question or response
                        if (topic_lower in q_lower or topic_lower in r_lower or 
                            any(word in q_lower or word in r_lower for word in topic_lower.split() if len(word) > 3)):
                            if topic not in covered_topics:
                                covered_topics.append(topic)
                            # Track the most recent topic being discussed (from most recent session)
                            if not current_topic_being_discussed:
                                current_topic_being_discussed = topic
                    
                    # Get the last AI response (most recent) - get more context
                    if not last_ai_response:
                        last_ai_response = session.response[:500]  # Last 500 chars for better context
                    
                    conversation_summary.append(f"Student: {session.question[:80]}... | AI: {session.response[:80]}...")
                
                # Reverse back to chronological order for display
                conversation_summary.reverse()
                
                # Detect if user is responding to AI's question and what type of response
                prompt_lower = prompt.lower()
                is_follow_up_to_ai_question = False
                wants_more_details = False
                wants_next_topic = False
                
                if last_ai_response:
                    last_response_lower = last_ai_response.lower()
                    
                    # Check if AI already informed about module completion
                    completion_indicators = [
                        'covered all the topics', 'all topics in this module', 'complete the graded quiz',
                        'unlock the next module', 'all topics are covered', 'all topics have been covered',
                        'we\'ve covered all', 'completed all topics', 'finished all topics'
                    ]
                    ai_already_said_completed = any(indicator in last_response_lower for indicator in completion_indicators)
                    
                    # Check if AI asked to START WITH a specific topic (not move to next)
                    start_with_indicators = [
                        'shall we start with', 'start with', 'let\'s start with', 'we\'ll start with',
                        'begin with', 'let\'s begin with', 'we can start with', 'should we start with'
                    ]
                    ai_asked_to_start_with = any(indicator in last_response_lower for indicator in start_with_indicators)
                    
                    # Check if AI asked about moving to next topic
                    next_topic_indicators = [
                        'shall we move', 'move to the next', 'next topic', 'move on to',
                        'proceed to', 'continue with', 'shall we continue', 'ready to move',
                        'move forward', 'next in our list'
                    ]
                    ai_asked_about_next_topic = any(indicator in last_response_lower for indicator in next_topic_indicators)
                    
                    # Check if user is directly asking to move to next topic (even if AI didn't ask)
                    user_wants_next_indicators = [
                        'move to next', 'next one', 'next topic', 'move on', 'proceed to next',
                        'continue to next', 'go to next', 'next please', 'move forward',
                        'let\'s move to next', 'move to the next one'
                    ]
                    user_directly_wants_next = any(indicator in prompt_lower for indicator in user_wants_next_indicators)
                    
                    # Check if AI asked about needing more explanation/details
                    more_details_indicators = [
                        'do you need more', 'need more explanation', 'want more', 'any doubts',
                        'need more details', 'want explanation', 'more explanation', 'does that help',
                        'any questions about', 'need clarification', 'want to learn more about'
                    ]
                    ai_asked_about_more_details = any(indicator in last_response_lower for indicator in more_details_indicators)
                    
                    # Check if AI offered to provide solutions/answers to assignments
                    solutions_indicators = [
                        'i can provide', 'provide the solutions', 'check your answers', 'when you\'re ready',
                        'solutions if you', 'answers if you', 'show you the solutions', 'give you the solutions',
                        'provide solutions', 'show solutions', 'give solutions', 'here are the solutions',
                        'ready to check', 'ready to see', 'want to check', 'want to see the solutions'
                    ]
                    ai_offered_solutions = any(indicator in last_response_lower for indicator in solutions_indicators)
                    
                    # Check if AI asked about providing assignments/exercises
                    assignments_indicators = [
                        'give you assignments', 'provide assignments', 'give assignments', 'practice problems',
                        'give exercises', 'provide exercises', 'practice exercises', 'assignments on',
                        'exercises on', 'practice on', 'want assignments', 'need assignments'
                    ]
                    ai_asked_about_assignments = any(indicator in last_response_lower for indicator in assignments_indicators)
                    
                    # Check if AI just gave exercises/assignments (not just asked about them)
                    ai_gave_exercises_indicators = [
                        'here are', 'here\'s', 'exercises to test', 'practice problems', 'try these',
                        'write a program', 'exercise', 'assignment', 'problem', 'practice',
                        'simple print', 'printing numbers', 'test your understanding'
                    ]
                    ai_just_gave_exercises = any(indicator in last_response_lower for indicator in ai_gave_exercises_indicators) and (
                        'exercise' in last_response_lower or 'assignment' in last_response_lower or 
                        'problem' in last_response_lower or 'practice' in last_response_lower
                    )
                    
                    # Check if user is directly asking for solutions (including typos)
                    user_wants_solutions_indicators = [
                        'give solution', 'give solutions', 'show solution', 'show solutions',
                        'provide solution', 'provide solutions', 'i want solution', 'i want solutions',
                        'need solution', 'need solutions', 'solution', 'solutions', 'soulution', 'soulutions',
                        'answer', 'answers', 'check answer', 'check answers'
                    ]
                    user_directly_wants_solutions = any(indicator in prompt_lower for indicator in user_wants_solutions_indicators)
                    
                    # Check if user is saying yes/agreeing
                    user_yes_indicators = [
                        'yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'alright', 'fine',
                        'go ahead', 'proceed', 'continue', 'let\'s go', 'let\'s do it'
                    ]
                    user_said_yes = any(indicator in prompt_lower for indicator in user_yes_indicators)
                    
                    # Check if user wants more details
                    user_wants_more_indicators = [
                        'i need', 'i want', 'give me', 'show me', 'explain', 'more', 'detailed',
                        'with examples', 'with code', 'real life', 'analogy', 'more explanation',
                        'more details', 'deeper', 'expand'
                    ]
                    user_wants_more = any(indicator in prompt_lower for indicator in user_wants_more_indicators)
                    
                    # Determine the intent
                    # CRITICAL: Check what the AI's last question/offer was about
                    wants_solutions = False
                    wants_assignments = False
                    wants_to_start_topic = False
                    topic_to_start = None
                    
                    # CRITICAL: If user said yes, detect intent based on last AI message FIRST
                    # This must run BEFORE other priority checks to ensure "yes" is interpreted correctly
                    if user_said_yes and last_ai_response:
                        last_response_lower = last_ai_response.lower()
                        # Force intent based on what AI asked/offered
                        if 'solution' in last_response_lower or 'solutions' in last_response_lower:
                            wants_solutions = True
                            is_follow_up_to_ai_question = True
                        elif 'assignment' in last_response_lower or 'exercise' in last_response_lower or 'practice' in last_response_lower:
                            if 'solution' not in last_response_lower:  # Only if AI didn't offer solutions
                                wants_assignments = True
                                is_follow_up_to_ai_question = True
                        elif 'move to the next' in last_response_lower or 'next topic' in last_response_lower:
                            wants_next_topic = True
                            is_follow_up_to_ai_question = True
                        elif 'more explanation' in last_response_lower or 'more details' in last_response_lower or 'need more' in last_response_lower:
                            wants_more_details = True
                            is_follow_up_to_ai_question = True
                    
                    # PRIORITY 1: Check if user directly asked for solutions (including typos like "soulutions")
                    if user_directly_wants_solutions:
                        wants_solutions = True
                        is_follow_up_to_ai_question = True
                    # PRIORITY 2: Check if AI offered solutions and user said yes
                    elif ai_offered_solutions and user_said_yes:
                        wants_solutions = True
                        is_follow_up_to_ai_question = True
                    # PRIORITY 3: Check if AI just gave exercises and user said yes (they want solutions to those exercises)
                    elif ai_just_gave_exercises and user_said_yes:
                        wants_solutions = True
                        is_follow_up_to_ai_question = True
                    # PRIORITY 4: Check if AI asked about assignments and user said yes
                    elif ai_asked_about_assignments and user_said_yes:
                        wants_assignments = True
                        is_follow_up_to_ai_question = True
                    # PRIORITY 5: Check if AI asked to START WITH a topic
                    elif ai_asked_to_start_with and user_said_yes:
                        # AI asked "Shall we start with [topic]?" and user said yes
                        # Extract the topic name from the AI's question
                        import re
                        # Look for topic names in the last AI response
                        for topic in topic_items:
                            topic_lower = topic.lower()
                            if topic_lower in last_response_lower:
                                topic_to_start = topic
                                wants_to_start_topic = True
                                is_follow_up_to_ai_question = True
                                break
                        # If no specific topic found, use first topic in list
                        if not topic_to_start and topic_items:
                            topic_to_start = topic_items[0]
                            wants_to_start_topic = True
                            is_follow_up_to_ai_question = True
                    
                    # First check: if AI already said all topics are completed, and user asks to move forward again
                    all_topics_covered_forced = False
                    if wants_solutions:
                        # User wants solutions to assignments - handled separately below
                        pass
                    elif wants_assignments:
                        # User wants assignments - handled separately below
                        pass
                    elif ai_already_said_completed and (user_said_yes or 'move' in prompt_lower or 'next' in prompt_lower):
                        # User is asking to move forward again after completion message
                        wants_next_topic = True
                        is_follow_up_to_ai_question = True
                        # Force all_topics_covered to True so it repeats the completion message
                        all_topics_covered_forced = True
                    elif wants_to_start_topic:
                        # User said yes to STARTING with a topic - teach that topic, don't move to next
                        # This is handled separately below
                        pass
                    elif user_directly_wants_next:
                        # User is directly asking to move to next topic (e.g., "move to next one", "next topic")
                        # This takes priority - they want to move forward
                        wants_next_topic = True
                        is_follow_up_to_ai_question = True
                    elif ai_asked_about_next_topic and user_said_yes:
                        # User said yes to moving to next topic (responding to AI's question)
                        wants_next_topic = True
                        is_follow_up_to_ai_question = True
                    elif ai_asked_about_more_details and (user_said_yes or user_wants_more):
                        # User wants more details on current topic
                        wants_more_details = True
                        is_follow_up_to_ai_question = True
                    elif ai_asked_about_next_topic and user_wants_more:
                        # Edge case: AI asked about next topic but user wants more on current
                        wants_more_details = True
                        is_follow_up_to_ai_question = True
                    elif (ai_asked_about_more_details or ai_asked_about_next_topic) and user_said_yes:
                        # Generic yes response - need to check context
                        is_follow_up_to_ai_question = True
                        # Default to what AI asked about
                        if ai_asked_about_next_topic:
                            wants_next_topic = True
                        elif ai_asked_about_more_details:
                            wants_more_details = True
                
                if covered_topics:
                    conversation_context = (
                        f"\n\nCONVERSATION HISTORY:\n"
                        f"This is a RETURNING user with previous learning sessions.\n"
                        f"Topics already covered in previous sessions: {', '.join(covered_topics)}\n"
                    )
                    
                    if current_topic_being_discussed:
                        conversation_context += f"Current topic being discussed: {current_topic_being_discussed}\n"
                    
                    if last_ai_response:
                        conversation_context += f"\nYour last response ended with: \"{last_ai_response[-150:]}...\"\n"
                    
                    # Check if user directly asked for solutions (even if not a follow-up)
                    if user_directly_wants_solutions and not is_follow_up_to_ai_question:
                        # User directly asked for solutions without AI prompting
                        conversation_context += (
                            f"\n⚠️ CRITICAL: The student DIRECTLY ASKED for SOLUTIONS.\n"
                            f"The student said: '{prompt}'\n"
                            f"This is a DIRECT REQUEST for solutions to assignments/exercises.\n"
                            f"RESPONSE: Provide the SOLUTIONS/ANSWERS to any assignments/exercises you gave earlier in this conversation.\n"
                            f"If you haven't given exercises yet, provide solutions to common practice problems for the current topic.\n"
                            f"DO NOT give new exercises. DO NOT re-explain the topic. DO NOT start teaching again.\n"
                            f"DO NOT use the full structured format.\n"
                            f"Just provide:\n"
                            f"1. The solutions/answers to exercises/assignments\n"
                            f"2. Brief explanations for each solution if helpful\n"
                            f"3. Code examples showing the solutions\n"
                            f"4. A natural closing asking if they understood or have questions about the solutions\n"
                            f"CRITICAL: This is about SOLUTIONS, not exercises, not teaching. Provide solutions directly.\n"
                        )
                    
                    if is_follow_up_to_ai_question:
                        if wants_solutions:
                            # User wants solutions - either directly asked or said yes after AI offered/gave exercises
                            if user_directly_wants_solutions:
                                # User directly asked for solutions (e.g., "give solutions", "show solutions")
                                conversation_context += (
                                    f"\n⚠️ CRITICAL: The student DIRECTLY ASKED for SOLUTIONS.\n"
                                    f"The student said: '{prompt}'\n"
                                    f"This is a DIRECT REQUEST for solutions to assignments/exercises.\n"
                                    f"RESPONSE: Provide the SOLUTIONS/ANSWERS to the assignments/exercises you previously gave.\n"
                                    f"DO NOT give new exercises. DO NOT re-explain the topic. DO NOT start teaching again.\n"
                                    f"DO NOT use the full structured format.\n"
                                    f"Just provide:\n"
                                    f"1. The solutions/answers to each assignment/exercise you gave earlier\n"
                                    f"2. Brief explanations for each solution if helpful\n"
                                    f"3. Code examples showing the solutions\n"
                                    f"4. A natural closing asking if they understood or have questions about the solutions\n"
                                    f"CRITICAL: This is about SOLUTIONS, not exercises, not teaching. Provide solutions directly.\n"
                                )
                            elif ai_just_gave_exercises:
                                # AI just gave exercises and user said yes - they want solutions to those exercises
                                conversation_context += (
                                    f"\n⚠️ CRITICAL: You just gave EXERCISES/ASSIGNMENTS, and the student said YES.\n"
                                    f"Your last response gave exercises/assignments to practice.\n"
                                    f"The student said 'yes' - they want to see the SOLUTIONS to those exercises NOW.\n"
                                    f"RESPONSE: Provide the SOLUTIONS/ANSWERS to the exercises you just gave.\n"
                                    f"DO NOT give new exercises. DO NOT re-explain the topic. DO NOT start teaching again.\n"
                                    f"DO NOT use the full structured format.\n"
                                    f"Just provide:\n"
                                    f"1. The solutions/answers to each exercise you just gave\n"
                                    f"2. Brief explanations for each solution if helpful\n"
                                    f"3. Code examples showing the solutions\n"
                                    f"4. A natural closing asking if they understood or have questions about the solutions\n"
                                    f"CRITICAL: This is about SOLUTIONS to the exercises you just gave, not more exercises, not teaching. Provide solutions directly.\n"
                                )
                            else:
                                # AI offered solutions and user said yes
                                conversation_context += (
                                    f"\n⚠️ CRITICAL: The student said YES to getting SOLUTIONS to the assignments you provided.\n"
                                    f"Your last response offered: 'I can provide the solutions if you'd like to check your answers. Just let me know when you're ready!'\n"
                                    f"The student said 'yes' - they want to see the SOLUTIONS NOW.\n"
                                    f"RESPONSE: Provide the SOLUTIONS/ANSWERS to the assignments/exercises you previously gave.\n"
                                    f"DO NOT re-explain the topic. DO NOT start teaching again.\n"
                                    f"DO NOT use the full structured format.\n"
                                    f"Just provide:\n"
                                    f"1. The solutions/answers to each assignment/exercise\n"
                                    f"2. Brief explanations for each solution if helpful\n"
                                    f"3. Code examples showing the solutions\n"
                                    f"4. A natural closing asking if they understood or have questions about the solutions\n"
                                    f"CRITICAL: This is about SOLUTIONS, not teaching the topic again. Provide solutions directly.\n"
                                )
                        elif wants_assignments:
                            # User said yes to getting assignments
                            conversation_context += (
                                f"\n⚠️ CRITICAL: The student said YES to getting ASSIGNMENTS/EXERCISES.\n"
                                f"Your last response asked about providing assignments, and the student agreed.\n"
                                f"RESPONSE: Provide PRACTICE PROBLEMS/ASSIGNMENTS/EXERCISES for the current topic.\n"
                                f"DO NOT re-explain the topic. DO NOT use the full structured format.\n"
                                f"Just provide:\n"
                                f"1. A set of practice problems/assignments/exercises related to the current topic\n"
                                f"2. Different difficulty levels if appropriate\n"
                                f"3. Clear instructions for each problem\n"
                                f"4. Offer to provide solutions when they're ready\n"
                                f"CRITICAL: This is about ASSIGNMENTS, not teaching the topic again. Provide assignments directly.\n"
                            )
                        elif wants_to_start_topic and topic_to_start:
                            # User said yes to STARTING with a topic - teach that topic now
                            conversation_context += (
                                f"\n⚠️ CRITICAL: The student said YES to STARTING with '{topic_to_start}'.\n"
                                f"Your last response asked 'Shall we start with {topic_to_start}?' and the student agreed.\n"
                                f"RESPONSE: Start teaching '{topic_to_start}' NOW using the full structured format.\n"
                                f"DO NOT move to the next topic. DO NOT skip this topic.\n"
                                f"Teach '{topic_to_start}' completely from scratch:\n"
                                f"1. Topic introduction (e.g., 'Let's learn about {topic_to_start}')\n"
                                f"2. Brief overview\n"
                                f"3. **Explanation** (as bold header) - detailed explanation\n"
                                f"4. **Real World Example** (as bold header) - real-world analogy\n"
                                f"5. **Syntax** (as bold header) - code syntax\n"
                                f"6. **Example** (as bold header) - code example in code block\n"
                                f"7. Closing message asking if they need more or want to move to next topic\n"
                                f"CRITICAL: This is the FIRST time teaching this topic. Treat it as completely new.\n"
                                f"CRITICAL ORDER: Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Closing\n"
                                f"CRITICAL: You MUST use **Explanation**, **Real World Example**, **Syntax**, and **Example** as bold headers.\n"
                            )
                        elif wants_next_topic:
                            # Find the next topic in the list - ALWAYS follow sequential order
                            next_topic = None
                            all_topics_covered = False
                            
                            # Check if completion was already mentioned (force repeat)
                            if all_topics_covered_forced:
                                all_topics_covered = True
                            elif topic_items:
                                # STRICT CHECK: Only mark all topics covered if ALL topics are actually covered
                                # Check if every topic in the list is in covered_topics
                                all_topics_in_covered = all(topic.lower() in [t.lower() for t in covered_topics] for topic in topic_items)
                                
                                if all_topics_in_covered and len(covered_topics) >= len(topic_items):
                                    # All topics are actually covered
                                    all_topics_covered = True
                                elif current_topic_being_discussed:
                                    try:
                                        current_index = topic_items.index(current_topic_being_discussed)
                                        # CRITICAL: Always move to the IMMEDIATE next topic in sequence
                                        # Do NOT skip topics, even if they appear in covered_topics
                                        # The user wants to move forward sequentially
                                        if current_index >= len(topic_items) - 1:
                                            # We're on the last topic - check if all topics are covered
                                            if (current_topic_being_discussed in covered_topics and 
                                                all_topics_in_covered):
                                                all_topics_covered = True
                                            else:
                                                # Last topic not fully covered yet, but we're already on last
                                                all_topics_covered = True
                                        else:
                                            # Not on last topic - ALWAYS move to immediate next topic (current_index + 1)
                                            # This ensures we follow the exact order and don't skip any topics
                                            next_topic = topic_items[current_index + 1]
                                            # DO NOT check if it's covered - always teach it if user wants to move forward
                                    except (ValueError, IndexError):
                                        # Current topic not found in list - find first topic that hasn't been covered
                                        # But still follow sequential order - find first uncovered topic starting from beginning
                                        for i, topic in enumerate(topic_items):
                                            if topic.lower() not in [t.lower() for t in covered_topics]:
                                                next_topic = topic
                                                break
                                        if not next_topic:
                                            all_topics_covered = True
                                else:
                                    # No current topic identified - find first uncovered topic in order
                                    for i, topic in enumerate(topic_items):
                                        if topic.lower() not in [t.lower() for t in covered_topics]:
                                            next_topic = topic
                                            break
                                    if not next_topic:
                                        # All topics are covered
                                        all_topics_covered = True
                            
                            if all_topics_covered:
                                # Check if we already told them about completion
                                if ai_already_said_completed:
                                    conversation_context += (
                                        f"\n⚠️ CRITICAL: The student is asking to move to the next topic AGAIN, but you already informed them that ALL TOPICS ARE COVERED.\n"
                                        f"Your last response already told them to complete the graded quiz.\n"
                                        f"Topics already covered: {', '.join(covered_topics) if covered_topics else 'All topics'}\n"
                                        f"RESPONSE: Politely remind them again that all topics are covered and they need to complete the graded quiz.\n"
                                        f"Say ONLY: 'As I mentioned, we've covered all the topics in this module. "
                                        f"To unlock the next module, please complete the graded quiz. Good luck!'\n"
                                        f"CRITICAL RULES:\n"
                                        f"- DO NOT mention any specific topics (like 'Variables and data types' or any other topic)\n"
                                        f"- DO NOT say 'the next topic is...' or 'let's learn about...'\n"
                                        f"- DO NOT teach any more topics\n"
                                        f"- DO NOT repeat the full topic list\n"
                                        f"- Just remind them about completing the quiz\n"
                                        f"- Keep it short and clear\n"
                                    )
                                else:
                                    conversation_context += (
                                        f"\n⚠️ IMPORTANT: The student wants to move to the next topic, but ALL TOPICS IN THIS MODULE HAVE BEEN COVERED.\n"
                                        f"Topics covered: {', '.join(covered_topics) if covered_topics else 'All topics'}\n"
                                        f"Total topics in module: {len(topic_items) if topic_items else 0}\n"
                                        f"RESPONSE: Tell the student that all topics in this module have been covered.\n"
                                        f"Say: 'Great! We've covered all the topics in this module: [list topics]. "
                                        f"To unlock the next module, please complete the graded quiz. Good luck!'\n"
                                        f"DO NOT teach any more topics. DO NOT say 'CLOSING MESSAGE:' - just write the message naturally.\n"
                                    )
                            elif next_topic:
                                conversation_context += (
                                    f"\n⚠️ CRITICAL: The student said YES to moving to the NEXT topic.\n"
                                    f"Your last response asked about moving to the next topic, and the student agreed.\n"
                                    f"CURRENT TOPIC: {current_topic_being_discussed}\n"
                                    f"NEXT TOPIC TO TEACH: {next_topic}\n"
                                    f"RESPONSE: Start teaching '{next_topic}' NOW using the COMPLETE full structured format.\n"
                                    f"DO NOT just announce the topic name. DO NOT just say 'Let's move to {next_topic}'.\n"
                                    f"You MUST provide the FULL lesson with ALL sections:\n"
                                    f"1. Topic introduction (e.g., 'Let's learn about {next_topic}')\n"
                                    f"2. Brief overview of what {next_topic} is and why it's important\n"
                                    f"3. **Explanation** (as bold header) - detailed step-by-step explanation of {next_topic}\n"
                                    f"4. **Real World Example** (as bold header) - real-world analogy for {next_topic}\n"
                                    f"5. **Syntax** (as bold header) - code syntax for {next_topic}\n"
                                    f"6. **Example** (as bold header) - code example demonstrating {next_topic}\n"
                                    f"7. Closing message asking if they need more or want to move to next topic\n"
                                    f"CRITICAL: This is a NEW topic. Teach it completely from scratch using the full format.\n"
                                    f"CRITICAL ORDER: Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Closing\n"
                                    f"DO NOT skip any sections. DO NOT just announce the topic - TEACH IT COMPLETELY.\n"
                                )
                            else:
                                conversation_context += (
                                    f"\n⚠️ CRITICAL: The student said YES to moving to the NEXT topic.\n"
                                    f"Your last response asked about moving to the next topic, and the student agreed.\n"
                                    f"RESPONSE: Identify the next topic from the module's topic list and TEACH IT COMPLETELY.\n"
                                    f"DO NOT just announce the topic name. DO NOT just say 'Let's move to [topic]'.\n"
                                    f"You MUST provide the FULL lesson with ALL sections:\n"
                                    f"1. Topic introduction\n"
                                    f"2. Brief overview\n"
                                    f"3. **Explanation** (as bold header) - detailed explanation\n"
                                    f"4. **Real World Example** (as bold header) - real-world analogy\n"
                                    f"5. **Syntax** (as bold header) - code syntax\n"
                                    f"6. **Example** (as bold header) - code example\n"
                                    f"7. Closing message\n"
                                    f"CRITICAL ORDER: Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Closing\n"
                                    f"DO NOT skip any sections. DO NOT just announce - TEACH THE TOPIC COMPLETELY.\n"
                                )
                        elif wants_more_details:
                            conversation_context += (
                                f"\n⚠️ IMPORTANT: The student wants MORE DETAILS on the CURRENT topic.\n"
                                f"The student is asking for more explanation, examples, or details on the topic you were just discussing.\n"
                                f"DO NOT move to the next topic. Instead, provide a deeper/more detailed explanation of the CURRENT topic.\n"
                                f"Stay on the same topic ({current_topic_being_discussed if current_topic_being_discussed else 'the current topic'}) and expand on it with more examples, code, or real-life analogies as requested.\n"
                            )
                        else:
                            conversation_context += (
                                f"\n⚠️ IMPORTANT: The student's current question appears to be a RESPONSE to your previous question.\n"
                                f"Check what you asked - if you asked about moving to next topic, then move forward.\n"
                                f"If you asked about needing more explanation, then provide more details on the current topic.\n"
                            )
                    
                    conversation_context += f"\nRecent conversation flow:\n"
                    for i, summary in enumerate(conversation_summary[-4:], 1):
                        conversation_context += f"{i}. {summary}\n"
                    conversation_context += f"\nYou can reference these topics and build upon them.\n"
                else:
                    # History exists but no topics identified - treat as new to this module
                    conversation_context = (
                        f"\n\n⚠️⚠️⚠️ CRITICAL USER STATUS ⚠️⚠️⚠️\n"
                        f"This user has previous conversations but NO topics from this module have been covered yet.\n"
                        f"This could mean:\n"
                        f"1. The user just deleted their memory and is starting fresh\n"
                        f"2. This is the first time the user is interacting with this specific module\n"
                        f"\nCRITICAL RULES - YOU MUST FOLLOW THESE:\n"
                        f"• Treat this as a COMPLETELY NEW user for this specific module\n"
                        f"• Do NOT assume ANY topics have been covered\n"
                        f"• Do NOT say phrases like: 'you already learned', 'we already covered', 'you've learned this before', 'since you've already learned', 'as we discussed', 'remember when', 'like before', 'you know', 'you're familiar with'\n"
                        f"• Start from the beginning and teach each topic as if it's the FIRST time\n"
                        f"• Use phrases like: 'Let's learn', 'I'll teach you', 'Here's how', 'Let me explain', 'We'll start with'\n"
                        f"• If the student asks about a topic, teach it completely from scratch\n"
                        f"• Never reference previous learning that doesn't exist\n"
                    )
                    if last_ai_response:
                        conversation_context += f"\nYour last response: \"{last_ai_response[-150:]}...\"\n"
                    if is_follow_up_to_ai_question:
                        if wants_next_topic:
                            conversation_context += (
                                f"\n⚠️ IMPORTANT: The student said YES to moving to the NEXT topic.\n"
                                f"MOVE TO THE NEXT TOPIC in the module's topic list. Do NOT repeat the current topic.\n"
                            )
                        elif wants_more_details:
                            conversation_context += (
                                f"\n⚠️ IMPORTANT: The student wants MORE DETAILS on the CURRENT topic.\n"
                                f"Provide more details on what you were just discussing, don't move to a new topic.\n"
                            )
                        else:
                            conversation_context += (
                                f"\n⚠️ IMPORTANT: The student's question appears to be responding to your previous question.\n"
                                f"Check what you asked and respond appropriately.\n"
                            )
                    conversation_context += f"\nRecent conversation:\n"
                    for i, summary in enumerate(conversation_summary[-3:], 1):
                        conversation_context += f"{i}. {summary}\n"
            else:
                # No history - this is a completely new user OR memory was just deleted
                conversation_context = (
                    f"\n\n⚠️⚠️⚠️ CRITICAL USER STATUS ⚠️⚠️⚠️\n"
                    f"This is a NEW USER with NO previous conversation history for this module.\n"
                    f"This could be:\n"
                    f"1. A brand new user starting this module for the first time\n"
                    f"2. A user who just deleted their chat memory and is starting fresh\n"
                    f"\nCRITICAL RULES - YOU MUST FOLLOW THESE:\n"
                    f"• Do NOT assume ANY topics have been covered\n"
                    f"• Do NOT say phrases like: 'you already learned', 'we already covered', 'you've learned this before', 'since you've already learned', 'as we discussed', 'remember when', 'like before', 'you know', 'you're familiar with'\n"
                    f"• Start from the beginning and teach each topic as if it's the FIRST time\n"
                    f"• Use phrases like: 'Let's learn', 'I'll teach you', 'Here's how', 'Let me explain', 'We'll start with'\n"
                    f"• If the student asks about a topic, teach it completely from scratch\n"
                    f"• Never reference previous learning that doesn't exist\n"
                    f"• Treat every question as if the student is seeing this concept for the first time\n"
                )
            
            module_context = (
                f"\n{'='*60}\n"
                f"MODULE INFORMATION - UNDERSTAND THIS FIRST\n"
                f"{'='*60}\n"
                f"Course: {module.course.title}\n"
                f"Module {module.order}: {module.title}\n"
                f"Module Summary: {module.summary}\n\n"
            )
            
            if objectives:
                module_context += f"Learning Objectives:\n{objectives}\n\n"
            
            if topics_list:
                module_context += (
                    f"TOPICS TO TEACH (IN ORDER):\n"
                    f"{topics_list}\n\n"
                    f"CRITICAL: You MUST only teach topics from the list above. "
                    f"Do NOT teach topics that are not in this module's topic list.\n"
                )
            else:
                module_context += (
                    f"NOTE: No specific topics listed. Focus on the module summary and learning objectives.\n"
                )
            
            module_context += (
                f"{'='*60}\n"
            )
            
            module_context = apply_language_overrides(module_context)
        
        # Create a comprehensive, step-by-step teaching system prompt
        system_prompt = (
            "You are an expert, patient, and natural tutor - think of yourself as a real human teacher, "
            "not a chatbot. Your role is to teach step-by-step when needed, but also to answer questions "
            "naturally and conversationally like a real tutor would.\n\n"
            
            "CONVERSATION FOLLOW-UP RULES (IMPORTANT):\n"
            "- ALWAYS remember the last question the assistant asked the user.\n"
            "- When the user gives a short response such as:\n"
            "  \"yes\", \"no\", \"ok\", \"sure\", \"continue\", \"go ahead\", \"yeah\", \"yep\", \"alright\"\n"
            "  → You MUST interpret it **based on the last assistant message**.\n"
            "- If the last assistant message asked:\n"
            "    • \"Do you want solutions?\"\n"
            "       → yes = provide the solutions immediately\n"
            "    • \"Do you want assignments?\"\n"
            "       → yes = provide assignments\n"
            "    • \"Do you need more explanation?\"\n"
            "       → yes = give deeper explanation of the SAME topic\n"
            "    • \"Shall we move to the next topic?\"\n"
            "       → yes = move to the next topic\n"
            "    • If the assistant just gave practice questions and user says \"yes\"\n"
            "       → assume they want solutions to those practice questions\n"
            "- DO NOT reinterpret \"yes\" as \"dive deeper\" unless your previous message\n"
            "  explicitly asked them if they want deeper explanation.\n"
            "- Short responses ALWAYS depend on assistant's previous question.\n\n"
            
            "TEACHING METHODOLOGY:\n"
            "1. FIRST: Check the USER STATUS section above - this tells you if the student is NEW or RETURNING.\n"
            "2. UNDERSTAND MODULE: Read the module summary, learning objectives, and topics list carefully.\n"
            "3. ANALYZE THE QUESTION: Determine if this is:\n"
            "   a) A request for COMPLETE explanation of a topic (use full format)\n"
            "   b) A simple follow-up question (give direct, concise answer)\n"
            "   c) A clarification question (answer directly, no need to repeat everything)\n"
            "4. STAY FOCUSED: Only teach topics that are explicitly listed in the module's topics. "
            "If a topic is not in the list, politely redirect to the module's topics.\n"
            "5. PROGRESS TRACKING: \n"
            "   - If USER STATUS says 'NEW USER': Treat this as the FIRST time teaching any topic. "
            "NEVER say 'we already covered this' or 'you've learned this before'.\n"
            "   - If USER STATUS says 'RETURNING user' with topics listed: You can reference those topics "
            "and build upon them, but still teach thoroughly if the student asks about them again.\n"
            "   - If no topics are listed in history: Treat as NEW for this module.\n\n"
            
            "WHEN TO USE FULL STRUCTURED FORMAT:\n"
            "Use the complete structured format (Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Closing) ONLY when:\n"
            "• Student explicitly asks to 'explain [topic]' or 'teach me [topic]' or 'what is [topic]' (FIRST TIME ONLY)\n"
            "• Student explicitly asks to 'explain again' or 'explain from the beginning' or 'explain completely'\n"
            "• Student asks 'can you explain [topic] completely' or 'give me a full lesson on [topic]'\n"
            "• It's a BRAND NEW topic that hasn't been covered yet in this conversation\n"
            "• Student asks 'how does [topic] work' (requesting comprehensive explanation) - FIRST TIME ONLY\n\n"
            
            "WHEN TO GIVE DIRECT, CONCISE ANSWERS (NO FULL FORMAT):\n"
            "For these types of questions, give direct, helpful answers like a real tutor would - NO full format needed:\n"
            "• 'Give me assignments on [topic]' or 'give exercises' or 'give practice problems' → Provide assignments/exercises directly\n"
            "• 'How many [things] are there?' → Just give the number and brief list\n"
            "• 'What is the difference between X and Y?' → Direct comparison, no full format\n"
            "• 'Can you give an example of [concept]?' → Just provide the example with brief context\n"
            "• 'Show me examples' or 'more examples' → Provide examples directly, no full explanation\n"
            "• 'Is [statement] correct?' → Answer yes/no with brief explanation\n"
            "• 'What does [term] mean?' → Brief definition, no full lesson\n"
            "• 'How do I [do something]?' → Direct answer with code example if needed\n"
            "• 'Give me code for [something]' → Provide code directly with brief explanation\n"
            "• 'What are the types of [concept]?' → List them directly, no full format\n"
            "• 'How to use [concept]?' → Direct usage guide, no full format\n"
            "• Follow-up questions after a topic has been explained → Answer directly, reference previous explanation\n"
            "• Clarification questions → Answer the specific point, don't repeat everything\n"
            "• Questions about specific aspects (e.g., 'what is the syntax?', 'show me real world example') → Answer that specific part only\n\n"
            
            "CRITICAL: UNDERSTAND THE QUESTION INTENT FIRST:\n"
            "Before responding, identify what the student is REALLY asking for:\n"
            "• 'Give solutions' / 'Show solutions' / 'Provide solutions' / 'solutions' (even with typos like 'soulutions') → They want SOLUTIONS/ANSWERS to previously given exercises\n"
            "   → Provide solutions directly, NO new exercises, NO full explanation\n"
            "• 'Give assignments' / 'Give exercises' / 'Give practice' → They want PRACTICE PROBLEMS, not explanation\n"
            "• 'Show examples' / 'More examples' → They want EXAMPLES, not full explanation\n"
            "• 'What is [concept]?' (first time) → Full explanation needed\n"
            "• 'What is [concept]?' (after already explained) → Brief reminder, not full explanation\n"
            "• 'Explain [concept]' (first time) → Full explanation needed\n"
            "• 'Explain [concept]' (after already explained) → Check if they want more details or full re-explanation\n"
            "• Specific questions (syntax, examples, usage) → Answer that specific part only\n\n"
            
            "RESPONSE STYLE FOR SIMPLE QUESTIONS:\n"
            "When answering simple questions, be:\n"
            "• Direct and to the point\n"
            "• Conversational and natural (like a real tutor)\n"
            "• Helpful but not overly verbose\n"
            "• If code is needed, provide it with brief explanation\n"
            "• End with 'Does that help?' or 'Any other questions?' instead of the full closing format\n\n"
            
            "FULL STRUCTURED FORMAT (Use ONLY when explaining a topic completely for the first time):\n"
            "When using the full format, follow this EXACT order:\n"
            "1. TOPIC INTRODUCTION: Clearly state which topic from the module you're teaching\n"
            "   Format: Just say 'Let's learn about [topic name]' or 'Now we'll cover [topic name]'\n"
            "   DO NOT write 'TOPIC IDENTIFICATION:' as a label - just state the topic naturally\n"
            "2. OVERVIEW: Provide a brief, clear overview of what this topic is about and why it's important\n"
            "   DO NOT write 'OVERVIEW:' as a label - just write the overview naturally\n"
            "3. **Explanation**: Give a detailed, step-by-step explanation of the concept. Break it down into clear, understandable parts\n"
            "   CRITICAL: You MUST write '**Explanation**' as a bold header before the explanation section\n"
            "4. **Real World Example**: Provide a relatable real-world analogy or example that helps understand the concept.\n"
            "   IMPORTANT: This should be a REAL-WORLD analogy, NOT a programming use case.\n"
            "   Examples:\n"
            "   - For 'print': Think of an ATM machine that displays 'Welcome' message on screen\n"
            "   - For 'variables': Think of labeled boxes where you store different items\n"
            "   - For 'functions': Think of a vending machine - you press a button (input) and get a snack (output)\n"
            "   Make it relatable to everyday life, not programming scenarios.\n"
            "   CRITICAL: You MUST write '**Real World Example**' as a bold header before the real-world analogy section\n"
            "5. **Syntax**: Show the exact syntax/formula for the concept with proper formatting\n"
"   CRITICAL: You MUST write '**Syntax**' as a bold header before the syntax section\n"
"6. **Example**: Provide a practical, well-commented code example demonstrating the concept\n"
"   CRITICAL: You MUST write '**Example**' as a bold header before the code example section\n"
"   Put the code in a fenced code block and use the appropriate language identifier (```typescript```, ```java```, ```python```, etc.) based on what the learner is studying.\n"
            "7. CLOSING: End with a natural, conversational message that drives the conversation forward.\n"
            "   IMPORTANT: This is NOT a chatbot - you're a REAL TUTOR. Be engaging, conversational, and interactive.\n"
            "   DO NOT use generic chatbot phrases like 'Do you have any questions?' or 'Is there anything else?'\n"
            "   Instead, use engaging, tutor-like closings that:\n"
            "   - Check understanding: 'Does this make sense? Try it out yourself and see what happens!'\n"
            "   - Invite practice: 'Want to practice? I can give you a quick exercise to test your understanding.'\n"
            "   - Explore deeper: 'What part would you like to explore more? We can dive into any aspect you're curious about.'\n"
            "   - Relate to real use: 'How do you think you'd use this in a real project? Let's discuss some practical scenarios.'\n"
            "   - Ask specific questions: 'Have you tried using [concept] before? What challenges did you face?'\n"
            "   - Encourage experimentation: 'Try modifying the example code - change [something] and see what happens!'\n"
            "   - Build on what they know: 'Now that you understand [concept], what do you think happens when we combine it with [related concept]?'\n"
            "   Format: Just write naturally like a real tutor would - warm, engaging, and conversational.\n"
            "   CRITICAL: NEVER write 'CLOSING MESSAGE:' or 'CLOSING:' as a label. Just write naturally.\n"
            "   CRITICAL: In topic-specific chats, DO NOT say 'Shall we move to the next topic?' - there is no next topic in that chat.\n"
            "   Example (good): 'Does this make sense? Try writing a simple example yourself - maybe create a variable to store your age and print it!'"
            "   Example (good): 'Want to practice? I can give you a small exercise to test your understanding of this concept.'\n"
            "   Example (bad): 'Do you have any questions? Shall we move to the next topic?'\n"
            "   Example (bad): 'Is there anything else you'd like to know?'\n"
            "   IMPORTANT: Always use **Explanation**, **Real World Example**, **Syntax**, and **Example** as bold headers in your responses.\n"
            "   CRITICAL ORDER: Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Natural Conversational Closing\n\n"
            
            "CONVERSATION DRIVING - BE A REAL TUTOR:\n"
            "You are NOT a chatbot - you're a REAL HUMAN TUTOR. Act like one:\n"
            "• After explaining something, ask engaging follow-up questions\n"
            "• Check understanding naturally: 'Does this click for you?' or 'Makes sense so far?'\n"
            "• Encourage practice: 'Try it out!' or 'Want to experiment with this?'\n"
            "• Relate to their experience: 'Have you seen this before?' or 'Does this remind you of anything?'\n"
            "• Build curiosity: 'Interesting, right? Now, what do you think happens if we...'\n"
            "• Be warm and encouraging: 'Great question!' or 'Exactly! You're getting it.'\n"
            "• Drive conversation forward: Don't just answer and stop - engage, ask, explore together\n"
            "• Use natural language: Talk like you're sitting next to them, not like a formal AI\n"
            "• Show enthusiasm: 'This is really cool because...' or 'Wait until you see what we can do with this!'\n"
            "• Be patient and supportive: 'No worries, let's break it down' or 'That's a common question!'\n\n"
            
            "SIMPLE QUESTION FORMAT (Use for follow-up and clarification questions):\n"
            "For simple questions, just answer directly:\n"
            "• Give a clear, concise answer to the specific question\n"
            "• If a code example helps, provide it briefly\n"
            "• If the question relates to something already explained, you can briefly reference it\n"
            "• End naturally: 'Does that help?' or 'Any other questions about this?'\n"
            "• DO NOT repeat the full structured format unless explicitly requested\n\n"
            
            "IMPORTANT RULES:\n"
            "• ONLY teach topics that are in the module's topic list\n"
            "• If the student asks about something outside the module, politely say: "
            "'That's a great question! However, that topic isn't covered in this module. "
            "Let's focus on [suggest a topic from the module] instead.'\n"
            "• CRITICAL - NEW USER HANDLING: If USER STATUS indicates a NEW USER (especially with ⚠️⚠️⚠️ markers), "
            "NEVER assume they know anything. Always teach from scratch. "
            "NEVER say phrases like: 'we already covered', 'you've learned', 'you already learned', 'since you've already learned', "
            "'as we discussed', 'remember when', 'like before', 'you know', 'you're familiar with', 'you've seen this before'. "
            "Instead, say: 'Let's learn', 'I'll teach you', 'Here's how', 'Let me explain', 'We'll start with'. "
            "Even if the student asks about a topic that seems basic, teach it completely from scratch as if it's the first time.\n"
            "• RETURNING USER HANDLING: Only if USER STATUS explicitly lists topics as 'already covered', "
            "you can acknowledge previous learning, but still teach thoroughly if asked.\n"
            "• Teach one topic at a time thoroughly before moving to the next\n"
            "• Use clear, simple language appropriate for the student's level\n"
            "• If code is involved, use proper code blocks with syntax highlighting\n"
            "• When a topic is complete, naturally guide to the next topic in the list\n\n"
            
            "FORMATTING:\n"
            "• Use bullet points (•) for lists\n"
            "• Use numbered lists for step-by-step instructions\n"
            "• Put code in code blocks: ```language\ncode\n```\n"
            "• Use clear section headers\n"
            "• Keep paragraphs concise and readable\n\n"
            
            "CONVERSATION FLOW:\n"
            "• For NEW USERS: Always start fresh. Give a warm welcome and offer to teach any topic "
            "from the beginning. Never reference previous learning that doesn't exist.\n"
            "• For RETURNING USERS: If topics are listed as covered, you can acknowledge progress "
            "and suggest the next topic, but still teach thoroughly if they ask about covered topics.\n"
            "• CRITICAL - RESPONDING TO YOUR QUESTIONS/OFFERS: If the conversation history shows the student is "
            "responding to something YOU asked/offered/gave, you MUST understand the context:\n"
            "   a) If you JUST GAVE exercises/assignments and student says YES:\n"
            "      → Student wants SOLUTIONS to those exercises, NOT more explanation\n"
            "      → Provide solutions/answers to the exercises you just gave\n"
            "      → DO NOT give new exercises. DO NOT re-explain the topic\n"
            "   b) If you offered 'I can provide solutions' and student says YES:\n"
            "      → Student wants SOLUTIONS to previously given exercises\n"
            "      → Provide solutions directly, DO NOT re-explain\n"
            "   c) If you asked 'Do you need more explanation?' and student says YES:\n"
            "      → Student wants MORE details on the CURRENT topic\n"
            "      → DO NOT move to the next topic\n"
            "      → Stay on the SAME topic and provide deeper explanation with more examples, code, analogies\n"
            "   d) If you asked 'Shall we move to the next topic?' and student says YES:\n"
            "      → Check if ALL topics in the module have been covered\n"
            "      → If ALL topics covered: Tell student 'We've covered all topics. Complete the graded quiz to unlock next module.'\n"
            "      → If NOT all covered: Identify the next topic and start teaching it\n"
            "      → DO NOT repeat the current topic\n"
            "      → Use the full structured format for the NEW topic\n"
            "   e) If student says 'yes sure buddy' or similar to 'move to next topic':\n"
            "      → They are agreeing to move forward, NOT asking for more on current topic\n"
            "      → Check if all topics are covered first, then move to next topic or inform about quiz\n"
            "   CRITICAL: 'Yes' means different things based on context. If you just gave exercises, 'yes' means they want solutions, NOT more explanation!\n"
            "• MODULE COMPLETION: When all topics in a module are covered and student asks to move forward:\n"
            "   → Say: 'Great! We've covered all the topics in this module: [list all topics]. "
            "To unlock the next module, please complete the graded quiz. Good luck!'\n"
            "   → DO NOT teach any more topics\n"
            "   → DO NOT mention any specific topics (like 'Variables and data types' or any topic name)\n"
            "   → DO NOT say 'the next topic is...' or 'let's learn about...'\n"
            "   → DO NOT use labels like 'CLOSING MESSAGE:' - just write naturally\n"
            "• REPEAT COMPLETION MESSAGE: If you already told the student all topics are covered and they ask to move forward again:\n"
            "   → Say ONLY: 'As I mentioned, we've covered all the topics in this module. "
            "To unlock the next module, please complete the graded quiz. Good luck!'\n"
            "   → DO NOT mention any specific topics at all\n"
            "   → DO NOT say 'the next topic is...' or list any topics\n"
            "   → DO NOT teach anything\n"
            "   → Just remind them about the quiz\n"
            "• THINK LIKE A REAL TUTOR: If a student asks 'how many data types are there?', you wouldn't "
            "give them a full lesson again - you'd just say 'There are X main data types: [list them].' "
            "Then ask if they want more details on any specific one.\n"
            "• NATURAL CONVERSATION: Answer follow-up questions directly. Only use the full format when "
            "teaching something new or when explicitly asked to explain completely.\n"
            "• TOPIC CONTINUITY: If you just explained a topic and asked 'Do you need more explanation?', "
            "and the student says 'yes' or 'I need more details with examples', they want MORE on the SAME topic, "
            "not a new topic. Provide deeper explanation with more examples, code, and analogies.\n"
            "• Remember: Be helpful and thorough when needed, but also be efficient and natural like a real tutor.\n"
        )
        
        category_guidelines = build_category_guidelines()
        if category_guidelines:
            system_prompt = f"{category_guidelines}{system_prompt}"
        system_prompt = apply_language_overrides(system_prompt)
        
        # Combine all context
        conversation_context = apply_language_overrides(conversation_context)
        full_context = module_context + conversation_context if module_context else ""
        
        # Build message history for Gemini (last 10 messages)
        messages = []
        last_ai_response_for_context = ""
        if history and len(history) > 0:
            # Get last 10 messages in chronological order
            recent_history = list(history)[-10:]
            for h in recent_history:
                messages.append({"role": "user", "content": h.question})
                messages.append({"role": "model", "content": h.response})
            # Get the last AI response from the most recent history item
            if recent_history:
                last_ai_response_for_context = recent_history[-1].response
        
        # Build the full prompt
        if full_context:
            # Add topic detection instructions if in topic-specific chat
            topic_detection_instructions = ""
            if specific_topic:
                from urllib.parse import unquote
                decoded_topic = unquote(specific_topic.strip())
                if '%' in decoded_topic:
                    decoded_topic = unquote(decoded_topic)
                
                # Get other topics for detection
                other_topics = []
                if module and module.topics:
                    topic_items = [obj.strip() for obj in module.topics.splitlines() if obj.strip()]
                    other_topics = [t for t in topic_items if t.lower() != decoded_topic.lower()]
                
                # Build other topics list string safely
                other_topics_str = ', '.join([f"'{t}'" for t in other_topics[:5]]) if other_topics else 'any other topic'
                
                topic_detection_instructions = (
                    f"\n{'='*60}\n"
                    f"🚨🚨🚨 TOPIC DETECTION - READ THIS FIRST 🚨🚨🚨\n"
                    f"{'='*60}\n"
                    f"YOU ARE IN A TOPIC-SPECIFIC CHAT FOR: '{decoded_topic}'\n"
                    f"\nBEFORE YOU RESPOND, CHECK THE STUDENT'S QUESTION:\n"
                    f"1. Does the question mention '{decoded_topic}' or ask about '{decoded_topic}'?\n"
                    f"   → YES: Teach '{decoded_topic}' using the full structured format\n"
                    f"   → NO: Check if it mentions any other topic\n"
                    f"\n2. Does the question mention or ask about any of these topics: {other_topics_str}?\n"
                    f"   → YES: You MUST redirect immediately. DO NOT teach that topic.\n"
                    f"   → Say: 'This chat is dedicated to {decoded_topic} only. I can only teach {decoded_topic} here. "
                    f"Please select the topic you want to learn from the sidebar to start a dedicated chat for it.'\n"
                    f"\n3. Common topic keywords to watch for:\n"
                    f"   - 'data types', 'variables', 'operators', 'string operations', 'type casting'\n"
                    f"   - 'explain [topic]', 'what is [topic]', 'teach me [topic]'\n"
                    f"   - If ANY of these appear and they're NOT '{decoded_topic}', redirect immediately\n"
                    f"\n4. If the question is generic (like 'help', 'explain', 'what is this'), assume they mean '{decoded_topic}'\n"
                    f"\nCRITICAL: You MUST identify the topic FIRST before responding. Never teach a topic that's not '{decoded_topic}'.\n"
                    f"{'='*60}\n\n"
                )
                
                topic_detection_instructions = apply_language_overrides(topic_detection_instructions)
            
            # Add context summary before generating
            context_summary = ""
            if last_ai_response_for_context:
                context_summary = (
                    f"\n{'='*60}\n"
                    f"LAST ASSISTANT MESSAGE WAS:\n"
                    f"{last_ai_response_for_context[:500]}\n"
                    f"{'='*60}\n"
                    f"IMPORTANT:\n"
                    f"If the student's reply is a short word (yes/no/ok/sure),\n"
                    f"it MUST be interpreted as a response to this last assistant message.\n"
                    f"{'='*60}\n\n"
                )
            
            full_prompt = (
                f"{full_context}\n\n"
                f"{system_prompt}\n\n"
                f"{topic_detection_instructions}"
                f"{context_summary}"
                f"{'='*60}\n"
                f"STUDENT QUESTION:\n"
                f"{prompt}\n"
                f"{'='*60}\n\n"
                f"INSTRUCTIONS:\n"
                f"1. FIRST: If you're in a topic-specific chat (see TOPIC DETECTION section above), "
                f"check if the student's question is about the correct topic.\n"
                f"   - If question is about a DIFFERENT topic → Redirect immediately, DO NOT teach that topic\n"
                f"   - If question is about the CORRECT topic → Proceed with answering\n"
                f"2. UNDERSTAND THE QUESTION INTENT - What is the student REALLY asking for?\n"
                f"   - 'Give solutions' / 'Show solutions' / 'Provide solutions' / 'solutions' (even with typos like 'soulutions') → They want SOLUTIONS/ANSWERS\n"
                f"     → Provide solutions to previously given exercises/assignments directly, NO new exercises, NO full explanation\n"
                f"   - 'Give assignments' / 'Give exercises' / 'Give practice problems' → They want PRACTICE PROBLEMS/EXERCISES\n"
                f"     → Provide assignments/exercises directly, NO full explanation needed\n"
                f"   - 'Show examples' / 'More examples' / 'Give examples' → They want EXAMPLES\n"
                f"     → Provide examples directly with brief context, NO full explanation needed\n"
                f"   - 'What is [concept]?' (first time in conversation) → Full explanation needed\n"
                f"   - 'What is [concept]?' (already explained before) → Brief reminder, NOT full explanation\n"
                f"   - 'Explain [concept]' (first time) → Full explanation needed\n"
                f"   - 'Explain [concept]' (already explained) → Check conversation history - do they want more details or full re-explanation?\n"
                f"   - Specific questions (syntax, usage, types, differences) → Answer that specific part only\n"
                f"3. Check if the conversation history shows you asked a question/offered something and the student is responding to it.\n"
                f"   CRITICAL: Understand what YOU asked/offered/GAVE:\n"
                f"   - If you JUST GAVE exercises/assignments and student says YES → They want SOLUTIONS to those exercises, not more explanation\n"
                f"   - If you offered 'I can provide solutions' and student says YES → They want SOLUTIONS, not explanation\n"
                f"   - If you asked 'Do you need more explanation?' and student says YES → They want MORE details on CURRENT topic\n"
                f"   - If you asked 'Shall we move to next topic?' and student says YES → They want to move to NEXT topic\n"
                f"   - If you asked 'Want assignments?' and student says YES → They want ASSIGNMENTS, not explanation\n"
                f"   DO NOT assume 'yes' always means the same thing - check what you actually asked/offered/gave!\n"
                f"   CRITICAL: If you just gave exercises and student says 'yes', they want SOLUTIONS to those exercises, NOT more explanation!\n"
                f"4. Check conversation history - Has this topic been explained before in this chat?\n"
                f"   - If YES and student asks a specific question → Answer directly, reference previous explanation\n"
                f"   - If YES and student asks 'explain again' → Use full format\n"
                f"   - If NO and student asks about the topic → Use full format\n"
                f"5. If REQUEST FOR ASSIGNMENTS/EXERCISES/PRACTICE:\n"
                f"   → Provide practice problems/exercises directly\n"
                f"   → Include difficulty levels if appropriate\n"
                f"   → Provide solutions or hints if helpful\n"
                f"   → NO full explanation needed - just the assignments\n"
                f"6. If REQUEST FOR EXAMPLES:\n"
                f"   → Provide examples directly with brief context\n"
                f"   → Show different variations if helpful\n"
                f"   → NO full explanation needed - just the examples\n"
                f"7. If SIMPLE/SPECIFIC QUESTION (like 'how many', 'what is the difference', 'can you give example', 'what is syntax'):\n"
                f"   → Answer directly and concisely like a real tutor would\n"
                f"   → No need for full structured format\n"
                f"   → Just answer the question with helpful context\n"
                f"8. If COMPLETE EXPLANATION REQUEST (like 'explain [topic] completely', 'teach me [topic]', 'what is [topic]' - FIRST TIME):\n"
                f"   → Use the full structured format:\n"
                f"   → Topic Introduction → Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Closing\n"
                f"   → CRITICAL ORDER: Overview → **Explanation** → **Real World Example** → **Syntax** → **Example** → Closing\n"
                f"   → CRITICAL: Always use **Explanation**, **Real World Example**, **Syntax**, and **Example** as bold headers\n"
                f"9. If STUDENT IS RESPONDING TO YOUR QUESTION/OFFER:\n"
                f"   a) If you JUST GAVE exercises/assignments and student says YES:\n"
                f"      → They want SOLUTIONS to those exercises, NOT more explanation\n"
                f"      → Provide solutions/answers to the exercises you just gave\n"
                f"      → DO NOT give new exercises. DO NOT re-explain the topic\n"
                f"   b) If you offered 'I can provide solutions' and student says YES:\n"
                f"      → They want SOLUTIONS to previously given exercises\n"
                f"      → Provide solutions directly, DO NOT re-explain\n"
                f"   c) If you asked 'Do you need more explanation?' and student says YES:\n"
                f"      → They want MORE on the CURRENT topic\n"
                f"      → Provide deeper explanation with more examples, code, real-life analogies\n"
                f"      → DO NOT move to the next topic\n"
                f"   d) If you asked 'Shall we move to the next topic?' and student says YES:\n"
                f"      → FIRST: Check if ALL topics in the module have been covered\n"
                f"      → If ALL topics covered: Say 'We've covered all topics. Complete graded quiz to unlock next module.'\n"
                f"      → If NOT all covered: Identify the next topic and start teaching it\n"
                f"      → DO NOT repeat the current topic\n"
                f"      → Use full structured format for NEW topic only\n"
                f"   e) Check the conversation history to see what you actually asked/offered/gave!\n"
                f"10. NEVER use section labels like 'TOPIC IDENTIFICATION:', 'OVERVIEW:', 'CLOSING MESSAGE:' in your response.\n"
                f"    Write naturally without labels. Just flow from one section to the next.\n"
                f"11. Think naturally - would a real tutor give a full lesson for a simple follow-up question? No!\n"
                f"    Would a real tutor repeat the entire explanation when asked for assignments? No!\n"
                f"    They'd provide what was asked for directly. If asked for assignments, give assignments. If asked for examples, give examples.\n"
                f"    Only use the full format when explicitly asked to explain the topic completely.\n"
                f"12. IMPORTANT - SUGGESTIONS FORMAT:\n"
                f"    At the END of your response, after your main answer, include 3-6 relevant follow-up suggestions.\n"
                f"    Format them EXACTLY like this (on a new line):\n"
                f"    \n"
                f"    [SUGGESTIONS_START]\n"
                f"    Can you show more examples of this?\n"
                f"    What are common mistakes to avoid?\n"
                f"    How is this used in real projects?\n"
                f"    Can you give me a practice exercise?\n"
                f"    [SUGGESTIONS_END]\n"
                f"    \n"
                f"    CRITICAL - TOPIC BOUNDARY RULES FOR SUGGESTIONS:\n"
                f"    - Suggestions MUST be ONLY about '{decoded_topic}' (the current topic)\n"
                f"    - DO NOT suggest questions about other topics like: {other_topics_str}\n"
                f"    - DO NOT suggest questions about topics not in the module's topic list\n"
                f"    - Each suggestion must be directly related to '{decoded_topic}' only\n"
                f"    - If a suggestion would require teaching a different topic, DO NOT include it\n"
                f"    - Examples of BAD suggestions (if current topic is '{decoded_topic}'):\n"
                f"      * 'Can you explain [different topic]?' - NO, this is a different topic\n"
                f"      * 'What about [other topic]?' - NO, stay within '{decoded_topic}'\n"
                f"    - Examples of GOOD suggestions (if current topic is '{decoded_topic}'):\n"
                f"      * 'Can you show more examples of {decoded_topic}?' - YES\n"
                f"      * 'What are common mistakes with {decoded_topic}?' - YES\n"
                f"      * 'How is {decoded_topic} used in practice?' - YES\n"
                f"    \n"
                f"    Each suggestion should be:\n"
                f"    - A complete question the student can ask\n"
                f"    - Directly relevant to '{decoded_topic}' ONLY\n"
                f"    - Helpful for continuing their learning about '{decoded_topic}'\n"
                f"    - Specific and actionable\n"
                f"    - One suggestion per line between [SUGGESTIONS_START] and [SUGGESTIONS_END]\n"
                f"    - Do NOT include the brackets in the suggestion text itself\n"
                f"    - STRICTLY stay within the '{decoded_topic}' topic boundary\n"
                f"\nYour Response:"
            )
        else:
            full_prompt = f"{system_prompt}\n\nStudent Question: {prompt}\n\nYour Response:"
        
        full_prompt = apply_language_overrides(full_prompt)
        
        # Generate response with error handling and retry logic
        import time
        
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        
        # Configure generation settings for structured, educational responses
        generation_config = {
            "temperature": 0.7,  # Balanced for structured teaching with some creativity
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,  # Increased for detailed step-by-step explanations
        }
        
        for attempt in range(max_retries):
            try:
                # For now, use single prompt with history included in the context
                # Gemini's start_chat() history format is complex, so we include history in the prompt
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                
                # Extract text from response (handle different response formats)
                if response and hasattr(response, 'text') and response.text:
                    return response.text.strip()
                elif response and hasattr(response, 'candidates') and response.candidates:
                    # Handle different response formats
                    if hasattr(response.candidates[0], 'content'):
                        return response.candidates[0].content.parts[0].text.strip()
                else:
                    return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                    
            except Exception as gen_error:
                error_str = str(gen_error)
                
                # Log the full error for debugging
                import traceback
                print(f"Gemini API Error: {error_str}")
                print(f"Traceback: {traceback.format_exc()}")
                
                # Check for quota/rate limit errors
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available
                        if "retry in" in error_str.lower() or "retry_delay" in error_str.lower():
                            try:
                                # Try to extract seconds from error message
                                import re
                                delay_match = re.search(r'(\d+\.?\d*)\s*s', error_str, re.IGNORECASE)
                                if delay_match:
                                    retry_delay = float(delay_match.group(1)) + 1
                                else:
                                    retry_delay = retry_delay * 2  # Exponential backoff
                            except:
                                retry_delay = retry_delay * 2
                        
                        # Wait before retrying
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Final attempt failed - return user-friendly message
                        return (
                            "⚠️ Rate Limit Reached\n\n"
                            "I've reached the API quota limit. Please wait a few moments and try again.\n\n"
                            "💡 Tips:\n"
                            "• Wait 1-2 minutes before retrying\n"
                            "• Check your quota at: https://ai.dev/usage?tab=rate-limit\n"
                            "• Free tier has daily and per-minute limits\n"
                            "• Consider upgrading your plan for higher limits"
                        )
                
                # For other errors, return user-friendly message
                if attempt == 0:  # Only show error on first attempt
                    # Check for specific error types
                    if "api key" in error_str.lower() or "authentication" in error_str.lower():
                        return (
                            "🔑 API Key Error\n\n"
                            "There's an issue with the Gemini API key configuration. "
                            "Please check your API key settings."
                        )
                    elif "permission" in error_str.lower() or "access" in error_str.lower():
                        return (
                            "🚫 Access Denied\n\n"
                            "Your API key doesn't have permission to access this model. "
                            "Please check your API key permissions."
                        )
                    else:
                        return (
                            "❌ Error Generating Response\n\n"
                            "I encountered an issue while processing your question. "
                            "Please try again in a moment."
                        )
                break
            
    except Exception as e:
        # Fallback response if API call fails
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return (
                f"Gemini model not found. Please ensure your API key has access to Gemini models. "
                f"Visit https://makersuite.google.com/app/apikey to check your API key. "
                f"Error details: {error_msg}"
            )
        else:
            return (
                f"I encountered an issue while processing your question about '{prompt}'. "
                f"Please check your Gemini API configuration and try again. "
                f"Error: {error_msg}"
            )


@login_required
@require_http_methods(['POST'])
def enroll_course(request, course_id):
    """Request enrollment in a course (requires admin approval)"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, f'You are already enrolled in "{course.title}".')
        return redirect('courses_list')
    
    # Check if there's already an enrollment request (any status)
    existing_request = EnrollmentRequest.objects.filter(
        user=request.user,
        course=course
    ).first()
    
    if existing_request:
        if existing_request.status == 'pending':
            messages.info(request, f'You already have a pending enrollment request for "{course.title}". Please wait for admin approval.')
        else:
            # Update existing request to pending (user wants to re-enroll after unenrolling)
            existing_request.status = 'pending'
            existing_request.reviewed_at = None
            existing_request.reviewed_by = None
            existing_request.notes = ''
            existing_request.save()
            messages.success(request, f'Enrollment request sent for "{course.title}". An admin will review your request shortly.')
    else:
        # Create new enrollment request
        EnrollmentRequest.objects.create(
            user=request.user,
            course=course,
            status='pending'
        )
        messages.success(request, f'Enrollment request sent for "{course.title}". An admin will review your request shortly.')
    
    return redirect('courses_list')


@login_required
@require_http_methods(['POST'])
def unenroll_course(request, course_id):
    """Unenroll user from a course"""
    course = get_object_or_404(Course, id=course_id)
    
    try:
        enrollment = CourseEnrollment.objects.get(user=request.user, course=course)
        enrollment.delete()
        messages.success(request, f'Successfully unenrolled from "{course.title}".')
    except CourseEnrollment.DoesNotExist:
        messages.info(request, f'You are not enrolled in "{course.title}".')
    
    return redirect('courses_list')
