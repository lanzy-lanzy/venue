from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    """
    Decorator for views that checks that the user is an admin (superuser).
    This is different from Django's built-in admin and ensures only superusers
    can access the custom admin views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        
        if not request.user.is_superuser:
            return HttpResponseForbidden("You don't have permission to access this page. Admin privileges required.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
