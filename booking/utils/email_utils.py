"""
Email utility functions for the booking app.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_booking_confirmation_email(booking):
    """
    Send a booking confirmation email to the user.
    
    Args:
        booking: The Booking instance that was confirmed
    """
    subject = f'Your Booking at {booking.venue.name} has been Confirmed'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = booking.user.email
    
    # Context for the email template
    context = {
        'booking': booking,
        'user': booking.user,
        'venue': booking.venue,
        'time_slot': booking.time_slot,
        'site_name': settings.SITE_NAME,
    }
    
    # Render HTML content
    html_content = render_to_string('emails/booking_confirmed.html', context)
    
    # Create plain text version by stripping HTML tags
    text_content = strip_tags(html_content)
    
    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email]
    )
    
    # Attach HTML content
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    email.send()
    
    return True
