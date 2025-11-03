# social/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.db.models import Max

from django.conf import settings
from .models import FriendRequest, Friendship, Conversation, Message
User = settings.AUTH_USER_MODEL

UserModel = get_user_model()

# Search and return user that match the input
@login_required
def user_search(request):
    # Get user name from query
    q = request.GET.get("q", "").strip()
    results = []

    # Find users
    if q:
        results = UserModel.objects.filter(
            Q(username__icontains=q) | 
            Q(first_name__icontains=q) | 
            Q(last_name__icontains=q) | 
            Q(email__icontains=q)
        ).exclude(id=request.user.id)[:20]

    # Return users results
    return render(request, "social/user_search.html", 
                  {"q": q, 
                   "results": results
                   })


# Send friend request 
@login_required
def send_friend_request(request, user_id):
    # Find user
    to_user = get_object_or_404(UserModel, id=user_id)

    # Add yourself
    if to_user == request.user:
        messages.error(request, "You cannot add yourself.")
        return redirect("social:user_search")
    
    # Already friends
    if Friendship.friends_of(request.user).filter(id=to_user.id).exists():
        messages.info(request, "Already friends.")
        return redirect("social:user_search")
    
    # Pending request
    existing = FriendRequest.objects.filter(
        (Q(from_user=request.user, to_user=to_user) | 
         Q(from_user=to_user, to_user=request.user)) & 
         Q(status="pending")
    ).first()

    if existing:
        messages.info(request, "Request already pending.")
        return redirect("social:user_search")
    
    # Send request
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, "Friend request sent.")
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
    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status="pending")
    fr.accept()

    messages.success(request, f"You are now friends with {fr.from_user}.")
    return redirect("social:friends")

# Decline request
@login_required
def decline_request(request, req_id):
    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status="pending")
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


# Send a message
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
        Message.objects.create(
            conversation=convo, 
            sender=request.user, 
            body=body
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
    other = convo.participants.exclude(id=request.user.id).first()
    convos = _sidebar_convos(request) 
    return render(
        request,
        "social/chat_detail.html",
        {
            "convo": convo,
            "messages": msgs,
            "other": other,
            "convos": convos,  
        },
    )
