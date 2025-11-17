from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Interest
from .forms import UserRegisterForm, UserUpdateForm, ProfileForm


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
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            profile.bio = request.POST.get('bio', '').strip()
            interests_raw = request.POST.get('interests', '')
            interest_names = [
                name.strip() for name in interests_raw.split(',')
                if name.strip()
            ]
            profile.interests.clear()

            for name in interest_names:
                interest_obj, _ = Interest.objects.get_or_create(name=name)
                profile.interests.add(interest_obj)

            profile.is_completed = True
            profile.save()

            messages.success(
                request, 'Your profile has been updated successfully!'
            )
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)

    interests_string = ", ".join(i.name for i in profile.interests.all())

    return render(
        request,
        'users/profile.html',
        {
            'form': form,
            'bio': profile.bio,
            'interests': interests_string,
        },
    )


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
        return redirect("app-home")

    return render(request, "users/complete_profile.html")


@login_required
def post_login_redirect(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.is_completed:
        return redirect('complete_profile')

    return redirect('app-home')

@login_required
def profile_view(request, username):
    # Get the User and Profile being viewed
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    template_name = "users/profile_view.html"
    context = {
            "user": user,
            "profile": profile,
        }

    return render(request, template_name, context)