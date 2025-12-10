from .models import Notification

def unread_notifications(request):
    has_any = False
    count = 0
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
        has_any = count > 0
    return {"has_unread_notifications": has_any, "unread_notifications_count": count}