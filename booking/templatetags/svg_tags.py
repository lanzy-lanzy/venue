from django import template
from django.utils.safestring import mark_safe
from booking.svg_icons import (
    venue_placeholder, 
    get_icon_for_category,
    CATEGORY_ICONS
)

register = template.Library()

@register.simple_tag
def svg_icon(icon_name=None):
    """
    Render an SVG icon by name.
    
    Usage:
        {% svg_icon "conference_room" %}
    """
    if not icon_name:
        return mark_safe(venue_placeholder())
    
    # Convert from template parameter format (with hyphens) to function name (with underscores)
    icon_name = icon_name.replace('-', '_')
    
    # Try to get the icon function from the module
    icon_func = globals().get(icon_name)
    
    if icon_func and callable(icon_func):
        return mark_safe(icon_func())
    
    # Fallback to placeholder
    return mark_safe(venue_placeholder())

@register.simple_tag
def category_icon(category_name=None):
    """
    Render an SVG icon for a category.
    
    Usage:
        {% category_icon category.name %}
    """
    if not category_name:
        return mark_safe(venue_placeholder())
    
    icon_func = get_icon_for_category(category_name)
    return mark_safe(icon_func())

@register.simple_tag
def venue_icon(venue=None):
    """
    Render an SVG icon for a venue based on its primary category.
    
    Usage:
        {% venue_icon venue %}
    """
    if not venue:
        return mark_safe(venue_placeholder())
    
    # Get the first category of the venue
    categories = venue.categories.all()
    if categories:
        return category_icon(categories[0].name)
    
    # Fallback to placeholder
    return mark_safe(venue_placeholder())
