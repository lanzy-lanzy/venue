from django.urls import path
from . import views

# Main app URLs
urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('venues/', views.venue_list, name='venue_list'),
    path('venues/<int:venue_id>/', views.venue_detail, name='venue_detail'),

    # Booking related
    path('venues/<int:venue_id>/book/', views.book_venue, name='book_venue'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # User profile and dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # HTMX endpoints
    path('venues/<int:venue_id>/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('manager/venues/<int:venue_id>/edit-modal/', views.venue_edit_modal, name='venue_edit_modal'),
    path('manager/venues/add-modal/', views.venue_add_modal, name='venue_add_modal'),

    # Venue Manager URLs
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/venues/', views.manager_venues, name='manager_venues'),
    path('manager/venues/add/', views.manager_add_venue, name='manager_add_venue'),
    path('manager/venues/<int:venue_id>/edit/', views.manager_edit_venue, name='manager_edit_venue'),
    path('manager/bookings/', views.manager_bookings, name='manager_bookings'),
    path('manager/venues/<int:venue_id>/time-slots/', views.manager_time_slots, name='manager_time_slots'),
    path('manager/venues/<int:venue_id>/time-slots/add/', views.manager_add_time_slot, name='manager_add_time_slot'),
]
