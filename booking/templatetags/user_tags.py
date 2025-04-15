from django import template

register = template.Library()

@register.filter
def has_profile(user):
    """
    Check if a user has a profile.
    Usage: {% if user|has_profile %}
    """
    return hasattr(user, 'profile')

@register.filter
def has_profile_picture(user):
    """
    Check if a user has a profile picture.
    Usage: {% if user|has_profile_picture %}
    """
    return hasattr(user, 'profile') and user.profile.profile_picture
