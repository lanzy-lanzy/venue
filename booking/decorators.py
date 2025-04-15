from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from functools import wraps

def venue_manager_required(view_func):
    """
    Decorator for views that checks that the user is a venue manager.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        
        if not hasattr(request.user, 'venue_manager'):
            return HttpResponseForbidden("You don't have permission to access this page.")
            
        if not request.user.venue_manager.is_approved:
            return HttpResponseForbidden("Your venue manager account is not approved yet.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
