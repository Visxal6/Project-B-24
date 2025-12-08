# social/views.py
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.db.models import Max
from django.urls import reverse
from users.models import Notification

from django.conf import settings
from .models import FriendRequest, Friendship, Conversation, Message, ConversationParticipant
from users.models import Profile
User = settings.AUTH_USER_MODEL

UserModel = get_user_model()

# Search and return user that match the input
@login_required
def user_search(request):
    q = request.GET.get("q", "").strip()
    results = []

    if q:
        terms = q.split()

        # Start with single-field matching
        query = (
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

        for term in terms:
            query |= Q(first_name__icontains=term) | Q(last_name__icontains=term)

        results = (
            UserModel.objects
            .filter(query)
            .exclude(id=request.user.id)
            .distinct()[:20]
        )

    return render(
        request,
        "social/user_search.html",
        {"q": q, "results": results}
    )

# Send friend request
@login_required
def send_friend_request(request, user_id):
    # Find user
    to_user = get_object_or_404(UserModel, id=user_id)
    
    # Determine redirect URL (prefer referer, fallback to user_search)
    redirect_url = request.META.get('HTTP_REFERER', None)
    if not redirect_url:
        redirect_url = "social:user_search"
    else:
        # If referer is from find_cios, keep it; otherwise use user_search
        if 'cios' not in redirect_url:
            redirect_url = "social:user_search"

    # Add yourself
    if to_user == request.user:
        messages.error(request, "You cannot add yourself.")
        if isinstance(redirect_url, str):
            return redirect(redirect_url)
        else:
            return redirect("social:user_search")

    # Already friends
    if Friendship.friends_of(request.user).filter(id=to_user.id).exists():
        messages.info(request, "Already friends.")
        if isinstance(redirect_url, str):
            return redirect(redirect_url)
        else:
            return redirect("social:user_search")

    # Pending request
    existing = FriendRequest.objects.filter(
        (Q(from_user=request.user, to_user=to_user) |
         Q(from_user=to_user, to_user=request.user)) &
        Q(status="pending")
    ).first()

    if existing:
        messages.info(request, "Request already pending.")
        if isinstance(redirect_url, str):
            return redirect(redirect_url)
        else:
            return redirect("social:user_search")

    # Send request
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, "Friend request sent.")

    # Notify the recipient about the friend request
    Notification.objects.create(
        user=to_user,
        notif_type="friend_request",
        text=f"{request.user.username} sent you a friend request",
        url=reverse("social:incoming_requests"),
    )

    if isinstance(redirect_url, str):
        return redirect(redirect_url)
    else:
        return redirect("social:user_search")


# Incoming Request


@login_required
def incoming_requests(request):
    # Retrieves all pending request
    reqs = FriendRequest.objects.filter(
        to_user=request.user, status="pending"
    ).order_by("-created_at")

    return render(request, "social/incoming_requests.html",
                  {
                      "requests": reqs
                  })

# Accept request


@login_required
def accept_request(request, req_id):
    # Get friend request
    fr = get_object_or_404(FriendRequest, id=req_id,
                           to_user=request.user, status="pending")
    fr.accept()

    messages.success(request, f"You are now friends with {fr.from_user}.")
    return redirect("social:friends")

# Decline request


@login_required
def decline_request(request, req_id):
    fr = get_object_or_404(FriendRequest, id=req_id,
                           to_user=request.user, status="pending")
    fr.decline()

    messages.info(request, "Friend request declined.")
    return redirect("social:incoming_requests")


# Start Chat
@login_required
def start_chat_with_friend(request, user_id):
    # Get friend
    other = get_object_or_404(get_user_model(), id=user_id)

    # Get or create a conversation
    convo = Conversation.get_or_create_dm(request.user, other)

    return redirect("social:chat_detail", convo_id=convo.id)


@login_required
def send_message(request, convo_id):
    # Get conversation
    convo = get_object_or_404(
        Conversation,
        id=convo_id,
        participants=request.user
    )

    # Get message from body
    body = request.POST.get("body", "").strip()

    # Create message
    if body:
        msg = Message.objects.create(
            conversation=convo,
            sender=request.user,
            body=body
        )

        # 🔔 create notifications for everyone else in the convo
        recipients = convo.participants.exclude(id=request.user.id)
        url = reverse("social:chat_detail", kwargs={"convo_id": convo.id})

        for user in recipients:
            Notification.objects.create(
                user=user,
                notif_type="message",
                text=f"New message from {request.user.username}",
                url=url,
            )

    return redirect("social:chat_detail", convo_id=convo.id)


@login_required
def friends_list(request):
    """Show the friends page with sidebar chats."""
    friends = Friendship.friends_of(request.user).order_by("username")
    convos = _sidebar_convos(request)
    return render(
        request,
        "social/social.html",
        {
            "friends": friends,
            "convos": convos,
            "convo": None,
        },
    )


