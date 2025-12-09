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
    path('post/<int:pk>/update-privacy/', views.post_update_privacy, name='post_update_privacy'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),

    # Moderation endpoints
    path('post/<int:pk>/flag-inappropriate/',
         views.post_flag_inappropriate, name='post_flag_inappropriate'),
    path('post/<int:pk>/edit-moderation/',
         views.post_edit_moderation, name='post_edit_moderation'),
    path('post/<int:pk>/remove-moderation/',
         views.post_remove_moderation, name='post_remove_moderation'),
    path('comment/<int:pk>/flag-inappropriate/',
         views.comment_flag_inappropriate, name='comment_flag_inappropriate'),
    path('comment/<int:pk>/edit-moderation/',
         views.comment_edit_moderation, name='comment_edit_moderation'),
    path('comment/<int:pk>/remove-moderation/',
         views.comment_remove_moderation, name='comment_remove_moderation'),

    # Moderation notes endpoints
    path('post/<int:post_id>/notes/',
         views.flagged_post_notes, name='flagged_post_notes'),
    path('comment/<int:comment_id>/notes/',
         views.flagged_comment_notes, name='flagged_comment_notes'),
]
