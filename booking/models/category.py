from django.db import models


class Category(models.Model):
    """
    Represents a category for venues (e.g., Conference Hall, Wedding Venue, etc.)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
