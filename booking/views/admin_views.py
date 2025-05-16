from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from booking.models import Venue, Category, TimeSlot, Booking, VenueManager, UserProfile
from booking.forms import VenueForm, UserProfileForm
from booking.decorators.admin_decorators import admin_required


@login_required
@admin_required
def admin_dashboard(request):
    """
    Admin dashboard view showing system overview.
    """
    # Get counts for various entities
    users_count = User.objects.count()
    venues_count = Venue.objects.count()
    bookings_count = Booking.objects.count()
    pending_bookings_count = Booking.objects.filter(status='pending').count()

    # Get recent users
    recent_users = User.objects.order_by('-date_joined')[:5]

    # Get recent bookings
    recent_bookings = Booking.objects.order_by('-booking_date')[:5]

    # Get venues with most bookings
    popular_venues = Venue.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]

    context = {
        'users_count': users_count,
        'venues_count': venues_count,
        'bookings_count': bookings_count,
        'pending_bookings_count': pending_bookings_count,
        'recent_users': recent_users,
        'recent_bookings': recent_bookings,
        'popular_venues': popular_venues,
    }

    return render(request, 'admin/dashboard.html', context)


@login_required
@admin_required
def admin_users(request):
    """
    Admin view for managing users.
    """
    # Handle POST requests for user actions
    if request.method == 'POST':
        action_type = request.POST.get('action_type', '')

        # Handle adding a new user
        if action_type == '':  # Default form submission from add user modal
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            role = request.POST.get('role', 'regular')
            user_type = request.POST.get('user_type', 'regular')

            # Validate form data
            if not username or not email or not password1 or not password2:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('admin_users')

            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
                return redirect('admin_users')

            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" is already taken.')
                return redirect('admin_users')

            if User.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" is already registered.')
                return redirect('admin_users')

            # Create user
            is_staff = user_type in ['staff', 'admin']
            is_superuser = user_type == 'admin'

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff,
                is_superuser=is_superuser
            )

            # Create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            # Create venue manager if user is staff
            if is_staff:
                from booking.models import VenueManager
                VenueManager.objects.create(user=user)

            messages.success(request, f'User "{username}" has been created successfully.')
            return redirect('admin_users')

        # Handle bulk actions
        elif action_type == 'bulk_action':
            bulk_action = request.POST.get('bulk_action', '')
            selected_users = request.POST.getlist('selected_users', [])

            if not selected_users:
                messages.error(request, 'No users selected.')
                return redirect('admin_users')

            if not bulk_action:
                messages.error(request, 'No action selected.')
                return redirect('admin_users')

            # Get selected users
            users_to_update = User.objects.filter(id__in=selected_users)

            # Apply bulk action
            if bulk_action == 'activate':
                users_to_update.update(is_active=True)
                messages.success(request, f'{len(selected_users)} users have been activated.')

            elif bulk_action == 'deactivate':
                users_to_update.update(is_active=False)
                messages.success(request, f'{len(selected_users)} users have been deactivated.')

            elif bulk_action == 'make_staff':
                users_to_update.update(is_staff=True)
                # Create venue manager for each user
                for user in users_to_update:
                    if not hasattr(user, 'venue_manager'):
                        from booking.models import VenueManager
                        VenueManager.objects.create(user=user)
                messages.success(request, f'{len(selected_users)} users have been made managers.')

            elif bulk_action == 'remove_staff':
                users_to_update.update(is_staff=False)
                messages.success(request, f'{len(selected_users)} users have had manager role removed.')

            elif bulk_action == 'change_role':
                new_role = request.POST.get('new_role', '')
                if not new_role:
                    messages.error(request, 'No role selected.')
                    return redirect('admin_users')

                # Update user profiles
                for user in users_to_update:
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.role = new_role
                    profile.save()

                messages.success(request, f'{len(selected_users)} users have had their role updated.')

            return redirect('admin_users')

        # Handle toggle user status
        elif action_type == 'toggle_status':
            user_id = request.POST.get('user_id')
            action = request.POST.get('action')

            if not user_id or not action:
                messages.error(request, 'Invalid request.')
                return redirect('admin_users')

            user = get_object_or_404(User, id=user_id)

            if action == 'activate':
                user.is_active = True
                user.save()
                messages.success(request, f'User "{user.username}" has been activated.')

            elif action == 'deactivate':
                user.is_active = False
                user.save()
                messages.success(request, f'User "{user.username}" has been deactivated.')

            return redirect('admin_users')

        # Handle toggle user role
        elif action_type == 'toggle_role':
            user_id = request.POST.get('user_id')
            action = request.POST.get('action')

            if not user_id or not action:
                messages.error(request, 'Invalid request.')
                return redirect('admin_users')

            user = get_object_or_404(User, id=user_id)

            if action == 'make_staff':
                user.is_staff = True
                user.save()

                # Create venue manager if not exists
                if not hasattr(user, 'venue_manager'):
                    from booking.models import VenueManager
                    VenueManager.objects.create(user=user)

                messages.success(request, f'User "{user.username}" is now a manager.')

            elif action == 'remove_staff':
                user.is_staff = False
                user.save()
                messages.success(request, f'Manager role has been removed from "{user.username}".')

            return redirect('admin_users')

    # Handle GET requests for filtering and export
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    is_staff_filter = request.GET.get('is_staff', '')
    status_filter = request.GET.get('status', '')
    date_joined_filter = request.GET.get('date_joined', '')
    sort_by = request.GET.get('sort_by', '-date_joined')
    has_bookings_filter = request.GET.get('has_bookings', '')
    is_superuser_filter = request.GET.get('is_superuser', '')
    per_page = request.GET.get('per_page', '10')

    # Handle export action
    action_type = request.GET.get('action_type', '')
    if action_type == 'export':
        # This would normally generate and return a file
        # For now, just show a message
        messages.info(request, 'Export functionality will be implemented soon.')
        return redirect('admin_users')

    # Start with all users
    users = User.objects.all()

    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if role_filter:
        users = users.filter(profile__role=role_filter)

    if is_staff_filter:
        is_staff = is_staff_filter == 'true'
        users = users.filter(is_staff=is_staff)

    if status_filter:
        is_active = status_filter == 'active'
        users = users.filter(is_active=is_active)

    if date_joined_filter:
        users = users.filter(date_joined__gte=date_joined_filter)

    if has_bookings_filter:
        if has_bookings_filter == 'yes':
            users = users.filter(bookings__isnull=False).distinct()
        elif has_bookings_filter == 'no':
            users = users.filter(bookings__isnull=True)

    if is_superuser_filter:
        is_superuser = is_superuser_filter == 'true'
        users = users.filter(is_superuser=is_superuser)

    # Apply sorting
    users = users.order_by(sort_by)

    # Get counts for stats
    active_users_count = User.objects.filter(is_active=True).count()
    managers_count = User.objects.filter(is_staff=True).count()
    from datetime import datetime, timedelta
    one_week_ago = datetime.now() - timedelta(days=7)
    new_users_count = User.objects.filter(date_joined__gte=one_week_ago).count()

    # Paginate results
    try:
        per_page_int = int(per_page)
    except ValueError:
        per_page_int = 10

    paginator = Paginator(users, per_page_int)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all available roles for filtering
    roles = UserProfile.USER_ROLE_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'is_staff_filter': is_staff_filter,
        'status_filter': status_filter,
        'date_joined_filter': date_joined_filter,
        'sort_by': sort_by,
        'has_bookings_filter': has_bookings_filter,
        'is_superuser_filter': is_superuser_filter,
        'per_page': per_page,
        'roles': roles,
        'active_users_count': active_users_count,
        'managers_count': managers_count,
        'new_users_count': new_users_count,
    }

    return render(request, 'admin/users.html', context)


