class VenueManagerMiddleware:
    """
    Middleware to add venue_manager_access to the request.
    This makes it easy to check if a user has venue manager access in templates and views.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add venue_manager_access attribute to request
        if request.user.is_authenticated:
            request.venue_manager_access = (
                hasattr(request.user, 'venue_manager') and 
                request.user.venue_manager.is_approved
            )
        else:
            request.venue_manager_access = False
            
        response = self.get_response(request)
        return response
