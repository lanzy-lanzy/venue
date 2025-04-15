from django.db import models
from django.urls import reverse
from django.utils import timezone
from .category import Category
from .venue_manager import VenueManager


class Venue(models.Model):
    """
    Represents a venue that can be booked.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='venues/', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='venues')
    manager = models.ForeignKey(VenueManager, on_delete=models.SET_NULL, null=True, related_name='managed_venues')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Returns the URL to access a detail record for this venue.
        """
        return reverse('venue_detail', args=[str(self.id)])
    
    def is_available(self):
        """
        Checks if the venue is available for booking.
        """
        return self.status == 'active'
    
    def get_upcoming_bookings(self):
        """
        Returns all confirmed upcoming bookings for this venue.
        """
        return self.bookings.filter(time_slot__date__gte=timezone.now().date(), status='confirmed')
    
    class Meta:
        ordering = ['name']