@login_required
@admin_required
def admin_user_detail(request, user_id):
    """
    Admin view for user details.
    """
    user = get_object_or_404(User, id=user_id)

    # Get user's bookings
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')

    # Check if user is a venue manager
    is_venue_manager = hasattr(user, 'venue_manager')

    # If user is a venue manager, get their venues
    venues = []
    if is_venue_manager:
        venues = Venue.objects.filter(manager=user.venue_manager)

    context = {
        'user_obj': user,  # Using user_obj to avoid conflict with request.user
        'bookings': bookings,
        'is_venue_manager': is_venue_manager,
        'venues': venues,
    }

    return render(request, 'admin/user_detail.html', context)


@login_required
@admin_required
def admin_user_edit(request, user_id):
    """
    Admin view for editing user details.
    """
    user = get_object_or_404(User, id=user_id)

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Process form submission
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            # Update user model fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']

            # Update staff status if provided
            is_staff = request.POST.get('is_staff') == 'on'
            user.is_staff = is_staff

            # Update superuser status if provided
            is_superuser = request.POST.get('is_superuser') == 'on'
            user.is_superuser = is_superuser

            # Save user
            user.save()

            # Save profile
            form.save()

            # If user is staff, ensure they have a venue manager profile
            if is_staff and not hasattr(user, 'venue_manager'):
                from booking.models import VenueManager
                VenueManager.objects.create(user=user)

            messages.success(request, f'User {user.username} has been updated successfully.')
            return redirect('admin_user_detail', user_id=user.id)
    else:
        # Initialize form with user data
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'user_obj': user,
    }

    return render(request, 'admin/user_edit.html', context)


@login_required
@admin_required
def admin_venues(request):
    """
    Admin view for managing venues.
    """
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    # Start with all venues
    venues = Venue.objects.all().order_by('-created_at')

    # Apply filters
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(manager__user__username__icontains=search_query)
        )

    if status_filter:
        venues = venues.filter(status=status_filter)

    if category_filter:
        venues = venues.filter(categories__id=category_filter)

    # Paginate results
    paginator = Paginator(venues, 10)  # Show 10 venues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all categories and statuses for filtering
    categories = Category.objects.all()
    statuses = Venue.STATUS_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': categories,
        'statuses': statuses,
    }

    return render(request, 'admin/venues.html', context)


@login_required
@admin_required
def admin_venue_detail(request, venue_id):
    """
    Admin view for venue details.
    """
    venue = get_object_or_404(Venue, id=venue_id)

    # Get venue's bookings
    bookings = Booking.objects.filter(venue=venue).order_by('-booking_date')

    # Get venue's time slots
    time_slots = TimeSlot.objects.filter(venue=venue).order_by('date', 'start_time')

    context = {
        'venue': venue,
        'bookings': bookings,
        'time_slots': time_slots,
    }

    return render(request, 'admin/venue_detail.html', context)


@login_required
@admin_required
def admin_venue_edit(request, venue_id):
    """
    Admin view for editing venue details.
    """
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, f'Venue "{venue.name}" has been updated successfully.')
            return redirect('admin_venue_detail', venue_id=venue.id)
    else:
        form = VenueForm(instance=venue)

    context = {
        'form': form,
        'venue': venue,
    }

    return render(request, 'admin/venue_edit.html', context)
