from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path('task-list/', views.task_list, name='task_list'),
    path('task/<int:idx>/toggle/', views.task_toggle, name='task_toggle'),
    path('events-list/', views.events_list, name='events_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('weekly/', views.weekly_list_view, name='weekly_list'),
    path('weekly/<int:idx>/toggle/', views.weekly_toggle, name='weekly_toggle'),
]