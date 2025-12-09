from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/view/<str:username>/',
         views.profile_view, name='profile_view'),

    # User suspension endpoints
    path('suspend/<str:username>/', views.suspend_user, name='suspend_user'),
    path('reinstate/<str:username>/', views.reinstate_user, name='reinstate_user'),
    path('suspended-users/', views.suspended_users_list,
         name='suspended_users_list'),

    # Moderator tools
    path('search/', views.search_users, name='search_users'),
    path('flagged-content/', views.flagged_content, name='flagged_content'),
]
