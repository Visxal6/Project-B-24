# social/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.utils import timezone

from django.conf import settings
from .models import FriendRequest, Friendship, Conversation, Message
User = settings.AUTH_USER_MODEL

from django.contrib.auth import get_user_model
UserModel = get_user_model()

@login_required
def user_search(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        results = UserModel.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
        ).exclude(id=request.user.id)[:20]
    return render(request, "social/user_search.html", {"q": q, "results": results})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(UserModel, id=user_id)
    if to_user == request.user:
        messages.error(request, "You cannot add yourself.")
        return redirect("social:user_search")
    # Already friends?
    if Friendship.friends_of(request.user).filter(id=to_user.id).exists():
        messages.info(request, "Already friends.")
        return redirect("social:user_search")
    # Existing pending in either direction?
    existing = FriendRequest.objects.filter(
        (Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user)) & Q(status="pending")
    ).first()
    if existing:
        messages.info(request, "Request already pending.")
        return redirect("social:user_search")

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, "Friend request sent.")
    return redirect("social:user_search")

@login_required
def incoming_requests(request):
    reqs = FriendRequest.objects.filter(to_user=request.user, status="pending").order_by("-created_at")
    return render(request, "social/incoming_requests.html", {"requests": reqs})

@login_required
def accept_request(request, req_id):
    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status="pending")
    fr.accept()
    messages.success(request, f"You are now friends with {fr.from_user}.")
    return redirect("social:friends")

@login_required
def decline_request(request, req_id):
    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status="pending")
    fr.decline()
    messages.info(request, "Friend request declined.")
    return redirect("social:incoming_requests")

@login_required
def friends_list(request):
    friends = Friendship.friends_of(request.user).order_by("username")
    return render(request, "social/friends.html", {"friends": friends})

@login_required
def start_chat_with_friend(request, user_id):
    other = get_object_or_404(get_user_model(), id=user_id)
    convo = Conversation.get_or_create_dm(request.user, other)
    return redirect("social:chat_detail", convo_id=convo.id)

@login_required
def chat_list(request):
    # Show all conversations the user is in (this can include non-friends → “people we message”)
    convos = request.user.conversations.all().order_by("-updated_at")
    return render(request, "social/chat_list.html", {"convos": convos})

@login_required
def chat_detail(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id, participants=request.user)
    msgs = convo.messages.select_related("sender").all()
    # For UI: who is the other participant?
    others = convo.participants.exclude(id=request.user.id)
    other = others.first() if others.exists() else None
    return render(request, "social/chat_detail.html", {"convo": convo, "messages": msgs, "other": other})

@login_required
def send_message(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id, participants=request.user)
    body = request.POST.get("body", "").strip()
    if body:
        Message.objects.create(conversation=convo, sender=request.user, body=body)
        # updated_at auto-updates on convo
    return redirect("social:chat_detail", convo_id=convo.id)
