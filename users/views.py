from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Interest
from .forms import UserRegisterForm, UserUpdateForm, ProfileCompleteForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'Your account has been created  {user.username}!, You are now able to login.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below.')
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})


def dashboard(request):
    if request.user.is_authenticated:
        messages.success(request, f"Welcome back, {request.user.username}!")

    return render(request, 'users/dashboard.html')


@login_required
def complete_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        role = request.POST.get("role")
        interests_values = request.POST.getlist(
            "interests")

        if not role:
            messages.error(
                request, "Please choose if you are a Student or a CIO.")
            return render(request, "users/complete_profile.html")

        profile.role = role
        profile.is_completed = True
        profile.save()

        interest_objs = []
        for value in interests_values:
            obj, _ = Interest.objects.get_or_create(name=value.capitalize())
            interest_objs.append(obj)

        profile.interests.set(interest_objs)

        messages.success(request, "Your profile has been completed!")
        return redirect("dashboard")

    return render(request, "users/complete_profile.html")


@login_required
def post_login_redirect(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.is_completed:
        return redirect('complete_profile')

    return redirect('dashboard')
