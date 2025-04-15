from django.db import models
from .venue import Venue


class TimeSlot(models.Model):
    """
    Represents a time slot for a venue that can be booked.
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.venue.name} - {self.date} ({self.start_time} to {self.end_time})"
    
    def duration_hours(self):
        """
        Calculate the duration of the time slot in hours.
        """
        return (self.end_time.hour - self.start_time.hour)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['venue', 'date', 'start_time']
