from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from booking.models import Venue, TimeSlot, Category
from booking.forms import VenueForm
from booking.decorators import venue_manager_required
from django.contrib.auth.decorators import login_required


def get_available_slots(request, venue_id):
    """
    HTMX endpoint for getting available time slots for a specific date.
    """
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
    }
    return render(request, 'partials/available_slots.html', context)


@login_required
@venue_manager_required
def venue_edit_modal(request, venue_id):
    """
    HTMX endpoint for editing a venue in a modal.
    """
    manager = request.user.venue_manager
    venue = get_object_or_404(Venue, id=venue_id, manager=manager)

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue updated successfully!')
            # Return a response with HX-Redirect header
            response = HttpResponse('Success')
            response['HX-Redirect'] = '/manager/venues/'
            return response
        else:
            # Return the form with validation errors
            context = {
                'form': form,
                'venue': venue,
                'categories': Category.objects.all(),
            }
            return render(request, 'partials/venue_edit_form_new.html', context)
    else:
        form = VenueForm(instance=venue)

    context = {
        'form': form,
        'venue': venue,
        'categories': Category.objects.all(),
    }
    return render(request, 'partials/venue_edit_form_new.html', context)


@login_required
@venue_manager_required
def venue_add_modal(request):
    """
    HTMX endpoint for adding a new venue in a modal.
    """
    manager = request.user.venue_manager

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.manager = manager
            venue.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Venue added successfully!')
            # Return a response with HX-Redirect header
            response = HttpResponse('Success')
            response['HX-Redirect'] = '/manager/venues/'
            return response
        else:
            # Return the form with validation errors
            context = {
                'form': form,
                'categories': Category.objects.all(),
            }
            return render(request, 'partials/venue_add_form_new.html', context)
    else:
        form = VenueForm()

    context = {
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'partials/venue_add_form_new.html', context)
