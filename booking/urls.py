from django.urls import path, include
from . import views
from . import urls_admin

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

    # Payment related
    path('bookings/<int:booking_id>/payment/', views.submit_payment, name='submit_payment'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/', views.payment_history, name='payment_history'),

    # User profile and dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/update-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('logout/', views.logout_view, name='custom_logout'),

    # HTMX endpoints
    path('venues/<int:venue_id>/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('manager/venues/<int:venue_id>/edit-modal/', views.venue_edit_modal, name='venue_edit_modal'),
    path('manager/venues/add-modal/', views.venue_add_modal, name='venue_add_modal'),

    # Venue Manager URLs
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/venues/', views.manager_venues, name='manager_venues'),
    path('manager/venues/add/', views.manager_add_venue, name='manager_add_venue'),
    path('manager/venues/<int:venue_id>/edit/', views.manager_edit_venue, name='manager_edit_venue'),
    path('manager/venues/<int:venue_id>/delete/', views.manager_delete_venue, name='manager_delete_venue'),
    path('manager/bookings/', views.manager_bookings, name='manager_bookings'),
    path('manager/bookings/<int:booking_id>/confirm/', views.manager_confirm_booking, name='manager_confirm_booking'),
    path('manager/bookings/<int:booking_id>/cancel/', views.manager_cancel_booking, name='manager_cancel_booking'),
    path('manager/bookings/<int:booking_id>/', views.manager_booking_detail, name='manager_booking_detail'),
    path('manager/venues/<int:venue_id>/time-slots/', views.manager_time_slots, name='manager_time_slots'),
    path('manager/venues/<int:venue_id>/time-slots/add/', views.manager_add_time_slot, name='manager_add_time_slot'),

    # Manager Payment URLs
    path('manager/payments/', views.manager_payments, name='manager_payments'),
    path('manager/payments/<int:payment_id>/', views.manager_payment_detail, name='manager_payment_detail'),
    path('manager/payments/<int:payment_id>/verify/', views.manager_verify_payment, name='manager_verify_payment'),
    path('manager/payments/<int:payment_id>/reject/', views.manager_reject_payment, name='manager_reject_payment'),

    # Custom Admin URLs - separate from Django's built-in admin
    path('admin-dashboard/', include('booking.urls_admin')),
]
