from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from booking.models import Venue, TimeSlot, Booking, Category, VenueManager
from booking.forms import VenueForm, TimeSlotForm
from booking.decorators import venue_manager_required


@login_required
@venue_manager_required
def manager_dashboard(request):
    """
    Dashboard view for venue managers.
    """

    manager = request.user.venue_manager
    venues = Venue.objects.filter(manager=manager)

    # Get recent bookings for all managed venues
    recent_bookings = Booking.objects.filter(
        venue__in=venues
    ).order_by('-booking_date')[:10]

    # Get pending bookings count
    pending_bookings_count = Booking.objects.filter(
        venue__in=venues,
        status='pending'
    ).count()

    # Get total venues count
    venues_count = venues.count()

    # Get total confirmed bookings
    confirmed_bookings_count = Booking.objects.filter(
        venue__in=venues,
        status='confirmed'
    ).count()

    context = {
        'manager': manager,
        'venues': venues,
        'recent_bookings': recent_bookings,
        'pending_bookings_count': pending_bookings_count,
        'venues_count': venues_count,
        'confirmed_bookings_count': confirmed_bookings_count,
    }
    return render(request, 'manager/dashboard.html', context)


@login_required
@venue_manager_required
def manager_venues(request):
    """
    View for managing venues.
    """

    manager = request.user.venue_manager
    venues = Venue.objects.filter(manager=manager)

    context = {
        'venues': venues,
    }
    return render(request, 'manager/venues.html', context)


@login_required
@venue_manager_required
def manager_add_venue(request):
    """
    View for adding a new venue.
    """

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.manager = request.user.venue_manager
            venue.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Venue added successfully!')
            return redirect('manager_venues')
    else:
        form = VenueForm()

    # Get all venues for the sidebar
    venues = Venue.objects.filter(manager=request.user.venue_manager)

    context = {
        'form': form,
        'categories': Category.objects.all(),
        'venues': venues,
    }
    return render(request, 'manager/add_venue.html', context)


@login_required
@venue_manager_required
def manager_edit_venue(request, venue_id):
    """
    View for editing a venue.
    """

    manager = request.user.venue_manager
    venue = get_object_or_404(Venue, id=venue_id, manager=manager)

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue updated successfully!')
            return redirect('manager_venues')
    else:
        form = VenueForm(instance=venue)

    context = {
        'form': form,
        'venue': venue,
        'categories': Category.objects.all(),
    }
    return render(request, 'manager/edit_venue.html', context)


@login_required
@venue_manager_required
def manager_bookings(request):
    """
    View for managing bookings.
    """

    manager = request.user.venue_manager
    venues = Venue.objects.filter(manager=manager)

    # Get bookings for all managed venues
    bookings = Booking.objects.filter(venue__in=venues).order_by('-booking_date')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)

    # Filter by venue if provided
    venue_id = request.GET.get('venue')
    if venue_id:
        bookings = bookings.filter(venue_id=venue_id)

    context = {
        'bookings': bookings,
        'venues': venues,
        'status': status,
        'venue_id': venue_id,
    }
    return render(request, 'manager/bookings.html', context)


@login_required
@venue_manager_required
def manager_time_slots(request, venue_id):
    """
    View for managing time slots for a venue.
    """

    manager = request.user.venue_manager
    venue = get_object_or_404(Venue, id=venue_id, manager=manager)

    # Get time slots for the venue
    time_slots_list = TimeSlot.objects.filter(venue=venue).order_by('date', 'start_time')

    # Pagination
    page = request.GET.get('page', 1)
    items_per_page = 10  # Number of time slots per page
    paginator = Paginator(time_slots_list, items_per_page)
    time_slots = paginator.get_page(page)

    # Get all venues for the sidebar
    venues = Venue.objects.filter(manager=manager)

    context = {
        'venue': venue,
        'time_slots': time_slots,
        'venues': venues,
    }
    return render(request, 'manager/time_slots.html', context)


@login_required
@venue_manager_required
def manager_add_time_slot(request, venue_id):
    """
    View for adding a new time slot for a venue.
    """

    manager = request.user.venue_manager
    venue = get_object_or_404(Venue, id=venue_id, manager=manager)

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save(commit=False)
            time_slot.venue = venue
            time_slot.save()
            messages.success(request, 'Time slot added successfully!')
            return redirect('manager_time_slots', venue_id=venue.id)
    else:
        form = TimeSlotForm()

    # Get all venues for the sidebar
    venues = Venue.objects.filter(manager=manager)

    context = {
        'form': form,
        'venue': venue,
        'venues': venues,
    }
    return render(request, 'manager/add_time_slot.html', context)


@login_required
@venue_manager_required
def manager_booking_detail(request, booking_id):
    """
    View for displaying booking details for managers.
    """
    manager = request.user.venue_manager
    venues = Venue.objects.filter(manager=manager)

    # Get the booking and verify it belongs to one of the manager's venues
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the booking belongs to one of the manager's venues
    if booking.venue.manager != manager:
        return HttpResponseForbidden("You don't have permission to view this booking.")

    context = {
        'booking': booking,
        'venues': venues,
    }
    return render(request, 'manager/booking_detail.html', context)


@login_required
@venue_manager_required
def manager_confirm_booking(request, booking_id):
    """
    View for confirming a pending booking.
    """
    manager = request.user.venue_manager

    # Get the booking and verify it belongs to one of the manager's venues
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the booking belongs to one of the manager's venues
    if booking.venue.manager != manager:
        return HttpResponseForbidden("You don't have permission to confirm this booking.")

    # Check if the booking is pending
    if booking.status != 'pending':
        messages.error(request, 'Only pending bookings can be confirmed.')
        return redirect('manager_bookings')

    # Confirm the booking
    booking.status = 'confirmed'
    booking.save()

    # Make sure the time slot is marked as unavailable
    booking.time_slot.is_available = False
    booking.time_slot.save()

    messages.success(request, f'Booking #{booking.id} has been confirmed successfully.')
    return redirect('manager_bookings')


@login_required
@venue_manager_required
def manager_cancel_booking(request, booking_id):
    """
    View for cancelling a booking by a manager.
    """
    manager = request.user.venue_manager

    # Get the booking and verify it belongs to one of the manager's venues
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the booking belongs to one of the manager's venues
    if booking.venue.manager != manager:
        return HttpResponseForbidden("You don't have permission to cancel this booking.")

    # Check if the booking is already cancelled
    if booking.status == 'cancelled':
        messages.error(request, 'This booking is already cancelled.')
        return redirect('manager_bookings')

    # If the booking was confirmed, make the time slot available again
    if booking.status == 'confirmed':
        booking.time_slot.is_available = True
        booking.time_slot.save()

    # Cancel the booking
    booking.status = 'cancelled'
    booking.save()

    messages.success(request, f'Booking #{booking.id} has been cancelled successfully.')
    return redirect('manager_bookings')


@login_required
@venue_manager_required
def manager_delete_venue(request, venue_id):
    """
    View for deleting a venue.
    """
    manager = request.user.venue_manager
    venue = get_object_or_404(Venue, id=venue_id, manager=manager)

    # Check if there are any active bookings for this venue
    active_bookings = Booking.objects.filter(
        venue=venue,
        status__in=['pending', 'confirmed']
    ).exists()

    if active_bookings:
        messages.error(request, 'Cannot delete venue with active bookings. Please cancel or complete all bookings first.')
        return redirect('manager_venues')

    # Store venue name for success message
    venue_name = venue.name

    # Delete the venue
    venue.delete()

    messages.success(request, f'Venue "{venue_name}" has been deleted successfully.')
    return redirect('manager_venues')
