from django.shortcuts import render
from booking.models import Venue, Category


def home(request):
    """
    View for the home page.
    Displays featured venues and categories.
    """
    # Get featured venues (for example, the 4 most recently added)
    featured_venues = Venue.objects.filter(status='active').order_by('-created_at')[:4]
    
    # Get all categories
    categories = Category.objects.all()
    
    context = {
        'featured_venues': featured_venues,
        'categories': categories,
    }
    return render(request, 'booking/home.html', context)
