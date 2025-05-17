from .models import Category, Notification

def common_context(request):
    """
    Context processor to add common data to all templates.
    """
    context = {
        'all_categories': Category.objects.all(),
    }

    # Add user notifications if user is authenticated
    if request.user.is_authenticated:
        # Get unread notifications
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')

        # Get recent notifications (both read and unread)
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        context.update({
            'unread_notifications': unread_notifications,
            'unread_notification_count': unread_notifications.count(),
            'recent_notifications': recent_notifications,
        })

    return context
