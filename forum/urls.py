from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('food/', views.food_list, name='food_list'),
    path('leaderboard/', views.leaderboard_list, name='leaderboard_list'),
    path('cio/', views.cio_list, name='cio_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]

