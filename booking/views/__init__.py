from .home import home
from .venue_views import venue_list, venue_detail
from .booking_views import book_venue, booking_detail, my_bookings, cancel_booking
from .htmx_views import get_available_slots, venue_edit_modal, venue_add_modal
from .user_views import edit_profile, my_profile, register, user_dashboard, update_profile_picture, logout_view
from .auth_views import CustomLoginView
from .manager_views import (
    manager_dashboard,
    manager_venues,
    manager_add_venue,
    manager_edit_venue,
    manager_bookings,
    manager_time_slots,
    manager_add_time_slot,
    manager_delete_venue,
    manager_booking_detail,
    manager_confirm_booking,
    manager_cancel_booking
)

# Make all views available at the package level
__all__ = [
    'home',
    'venue_list',
    'venue_detail',
    'book_venue',
    'booking_detail',
    'my_bookings',
    'cancel_booking',
    'get_available_slots',
    'venue_edit_modal',
    'venue_add_modal',
    'edit_profile',
    'my_profile',
    'register',
    'user_dashboard',
    'update_profile_picture',
    'logout_view',
    'CustomLoginView',
    'manager_dashboard',
    'manager_venues',
    'manager_add_venue',
    'manager_edit_venue',
    'manager_bookings',
    'manager_time_slots',
    'manager_add_time_slot',
    'manager_delete_venue',
    'manager_booking_detail',
    'manager_confirm_booking',
    'manager_cancel_booking'
]
