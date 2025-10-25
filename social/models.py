# social/models.py
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q, UniqueConstraint
from django.contrib.auth import get_user_model   

User = settings.AUTH_USER_MODEL 
UserModel = get_user_model()  


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        CANCELED = "canceled", "Canceled"

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    to_user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    status    = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["from_user", "to_user"],
                name="uq_pending_friend_request_pair",
                condition=Q(status="pending"),
            )
        ]

    def clean(self):
        if self.from_user_id == self.to_user_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("You cannot friend yourself.")

    @transaction.atomic
    def accept(self):
        if self.status != self.Status.PENDING:
            return
        self.status = self.Status.ACCEPTED
        self.responded_at = models.functions.Now()
        self.save(update_fields=["status", "responded_at"])
        Friendship.make_friends(self.from_user, self.to_user)

    @transaction.atomic
    def decline(self):
        if self.status == self.Status.PENDING:
            self.status = self.Status.DECLINED
            self.responded_at = models.functions.Now()
            self.save(update_fields=["status", "responded_at"])


class Friendship(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="related_to")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "friend")]

    @staticmethod
    @transaction.atomic
    def make_friends(u1, u2):
        if u1 == u2:
            return
        Friendship.objects.get_or_create(user=u1, friend=u2)
        Friendship.objects.get_or_create(user=u2, friend=u1)

    @staticmethod
    def friends_of(user):
        return UserModel.objects.filter(related_to__user=user)


class Conversation(models.Model):
    participants = models.ManyToManyField(User, through="ConversationParticipant", related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_or_create_dm(u1, u2):
        qs = Conversation.objects.filter(
            participants=u1
        ).filter(
            participants=u2
        ).annotate(
            count=models.Count("participants")
        ).filter(count=2)
        convo = qs.first()
        if convo:
            return convo
        convo = Conversation.objects.create()
        ConversationParticipant.objects.bulk_create([
            ConversationParticipant(conversation=convo, user=u1),
            ConversationParticipant(conversation=convo, user=u2),
        ])
        return convo


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("conversation", "user")]


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    body         = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
