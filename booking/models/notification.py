from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """
    Represents a notification for a user.
    """
    TYPE_CHOICES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_cancellation', 'Booking Cancellation'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
