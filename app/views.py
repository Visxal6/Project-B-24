from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time, timedelta
import os, json
from django.conf import settings
from leaderboard.models import Task

# render html for a request path


def home(request):
    if request.user.is_authenticated:
        messages.success(request, f"Welcome back, {request.user.username}!")
    
    tasks_remaining = 0
    time_until_reset = None
    weekly_tasks_remaining = 0
    time_until_weekly_reset = None
    
    # Calculate remaining tasks and time until reset
    if request.user.is_authenticated:
        try:
            # Load daily tasks template
            tasks_file = os.path.join(settings.BASE_DIR, "leaderboard", "daily_tasks.json")
            with open(tasks_file, "r", encoding="utf-8") as f:
                templates = json.load(f)
            
            total_tasks = len(templates)
            
            # Get completed tasks for today
            today = timezone.localdate()
            completed_today = Task.objects.filter(
                user=request.user, 
                completed=True, 
                created_at__date=today
            ).count()
            
            tasks_remaining = total_tasks - completed_today
            
            # Calculate time until midnight (daily reset)
            now = timezone.now()
            tomorrow = today + timedelta(days=1)
            midnight_tomorrow = timezone.make_aware(
                datetime.combine(tomorrow, time.min)
            )
            time_until_reset = midnight_tomorrow - now
            
            # Format time until reset as human-readable string
            total_seconds = int(time_until_reset.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_until_reset = f"{hours}h {minutes}m {seconds}s"
            
            # Load weekly tasks template
            weekly_file = os.path.join(settings.BASE_DIR, "leaderboard", "weekly_tasks.json")
            with open(weekly_file, "r", encoding="utf-8") as f:
                weekly_templates = json.load(f)
            
            total_weekly_tasks = len(weekly_templates)
            
            # Get completed weekly tasks for this week
            # Week starts on Monday (weekday=0)
            week_start = today - timedelta(days=today.weekday())
            completed_weekly = Task.objects.filter(
                user=request.user,
                completed=True,
                created_at__date__gte=week_start,
                created_at__date__lte=today
            ).count()
            
            weekly_tasks_remaining = total_weekly_tasks - completed_weekly
            
            # Calculate time until Sunday midnight (weekly reset)
            days_until_sunday = (6 - today.weekday()) % 7
            if days_until_sunday == 0:
                days_until_sunday = 7
            
            next_sunday = today + timedelta(days=days_until_sunday)
            midnight_sunday = timezone.make_aware(
                datetime.combine(next_sunday, time.min)
            )
            time_until_weekly_reset = midnight_sunday - now
            
            # Format weekly time until reset as human-readable string
            total_seconds_weekly = int(time_until_weekly_reset.total_seconds())
            hours_w, remainder_w = divmod(total_seconds_weekly, 3600)
            minutes_w, seconds_w = divmod(remainder_w, 60)
            time_until_weekly_reset = f"{hours_w}h {minutes_w}m {seconds_w}s"
            
        except Exception:
            tasks_remaining = -1
            time_until_reset = -1
            weekly_tasks_remaining = -1
            time_until_weekly_reset = -1

    return render(request, 'app/home.html', {
        'tasks_remaining': tasks_remaining,
        'time_until_reset': time_until_reset,
        'weekly_tasks_remaining': weekly_tasks_remaining,
        'time_until_weekly_reset': time_until_weekly_reset
    })

