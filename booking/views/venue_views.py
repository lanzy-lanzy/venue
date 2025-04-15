from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from booking.models import Venue, Category, TimeSlot


def venue_list(request):
    """
    View for listing venues with filtering options.
    """
    venues = Venue.objects.filter(status='active')
    categories = Category.objects.all()
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        venues = venues.filter(categories__id=category_id)
    
    # Filter by capacity if provided
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        venues = venues.filter(capacity__gte=min_capacity)
    
    # Filter by price range if provided
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        venues = venues.filter(hourly_rate__gte=min_price)
    if max_price:
        venues = venues.filter(hourly_rate__lte=max_price)
    
    # Search by name or address
    search_query = request.GET.get('search')
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'venues': venues,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'min_capacity': min_capacity,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    # If HTMX request, return only the venues list partial
    if request.headers.get('HX-Request'):
        return render(request, 'partials/venue_list.html', context)
    
    return render(request, 'booking/venue_list.html', context)


def venue_detail(request, venue_id):
    """
    View for displaying venue details and available time slots.
    """
    venue = get_object_or_404(Venue, id=venue_id, status='active')
    
    # Get available time slots for the next 7 days
    today = timezone.now().date()
    end_date = today + timedelta(days=7)
    available_slots = TimeSlot.objects.filter(
        venue=venue,
        date__gte=today,
        date__lte=end_date,
        is_available=True
    ).order_by('date', 'start_time')
    
    context = {
        'venue': venue,
        'available_slots': available_slots,
    }
    return render(request, 'booking/venue_detail.html', context)
