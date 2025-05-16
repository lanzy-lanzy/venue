from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Venue, Category, TimeSlot, Booking
from datetime import datetime, timedelta


def home(request):
    # Get featured venues (for example, the 4 most recently added)
    featured_venues = Venue.objects.all().order_by('-created_at')[:4]
    # Get all categories
    categories = Category.objects.all()

    context = {
        'featured_venues': featured_venues,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def venue_list(request):
    venues = Venue.objects.all()
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

    return render(request, 'venue_list.html', context)


def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

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
    return render(request, 'venue_detail.html', context)


@login_required
def book_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        time_slot_id = request.POST.get('time_slot')
        num_guests = request.POST.get('num_guests')
        special_requests = request.POST.get('special_requests', '')

        time_slot = get_object_or_404(TimeSlot, id=time_slot_id, venue=venue)

        if not time_slot.is_available:
            messages.error(request, 'Sorry, this time slot is no longer available.')
            return redirect('venue_detail', venue_id=venue.id)

        # Calculate hours and total price
        hours = (time_slot.end_time.hour - time_slot.start_time.hour)
        total_price = venue.hourly_rate * hours

        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            venue=venue,
            time_slot=time_slot,
            num_guests=num_guests,
            special_requests=special_requests,
            total_price=total_price,
            status='pending'
        )

        # Mark time slot as unavailable
        time_slot.is_available = False
        time_slot.save()

        messages.success(request, 'Booking created successfully! We will confirm your booking shortly.')
        return redirect('booking_detail', booking_id=booking.id)

    # Get available time slots
    available_slots = TimeSlot.objects.filter(venue=venue, is_available=True).order_by('date', 'start_time')

    context = {
        'venue': venue,
        'available_slots': available_slots,
    }
    return render(request, 'book_venue.html', context)


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    context = {
        'booking': booking,
    }
    return render(request, 'booking_detail.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    context = {
        'bookings': bookings,
    }
    return render(request, 'my_bookings.html', context)


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'confirmed':
        # Make the time slot available again
        booking.time_slot.is_available = True
        booking.time_slot.save()

    booking.status = 'cancelled'
    booking.save()

    messages.success(request, 'Booking cancelled successfully.')
    return redirect('my_bookings')


# HTMX endpoints
def get_available_slots(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    date_str = request.GET.get('date')

    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            available_slots = TimeSlot.objects.filter(
                venue=venue,
                date=selected_date,
                is_available=True
            ).order_by('start_time')
        except ValueError:
            available_slots = []
    else:
        available_slots = []

    context = {
        'available_slots': available_slots,
        'venue': venue,  # Add the venue to the context
    }
    return render(request, 'partials/available_slots.html', context)
