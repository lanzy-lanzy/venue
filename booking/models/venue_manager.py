from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class VenueManager(models.Model):
    """
    Represents a venue manager who can manage multiple venues.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='venue_manager')
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Manager"
    
    def get_managed_venues_count(self):
        """
        Returns the count of venues managed by this manager.
        """
        return self.managed_venues.count()
    
    class Meta:
        ordering = ['-created_at']


# Signal to create a VenueManager profile when a user is created with is_staff=True
@receiver(post_save, sender=User)
def create_venue_manager(sender, instance, created, **kwargs):
    """
    Signal handler to create a VenueManager when a staff user is created.
    """
    if created and instance.is_staff:
        VenueManager.objects.create(user=instance)


# Signal to update VenueManager when User is updated
@receiver(post_save, sender=User)
def save_venue_manager(sender, instance, **kwargs):
    """
    Signal handler to save VenueManager when the associated User is saved.
    """
    if hasattr(instance, 'venue_manager'):
        instance.venue_manager.save()
