from django.urls import path
from booking import views

# URLs for custom admin views
# These are separate from Django's built-in admin
urlpatterns = [
    # Admin dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # User management
    path('users/', views.admin_users, name='admin_users'),
    path('users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    
    # Venue management
    path('venues/', views.admin_venues, name='admin_venues'),
    path('venues/<int:venue_id>/', views.admin_venue_detail, name='admin_venue_detail'),
    path('venues/<int:venue_id>/edit/', views.admin_venue_edit, name='admin_venue_edit'),
]
