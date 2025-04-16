from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from django.http import JsonResponse
from booking.forms import UserProfileForm, RegistrationForm
from booking.models import Booking, Venue, UserProfile


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
            # Save the form data
            user_profile = form.save(commit=False)

            # Update the User model fields
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Save the profile
            user_profile.save()

            messages.success(request, 'Your profile has been updated successfully!')

            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
            else:
                # Return redirect response for non-AJAX requests
                return redirect('my_profile')
        else:
            # If the form is invalid
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response with errors for AJAX requests
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
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


@login_required
def update_profile_picture(request):
    """
    View for updating user profile picture via AJAX or form submission.
    """
    # Check if this is a direct GET request (not AJAX)
    if request.method == 'GET':
        # Redirect to the edit profile page
        return redirect('edit_profile')

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        # Get the user's profile or create one if it doesn't exist
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # Update the profile picture
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()

        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            return JsonResponse({'success': True, 'message': 'Profile picture updated successfully'})
        else:
            # Return redirect response for non-AJAX requests
            messages.success(request, 'Profile picture updated successfully!')
            return redirect(request.META.get('HTTP_REFERER', '/'))

    # Return error response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Error: No file uploaded'}, status=400)
    else:
        messages.error(request, 'Error: No file uploaded')
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def logout_view(request):
    """
    View for logging out users.
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')
