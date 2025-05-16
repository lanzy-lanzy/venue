from django.db import models
from django.contrib.auth.models import User
from .booking import Booking


class Payment(models.Model):
    """
    Represents a payment for a booking.
    """
    PAYMENT_METHOD_CHOICES = [
        ('gcash', 'GCash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='gcash')
    reference_number = models.CharField(max_length=100, blank=True)
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment for Booking #{self.booking.id} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-payment_date']
