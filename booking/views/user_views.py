from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.utils import timezone
from booking.forms import UserProfileForm, RegistrationForm
from booking.models import Booking, Venue


@login_required
def edit_profile(request):
    """
    View for users to edit their profile information.
    """
    # Get the user's profile or create one if it doesn't exist
    from booking.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        messages.info(request, 'We created a new profile for you. Please update your information.')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('my_profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'booking/edit_profile.html', context)


@login_required
def my_profile(request):
    """
    View for displaying the user's profile.
    """
    # Get the user's profile or create one if it doesn't exist
    from booking.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        messages.info(request, 'We created a new profile for you. Please update your information.')

    # Get booking statistics
    booking_stats = profile.get_booking_statistics()

    context = {
        'profile': profile,
        'booking_stats': booking_stats,
    }
    return render(request, 'booking/my_profile.html', context)


@login_required
def user_dashboard(request):
    """
    Dashboard view for regular users.
    """
    # Get the user's profile or create one if it doesn't exist
    from booking.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        messages.info(request, 'We created a new profile for you. Please update your information.')

    # Get booking statistics
    booking_stats = profile.get_booking_statistics()

    # Get recent bookings
    recent_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')[:5]

    # Get upcoming bookings
    today = timezone.now().date()
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        status='confirmed',
        time_slot__date__gte=today
    ).order_by('time_slot__date')[:3]

    # Get recommended venues
    recommended_venues = Venue.objects.filter(status='active').order_by('?')[:3]

    context = {
        'profile': profile,
        'booking_stats': booking_stats,
        'recent_bookings': recent_bookings,
        'upcoming_bookings': upcoming_bookings,
        'recommended_venues': recommended_venues,
    }
    return render(request, 'booking/user_dashboard.html', context)


def register(request):
    """
    View for user registration.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account created for {username}! You are now logged in.')

            # Redirect to appropriate dashboard
            if hasattr(user, 'venue_manager') and user.is_staff and user.venue_manager.is_approved:
                return redirect('manager_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'auth/register.html', context)
