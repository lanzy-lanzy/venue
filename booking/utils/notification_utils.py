"""
Notification utility functions for the booking app.
"""
from booking.models import Notification


def create_booking_confirmation_notification(booking):
    """
    Create a booking confirmation notification for the user.
    
    Args:
        booking: The Booking instance that was confirmed
    """
    title = f'Your Booking at {booking.venue.name} has been Confirmed'
    message = (
        f"Great news! Your booking at {booking.venue.name} has been confirmed by the venue manager.\n\n"
        f"Booking Details:\n"
        f"- Booking ID: #{booking.id}\n"
        f"- Venue: {booking.venue.name}\n"
        f"- Address: {booking.venue.address}\n"
        f"- Date: {booking.time_slot.date.strftime('%A, %B %d, %Y')}\n"
        f"- Time: {booking.time_slot.start_time.strftime('%I:%M %p')} - {booking.time_slot.end_time.strftime('%I:%M %p')}\n"
        f"- Number of Guests: {booking.num_guests}\n"
        f"- Total Price: ${booking.total_price}\n\n"
        f"If you have any questions or need to make changes to your booking, please contact us or the venue directly."
    )
    
    notification = Notification.objects.create(
        user=booking.user,
        type='booking_confirmation',
        title=title,
        message=message,
        related_object_id=booking.id,
        related_object_type='booking'
    )
    
    return notification
