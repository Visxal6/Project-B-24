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
    
    individual_leaderboard = []
    cio_leaderboard = []
    member_leaderboard = []
    is_cio = False
    
    try:
        # Individual Leaderboard: Users that are NOT CIOs
        individual_qs = Points.objects.select_related('user', 'user__profile').filter(
            user__profile__role__in=["student", "other", ""]
        ).order_by('-score')[:10]
        
        for idx, p in enumerate(individual_qs, start=1):
            individual_leaderboard.append({
                'rank': idx,
                'points': p.score,
                'user': p.user,
            })
    except Exception:
        individual_leaderboard = []
    
    try:
        # CIO Leaderboard: Sum points of all users following each CIO
        from django.db.models import Sum, Q
        from social.models import Friendship
        
        # Get all CIOs
        cios = Profile.objects.filter(role="cio").select_related('user')
        
        cio_scores = []
        for cio_profile in cios:
            cio_user = cio_profile.user
            
            # Get all friends of this CIO (users following the CIO)
            followers = Friendship.friends_of(cio_user)
            
            # Sum all points of the CIO's followers
            total_points = Points.objects.filter(
                user__in=followers
            ).aggregate(total=Sum('score'))['total'] or 0
            
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

    return render(request, 'users/dashboard.html', {
        'individual_leaderboard': individual_leaderboard,
        'cio_leaderboard': cio_leaderboard,
        'member_leaderboard': member_leaderboard,
        'is_cio': is_cio,
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
    context = {
        "user": user,
        "profile": profile,
    }

    return render(request, template_name, context)
