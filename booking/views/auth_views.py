from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    """
    Custom login view that redirects users to different dashboards based on their role.
    """
    template_name = 'auth/login.html'
    
    def get_success_url(self):
        """
        Determine the URL to redirect to after successful login.
        """
        user = self.request.user
        
        # Check if user is a venue manager
        if hasattr(user, 'venue_manager') and user.is_staff and user.venue_manager.is_approved:
            return reverse_lazy('manager_dashboard')
        
        # Regular user
        return reverse_lazy('user_dashboard')
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: if user is already authenticated, redirect to appropriate dashboard.
        """
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
