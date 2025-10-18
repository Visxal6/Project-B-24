from django.contrib import messages
from django.shortcuts import render

# render html for a request path


def home(request):
    if request.user.is_authenticated:
        messages.success(request, f"Welcome back, {request.user.username}!")

    return render(request, 'app/home.html')

