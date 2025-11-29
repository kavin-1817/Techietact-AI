from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to check if user is admin"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access admin panel.')
            return redirect('admin_login')
        
        # Check if user has admin profile or is staff
        if not (hasattr(request.user, 'admin_profile') or request.user.is_staff):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

