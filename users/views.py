from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Interest
from leaderboard.models import Points
from leaderboard.models import Task as LeaderboardTask
from django.utils import timezone
from datetime import timedelta
import os, json
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
    
    individual_leaderboard = []
    cio_leaderboard = []
    member_leaderboard = []
    is_cio = False
    
    try:
        # Individual Leaderboard: Users that are NOT CIOs (explicitly exclude CIO role)
        individual_qs = (
            Points.objects.select_related('user', 'user__profile')
            .exclude(user__profile__role='cio')
            .order_by('-score')[:10]
        )
        
        for idx, p in enumerate(individual_qs, start=1):
            individual_leaderboard.append({
                'rank': idx,
                'points': p.score,
                'user': p.user,
            })
    except Exception:
        individual_leaderboard = []
    
    try:
        # CIO Leaderboard: total member points — sum all follower points for each CIO
        from django.db.models import Sum, Q
        from social.models import Friendship
        
        # Get all CIOs
        cios = Profile.objects.filter(role="cio").select_related('user')
        
        cio_scores = []
        for cio_profile in cios:
            cio_user = cio_profile.user
            
            # Sum points of all followers (members) of this CIO
            followers = Friendship.friends_of(cio_user)
            total_points = (
                Points.objects.filter(user__in=followers)
                .aggregate(total=Sum('score'))['total'] or 0
            )
            
            cio_scores.append({
                'user': cio_user,
                'total_points': total_points,
            })
        
        # Sort by total points descending and take top 10
        cio_scores.sort(key=lambda x: x['total_points'], reverse=True)
        cio_scores = cio_scores[:10]
        
        for idx, cio_data in enumerate(cio_scores, start=1):
            cio_leaderboard.append({
                'rank': idx,
                'points': cio_data['total_points'],
                'user': cio_data['user'],
            })
    except Exception:
        cio_leaderboard = []
    
    # Member Leaderboard: Only shown to CIOs, lists their top followers
    try:
        from social.models import Friendship
        
        # Check if current user is a CIO
        if request.user.is_authenticated:
            user_profile = Profile.objects.filter(user=request.user, role="cio").first()
            if user_profile:
                is_cio = True
                
                # Get all followers of this CIO
                followers = Friendship.friends_of(request.user)
                
                # Get their points and sort
                member_qs = Points.objects.filter(
                    user__in=followers
                ).select_related('user', 'user__profile').order_by('-score')[:10]
                
                for idx, p in enumerate(member_qs, start=1):
                    member_leaderboard.append({
                        'rank': idx,
                        'points': p.score,
                        'user': p.user,
                    })
    except Exception:
        member_leaderboard = []

    # Weekly challenge progress for current user (for the dashboard widget)
    weekly_total = 0
    weekly_completed = 0
    if request.user.is_authenticated:
        tasks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'leaderboard', 'weekly_tasks.json')
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                weekly_total = len(templates)
                titles = [t.get('title') for t in templates]
        except Exception:
            titles = []

        today = timezone.localdate()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        if titles:
            weekly_completed = LeaderboardTask.objects.filter(
                user=request.user,
                completed=True,
                title__in=titles,
                created_at__date__gte=start_of_week,
                created_at__date__lt=end_of_week,
            ).count()

    # Daily challenge progress for current user (for the dashboard widget)
    daily_total = 0
    daily_completed = 0
    if request.user.is_authenticated:
        daily_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'leaderboard', 'daily_tasks.json')
        try:
            with open(daily_file, 'r', encoding='utf-8') as f:
                daily_templates = json.load(f)
                daily_total = len(daily_templates)
                daily_titles = [t.get('title') for t in daily_templates]
        except Exception:
            daily_titles = []

        if daily_titles:
            today = timezone.localdate()
            tomorrow = today + timedelta(days=1)
            daily_completed = LeaderboardTask.objects.filter(
                user=request.user,
                completed=True,
                title__in=daily_titles,
                created_at__date__gte=today,
                created_at__date__lt=tomorrow,
            ).count()

    # Upcoming events count for dashboard
    upcoming_events = 0
    try:
        from leaderboard.models import Event
        upcoming_events = Event.objects.filter(start_at__gte=timezone.now()).count()
    except Exception:
        upcoming_events = 0

    # current user's personal score
    my_score = 0
    if request.user.is_authenticated:
        try:
            pts = Points.objects.filter(user=request.user).first()
            my_score = pts.score if pts and pts.score is not None else 0
        except Exception:
            my_score = 0

    return render(request, 'users/dashboard.html', {
        'individual_leaderboard': individual_leaderboard,
        'cio_leaderboard': cio_leaderboard,
        'member_leaderboard': member_leaderboard,
        'is_cio': is_cio,
        'weekly_total': weekly_total,
        'weekly_completed': weekly_completed,
        'daily_total': daily_total,
        'daily_completed': daily_completed,
        'upcoming_events': upcoming_events,
        'my_score': my_score,
    })


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
    cio_members = []
    # If the profile belongs to a CIO, include their followers as a member leaderboard
    try:
        if profile.role == 'cio':
            from social.models import Friendship
            from leaderboard.models import Points

            followers = Friendship.friends_of(user)
            member_qs = (
                Points.objects.filter(user__in=followers)
                .select_related('user', 'user__profile')
                .order_by('-score')[:10]
            )

            for idx, p in enumerate(member_qs, start=1):
                cio_members.append({'rank': idx, 'points': p.score, 'user': p.user})
    except Exception:
        cio_members = []
    # relationship status for the current viewer
    is_friend = False
    request_pending = False
    if request.user.is_authenticated:
        try:
            from social.models import Friendship, FriendRequest
            is_friend = Friendship.friends_of(request.user).filter(id=user.id).exists()
            request_pending = FriendRequest.objects.filter(from_user=request.user, to_user=user, status='pending').exists()
        except Exception:
            is_friend = False
            request_pending = False

    context = {
        "user": user,
        "profile": profile,
        "is_friend": is_friend,
        "request_pending": request_pending,
        "cio_members": cio_members,
    }

    return render(request, template_name, context)


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect("app-login")

    return render(request, "users/delete_account.html")