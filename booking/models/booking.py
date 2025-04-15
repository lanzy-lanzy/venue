from django.db import models
from django.contrib.auth.models import User
from .venue import Venue
from .time_slot import TimeSlot


class Booking(models.Model):
    """
    Represents a booking of a venue for a specific time slot.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    num_guests = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.venue.name} ({self.time_slot})"
    
    def save(self, *args, **kwargs):
        """
        Override the save method to calculate total price and update time slot availability.
        """
        # Calculate total price if not set
        if not self.total_price:
            hours = self.time_slot.duration_hours()
            self.total_price = self.venue.hourly_rate * hours
        
        # Mark time slot as unavailable when booking is confirmed
        if self.status == 'confirmed' and self.time_slot.is_available:
            self.time_slot.is_available = False
            self.time_slot.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-booking_date']
