from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from booking.models import Notification


@login_required
def notifications(request):
    """
    View for displaying all notifications for the current user.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'booking/notifications.html', context)


@login_required
def notification_detail(request, notification_id):
    """
    View for displaying a specific notification.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Mark as read if not already
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    context = {
        'notification': notification,
    }
    return render(request, 'booking/notification_detail.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """
    View for marking a notification as read.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Mark as read
    notification.is_read = True
    notification.save()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))


@login_required
def mark_all_notifications_read(request):
    """
    View for marking all notifications as read.
    """
    # Mark all notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'All notifications marked as read.')
    
    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))
