from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from booking.models import Venue, TimeSlot, Booking


@login_required
def book_venue(request, venue_id):
    """
    View for booking a venue.
    """
    venue = get_object_or_404(Venue, id=venue_id, status='active')

    if request.method == 'POST':
        time_slot_id = request.POST.get('time_slot')
        num_guests = request.POST.get('num_guests')
        special_requests = request.POST.get('special_requests', '')

        time_slot = get_object_or_404(TimeSlot, id=time_slot_id, venue=venue)

        if not time_slot.is_available:
            messages.error(request, 'Sorry, this time slot is no longer available.')
            return redirect('venue_detail', venue_id=venue.id)

        # Calculate hours and total price
        hours = time_slot.duration_hours()
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
    return render(request, 'booking/book_venue.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    View for displaying booking details.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    context = {
        'booking': booking,
    }
    return render(request, 'booking/booking_detail.html', context)


@login_required
def my_bookings(request):
    """
    View for displaying all bookings for the current user.
    """
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    # Get the user's profile or create one if it doesn't exist
    from booking.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        from django.contrib import messages
        messages.info(request, 'We created a new profile for you. Please update your information.')

    context = {
        'bookings': bookings,
        'profile': profile,
    }
    return render(request, 'booking/my_bookings_fullpage.html', context)


@login_required
def cancel_booking(request, booking_id):
    """
    View for cancelling a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'confirmed':
        # Make the time slot available again
        booking.time_slot.is_available = True
        booking.time_slot.save()

    booking.status = 'cancelled'
    booking.save()

    messages.success(request, 'Booking cancelled successfully.')
    return redirect('my_bookings')
