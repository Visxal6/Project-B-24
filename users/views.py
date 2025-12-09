from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Interest
from leaderboard.models import Points
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
            profile.display_name = request.POST.get('display_name', '').strip()
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


@login_required
def profile_view(request):
    picture, _ = ProfilePicture.objects.get_or_create(user=request.user)

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if "image" in request.FILES:
            picture.image = request.FILES["image"]
            picture.save()
            messages.success(request, "Profile picture updated!")
            return redirect("profile-view")

    form = UserUpdateForm(instance=request.user)
    interest_list = profile.interests.all()

    return render(
        request,
        "users/profile-view.html",
        {
            "form": form,
            "picture": picture,
            "bio": profile.bio,
            "interests": interest_list,
        },
    )


def dashboard(request):
    if request.user.is_authenticated:
        messages.success(request, f"Welcome back, {request.user.username}!")
    top = []
    try:
        qs = Points.objects.select_related('user').order_by('-score')[:10]
        for idx, p in enumerate(qs, start=1):
            top.append({
                'rank': idx,
                'points': p.score,
                'user': p.user,
            })
    except Exception:
        top = []

    return render(request, 'users/dashboard.html', {'leaderboard': top})


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
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    template_name = "users/profile_view.html"
    context = {
        "user": user,
        "profile": profile,
    }

    return render(request, template_name, context)


def is_moderator(user):
    """Check if user is a moderator"""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.is_moderator
    except:
        return False


@login_required
def suspend_user(request, username):
    """Allow moderators to suspend users"""
    if not is_moderator(request.user):
        return redirect('app-home')

    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    if profile.is_suspended:
        messages.warning(request, f"{user.username} is already suspended.")
        return redirect('users:profile_view', username=username)

    if request.method == 'POST':
        reason = request.POST.get('suspension_reason', '')
        if not reason:
            messages.error(request, 'Please provide a reason for suspension.')
            return render(request, 'users/suspend_user.html', {'target_user': user, 'profile': profile})

        profile.suspend(request.user, reason)
        messages.success(
            request, f"{user.username} has been suspended for: {reason}")
        return redirect('users:profile_view', username=username)

    return render(request, 'users/suspend_user.html', {'target_user': user, 'profile': profile})


@login_required
def reinstate_user(request, username):
    """Allow moderators to reinstate suspended users"""
    if not is_moderator(request.user):
        return redirect('app-home')

    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    if not profile.is_suspended:
        messages.warning(request, f"{user.username} is not suspended.")
        return redirect('users:profile_view', username=username)

    if request.method == 'POST':
        profile.reinstate()
        messages.success(request, f"{user.username} has been reinstated.")
        return redirect('users:profile_view', username=username)

    return render(request, 'users/reinstate_user.html', {'target_user': user, 'profile': profile})


@login_required
def suspended_users_list(request):
    """Show list of suspended users (moderators only)"""
    if not is_moderator(request.user):
        return redirect('app-home')

    suspended_profiles = Profile.objects.filter(
        is_suspended=True).select_related('user', 'suspended_by')

    return render(request, 'users/suspended_users_list.html', {'suspended_profiles': suspended_profiles})


@login_required
def search_users(request):
    """Search for users (moderators only)"""
    if not is_moderator(request.user):
        return redirect('app-home')

    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Search by username or display name
        results = User.objects.filter(
            username__icontains=query
        ) | User.objects.filter(
            profile__display_name__icontains=query
        )
        results = results.select_related('profile').distinct()

    return render(request, 'users/search_users.html', {
        'query': query,
        'results': results,
        'is_moderator': is_moderator(request.user)
    })


@login_required
def flagged_content(request):
    """View flagged posts and comments (moderators only)"""
    if not is_moderator(request.user):
        return redirect('app-home')

    from forum.models import Post, Comment

    flagged_posts = Post.objects.filter(
        is_flagged_inappropriate=True).select_related('author')
    flagged_comments = Comment.objects.filter(
        is_flagged_inappropriate=True).select_related('author', 'post')

    return render(request, 'users/flagged_content.html', {
        'flagged_posts': flagged_posts,
        'flagged_comments': flagged_comments,
        'is_moderator': is_moderator(request.user)
    })
