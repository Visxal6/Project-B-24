from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import os, json

from .models import Task, Points


@login_required
def task_list(request):
    user = request.user

    tasks_file = os.path.join(settings.BASE_DIR, "leaderboard", "daily_tasks.json")
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            templates = json.load(f)
    except Exception:
        templates = []

    today = timezone.localdate()

    completed_qs = Task.objects.filter(user=user, completed=True, created_at__date=today)
    completed_titles = set(completed_qs.values_list("title", flat=True))

    tasks_todo = []
    tasks_done = []
    for idx, tpl in enumerate(templates):
        tpl_obj = dict(tpl)
        tpl_obj["idx"] = idx
        if tpl_obj.get("title") in completed_titles:
            tasks_done.append(tpl_obj)
        else:
            tasks_todo.append(tpl_obj)

    pts, _ = Points.objects.get_or_create(user=user)
    return render(request, "leaderboard/task_list.html", {"tasks_todo": tasks_todo, "tasks_done": tasks_done, "points": pts})


@login_required
def task_toggle(request, idx):
    if request.method != "POST":
        return redirect("leaderboard:task_list")

    tasks_file = os.path.join(settings.BASE_DIR, "leaderboard", "daily_tasks.json")
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            templates = json.load(f)
    except Exception:
        templates = []

    try:
        tpl = templates[int(idx)]
    except Exception:
        return redirect("leaderboard:task_list")

    user = request.user
    today = timezone.localdate()

    existing = Task.objects.filter(user=user, title=tpl.get("title"), created_at__date=today, completed=True).first()
    pts_obj, _ = Points.objects.get_or_create(user=user)
    if existing:
        pts_obj.add(-existing.points)
        existing.delete()
    else:
        new = Task.objects.create(user=user, title=tpl.get("title"), content=tpl.get("content", ""), points=int(tpl.get("points", 0)), completed=True)
        pts_obj.add(new.points)

    return redirect("leaderboard:task_list")


def events_list(request):
    return render(request, "leaderboard/events_list.html")