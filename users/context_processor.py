from .models import Notification

def unread_notifications(request):
    has_any = False
    if request.user.is_authenticated:
        has_any = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).exists()
    return {"has_unread_notifications": has_any}