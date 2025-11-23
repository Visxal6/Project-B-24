from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path('task-list/', views.task_list, name='task_list'),
    path('task/<int:idx>/toggle/', views.task_toggle, name='task_toggle'),
    path('events-list/', views.events_list, name='events_list'),
]