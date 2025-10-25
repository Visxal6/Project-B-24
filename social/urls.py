# social/urls.py
from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    path("", views.user_search, name="user_search"),
    path("request/<int:user_id>/", views.send_friend_request, name="send_request"),
    path("requests/", views.incoming_requests, name="incoming_requests"),
    path("requests/<int:req_id>/accept/", views.accept_request, name="accept_request"),
    path("requests/<int:req_id>/decline/", views.decline_request, name="decline_request"),

    path("friends/", views.friends_list, name="friends"),
    path("friends/start-chat/<int:user_id>/", views.start_chat_with_friend, name="start_chat"),

    path("chats/", views.chat_list, name="chat_list"),
    path("chats/<int:convo_id>/", views.chat_detail, name="chat_detail"),
    path("chats/<int:convo_id>/send/", views.send_message, name="send_message"),
]
