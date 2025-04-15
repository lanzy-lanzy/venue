from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class VenueManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='venue_manager')
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Manager"

    def get_managed_venues_count(self):
        return self.managed_venues.count()


class Venue(models.Model):
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
        return reverse('venue_detail', args=[str(self.id)])

    def is_available(self):
        return self.status == 'active'

    def get_upcoming_bookings(self):
        return self.bookings.filter(time_slot__date__gte=timezone.now().date(), status='confirmed')


class TimeSlot(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.venue.name} - {self.date} ({self.start_time} to {self.end_time})"

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['venue', 'date', 'start_time']


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    BOOKING_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('corporate', 'Corporate'),
        ('event', 'Event'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    num_guests = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default='standard')
    special_requests = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.venue.name} ({self.time_slot})"

    def get_user_role(self):
        """Get the role of the user who made this booking"""
        if hasattr(self.user, 'profile'):
            return self.user.profile.role
        return 'guest'

    def can_be_modified(self):
        """Check if booking can be modified based on user role and status"""
        # Cancelled bookings can't be modified
        if self.status == 'cancelled':
            return False

        # Check based on user role
        user_role = self.get_user_role()

        # Premium and corporate users can modify bookings even after confirmation
        if user_role in ['premium', 'corporate']:
            return True

        # Regular users can only modify pending bookings
        return self.status == 'pending'

    def can_be_cancelled(self):
        """Check if booking can be cancelled based on user role and status"""
        # Already cancelled bookings can't be cancelled again
        if self.status == 'cancelled':
            return False

        # Get time until booking
        from django.utils import timezone
        now = timezone.now()
        booking_date = timezone.make_aware(timezone.datetime.combine(self.time_slot.date, self.time_slot.start_time))
        hours_until_booking = (booking_date - now).total_seconds() / 3600

        # Check based on user role
        user_role = self.get_user_role()

        # Premium and corporate users can cancel up to 1 hour before
        if user_role in ['premium', 'corporate']:
            return hours_until_booking >= 1

        # Regular users can cancel up to 24 hours before
        return hours_until_booking >= 24

    def get_role_benefits(self):
        """Get role-specific benefits for this booking"""
        user_role = self.get_user_role()
        benefits = []

        if user_role == 'premium':
            benefits = [
                'Priority check-in',
                'Complimentary refreshments',
                'Extended booking hours',
                'Flexible cancellation (up to 1 hour before)',
                '10% discount on booking price'
            ]
        elif user_role == 'corporate':
            benefits = [
                'Dedicated event coordinator',
                'Access to premium equipment',
                'Complimentary catering options',
                'Flexible cancellation (up to 1 hour before)',
                '15% discount on booking price',
                'Priority booking for future events'
            ]
        elif user_role == 'regular':
            benefits = [
                'Standard check-in',
                'Regular booking hours',
                'Standard cancellation policy (24 hours notice)'
            ]

        return benefits

    def save(self, *args, **kwargs):
        # Calculate total price if not set
        if not self.total_price:
            hours = (self.time_slot.end_time.hour - self.time_slot.start_time.hour)
            base_price = self.venue.hourly_rate * hours

            # Apply discounts based on user role if the user has a profile
            if hasattr(self.user, 'profile'):
                user_role = self.user.profile.role
                if user_role == 'premium':
                    # Premium users get 10% discount
                    base_price = base_price * 0.9
                elif user_role == 'corporate':
                    # Corporate clients get 15% discount
                    base_price = base_price * 0.85
                    # Set booking type to corporate for corporate users
                    if self.booking_type == 'standard':
                        self.booking_type = 'corporate'

            self.total_price = base_price

        # Mark time slot as unavailable when booking is confirmed
        if self.status == 'confirmed' and self.time_slot.is_available:
            self.time_slot.is_available = False
            self.time_slot.save()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-booking_date']


# Signal to create a VenueManager profile when a user is created with is_staff=True
@receiver(post_save, sender=User)
def create_venue_manager(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    if created and instance.is_staff:
        VenueManager.objects.create(user=instance)


# Signal to update VenueManager when User is updated
@receiver(post_save, sender=User)
def save_venue_manager(sender, instance, **kwargs):  # pylint: disable=unused-argument
    if hasattr(instance, 'venue_manager'):
        instance.venue_manager.save()


