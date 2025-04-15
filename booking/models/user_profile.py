from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Represents a user profile with additional information and preferences.
    """
    USER_ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('regular', 'Regular User'),
        ('premium', 'Premium User'),
        ('corporate', 'Corporate Client'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='regular')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    booking_preferences = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def get_booking_count(self):
        """Returns the count of bookings made by this user."""
        return self.user.bookings.count()
    
    def get_active_bookings(self):
        """Returns the active (confirmed) bookings for this user."""
        return self.user.bookings.filter(status='confirmed')
    
    def get_profile_picture_url(self):
        """Return the URL of the profile picture or a default if none exists"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        # Return None to allow templates to use a default image or placeholder
        return None
    
    def is_eligible_for_booking_type(self, booking_type):
        """Check if user is eligible for a specific booking type based on their role"""
        if booking_type == 'standard':
            return True
        elif booking_type == 'corporate':
            return self.role in ['corporate']
        elif booking_type == 'event':
            return self.role in ['premium', 'corporate']
        elif booking_type == 'private':
            return self.role in ['premium', 'corporate']
        return False
    
    def get_discount_percentage(self):
        """Return the discount percentage based on user role"""
        if self.role == 'premium':
            return 10
        elif self.role == 'corporate':
            return 15
        return 0
    
    def can_book_venue(self, venue):
        """Check if user can book a specific venue based on their role"""
        # All users can book active venues
        if venue.status != 'active':
            return False
            
        # Check if venue has any restrictions
        if hasattr(venue, 'restrictions'):
            # Example: Some venues might be premium-only
            if getattr(venue, 'premium_only', False) and self.role not in ['premium', 'corporate']:
                return False
                
        # Corporate venues might only be available to corporate users
        corporate_categories = ['Corporate', 'Business', 'Conference']
        venue_categories = [cat.name for cat in venue.categories.all()]
        
        if any(cat in corporate_categories for cat in venue_categories) and self.role != 'corporate':
            # Allow premium users to book corporate venues with approval
            if self.role == 'premium':
                return True, "Requires approval"
            return False
            
        return True
    
    def get_booking_statistics(self):
        """Get booking statistics for this user"""
        from django.utils import timezone
        from django.db.models import Sum, Avg
        
        # Get all bookings for this user
        bookings = self.user.bookings.all()
        
        # Get counts by status
        confirmed_count = bookings.filter(status='confirmed').count()
        pending_count = bookings.filter(status='pending').count()
        cancelled_count = bookings.filter(status='cancelled').count()
        
        # Get upcoming bookings
        today = timezone.now().date()
        upcoming_bookings = bookings.filter(
            status='confirmed',
            time_slot__date__gte=today
        ).order_by('time_slot__date')
        
        # Get total spent
        total_spent = bookings.filter(status='confirmed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Get average booking price
        avg_price = bookings.filter(status='confirmed').aggregate(Avg('total_price'))['total_price__avg'] or 0
        
        return {
            'total_bookings': bookings.count(),
            'confirmed_count': confirmed_count,
            'pending_count': pending_count,
            'cancelled_count': cancelled_count,
            'upcoming_bookings': upcoming_bookings,
            'total_spent': total_spent,
            'avg_price': avg_price,
        }
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# Signal to create a UserProfile for regular users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """Signal handler to create a UserProfile when a non-staff user is created."""
    # Only create profile for non-staff users who don't already have one
    if created and not instance.is_staff and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)


# Signal to update UserProfile when User is updated
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Signal handler to save UserProfile when the associated User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
