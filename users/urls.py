from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/view/<str:username>/', views.profile_view, name='profile_view'),
    path("notifications/", views.notifications_list, name="notifications"),

]