@login_required
def chat_list(request):
    convos_qs = (
        request.user.conversations
        .prefetch_related("participants", "messages")
        .annotate(last_msg_at=Max("messages__created_at"))
        .order_by("-last_msg_at", "-updated_at")
    )

    items = []
    for c in convos_qs:
        other = c.participants.exclude(id=request.user.id).first()
        items.append({
            "id": c.id,
            "other": other,                         # a User object
            "display": other.get_full_name() or other.username if other else f"Conversation {c.id}",
            "last": c.messages.last(),
        })

    return render(request, "social/chat_list.html", {"items": items})


def _sidebar_convos(request):
    qs = (
        request.user.conversations
        .prefetch_related("participants", "messages")
        .annotate(last_msg_at=Max("messages__created_at"))
        .order_by("-last_msg_at", "-updated_at")
    )

    convos = []
    for c in qs:
        other = c.participants.exclude(id=request.user.id).first()
        if other:
            display = other.username
        else:
            display = f"Conversation {c.id}"
        convos.append({"id": c.id, "display": display})
    return convos


@login_required
def chat_detail(request, convo_id):
    """Show the chat detail page with messages and sidebar."""
    convo = get_object_or_404(
        Conversation, id=convo_id, participants=request.user)
    msgs = convo.messages.select_related("sender").all()
    participants = convo.participants.all()
    other = participants.exclude(id=request.user.id).first()
    convos = _sidebar_convos(request)

    # 🔔 mark message notifications for this convo as read
    url = reverse("social:chat_detail", kwargs={"convo_id": convo.id})
    Notification.objects.filter(
        user=request.user,
        notif_type="message",
        url=url,
        is_read=False,
    ).update(is_read=True)

    return render(
        request,
        "social/chat_detail.html",
        {
            "convo": convo,
            "messages": msgs,
            "other": other,
            "participants": participants, 
            "convos": convos,
        },
    )


# new need testing

@login_required
def chat_messages_api(request, convo_id):
    convo = get_object_or_404(
        Conversation, id=convo_id, participants=request.user)
    after = request.GET.get("after")
    qs = convo.messages.select_related("sender")
    if after:
        qs = qs.filter(id__gt=after)

    if not after:
        qs = qs.order_by("-id")[:50]

    msgs = qs.order_by("id").values(
        "id", "body", "created_at",
        "sender__username",
    )

    data = [{
        "id": m["id"],
        "body": m["body"],
        "created_at": m["created_at"].isoformat(),
        "sender": m["sender__username"],
    } for m in msgs]

    return JsonResponse({"messages": data})


@require_http_methods(["POST"])
@login_required
def send_message_api(request, convo_id):
    convo = get_object_or_404(
        Conversation, id=convo_id, participants=request.user)
    body = (request.POST.get("body") or "").strip()
    if not body:
        return JsonResponse({"ok": False, "error": "empty"}, status=400)

    msg = Message.objects.create(
        conversation=convo, sender=request.user, body=body)

    # 🔔 notifications for API-based send (same recipients logic)
    recipients = convo.participants.exclude(id=request.user.id)
    url = reverse("social:chat_detail", kwargs={"convo_id": convo.id})

    for user in recipients:
        Notification.objects.create(
            user=user,
            notif_type="message",
            text=f"New message from {request.user.username}",
            url=url,
        )

    return JsonResponse({
        "ok": True,
        "message": {
            "id": msg.id,
            "body": msg.body,
            "created_at": msg.created_at.isoformat(),
            "sender": request.user.username,
        }
    }, status=201)



@login_required
def find_cios(request):
    """Display a list of CIOs that the user can follow."""
    # Get all CIO users, excluding the current user
    cios = UserModel.objects.filter(
        profile__role="cio"
    ).exclude(id=request.user.id).select_related("profile").order_by("username")
    
    # Get the current user's friends to highlight them
    current_friends = Friendship.friends_of(request.user).values_list("id", flat=True)
    
    # Get pending friend requests from the current user
    pending_requests = FriendRequest.objects.filter(
        from_user=request.user,
        status="pending"
    ).values_list("to_user_id", flat=True)
    
    # Prepare CIO data with relationship status
    cios_data = []
    for cio in cios:
        cios_data.append({
            "user": cio,
            "profile": cio.profile,
            "is_friend": cio.id in current_friends,
            "request_pending": cio.id in pending_requests,
        })
    
    return render(request, "social/find_cios.html", {
        "cios": cios_data
    })

@login_required
def create_group_chat(request):
    friends = Friendship.friends_of(request.user)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        member_ids = request.POST.getlist("members")

        if not name:
            messages.error(request, "Group name is required.")
            return redirect("social:create_group_chat")

        if len(member_ids) < 2:
            messages.error(request, "Select at least 2 people to form a group.")
            return redirect("social:create_group_chat")

        convo = Conversation.objects.create()
        ConversationParticipant.objects.create(conversation=convo, user=request.user)

        # Add selected members
        for uid in member_ids:
            ConversationParticipant.objects.create(conversation=convo, user_id=uid)

        messages.success(request, f"Group '{name}' created.")
        return redirect("social:chat_detail", convo_id=convo.id)

    return render(request, "social/create_group_chat.html", {
        "friends": friends
    })

