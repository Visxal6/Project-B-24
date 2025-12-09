
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Post, Comment
from .forms import PostForm, CommentForm
from social.models import Friendship
from users.models import Profile
import logging

logger = logging.getLogger(__name__)


def is_moderator(user):
    """Check if user is a moderator"""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.is_moderator
    except:
        return False


def can_user_view_post(user, post):
    """
    Check if a user can view a post based on privacy settings.

    Privacy rules:
    - 'public': Everyone can view
    - 'cio_wide': Only users in the same CIO(s) as the post author can view
    - 'friends_only': Only direct friends of the post author can view
    - Post author can always view their own post
    """
    # Post author can always view their own post
    if user == post.author:
        return True

    # Public posts are viewable by everyone
    if post.privacy == 'public':
        return True

    # Anonymous users can only see public posts
    if not user.is_authenticated:
        return False

    # Friends only: check if user is a friend of the author
    if post.privacy == 'friends_only':
        return Friendship.objects.filter(
            user=post.author,
            friend=user
        ).exists()

    # CIO-wide: check if user is in any of the same CIOs as the author
    if post.privacy == 'cio_wide':
        # Get the author's CIO (assuming a user can be a CIO or follow CIOs)
        try:
            author_profile = post.author.profile
            viewer_profile = user.profile

            # Check if the author is a CIO
            if author_profile.role == 'cio':
                # Check if the viewer is a friend of this CIO
                return Friendship.objects.filter(
                    user=post.author,
                    friend=user
                ).exists()

            # Check if viewer and author are both followers of the same CIO
            # Get CIOs that the viewer follows
            viewer_cio_friends = Friendship.objects.filter(
                user=viewer_profile.user
            ).values_list('friend__profile__user_id', flat=True).filter(
                friend__profile__role='cio'
            )

            # Get CIOs that the author follows
            author_cio_friends = Friendship.objects.filter(
                user=author_profile.user
            ).values_list('friend__profile__user_id', flat=True).filter(
                friend__profile__role='cio'
            )

            # Check if there's any overlap
            return bool(set(viewer_cio_friends) & set(author_cio_friends))
        except Profile.DoesNotExist:
            return False

    return False


def get_viewable_posts(user, posts_queryset):
    """
    Filter a queryset of posts to only include those the user can view.

    For efficiency with larger datasets, this approach:
    1. Always includes posts by the user themselves
    2. Always includes public posts
    3. For authenticated users, checks privacy individually
    """
    if not user.is_authenticated:
        # Anonymous users can only see public posts
        return posts_queryset.filter(privacy='public')

    # Include: author's own posts, all public posts, friends-only from their friends,
    # and cio-wide from users in same CIOs
    try:
        user_profile = user.profile
        user_cio_friends = Friendship.objects.filter(
            user=user
        ).values_list('friend__profile__user_id', flat=True).filter(
            friend__profile__role='cio'
        )

        # Posts authored by the user, all public posts, or posts from friends
        return posts_queryset.filter(
            Q(author=user) |  # User's own posts
            Q(privacy='public') |  # Public posts
            # Friends' posts
            Q(privacy='friends_only', author__friendships__friend=user) |
            # CIO-wide posts from same CIOs
            Q(privacy='cio_wide', author__friendships__friend__in=user_cio_friends)
        ).distinct()
    except Profile.DoesNotExist:
        # If user has no profile, only show public posts
        return posts_queryset.filter(privacy='public')


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_mod = is_moderator(request.user)

    if post.author != request.user and not is_mod:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    if request.method == 'POST':
        logger.info(
            f"Deleting post {pk} with image: {post.image.name if post.image else 'None'}")
        post.delete()
        logger.info(f"Post {pk} successfully deleted")
        return redirect('forum:post_list')
    return render(request, 'forum/post_confirm_delete.html', {'post': post, 'is_moderator_action': is_mod})


@login_required
def post_update_privacy(request, pk):
    """Update the privacy setting of a post."""
    post = get_object_or_404(Post, pk=pk)

    # Only the post author can update privacy settings
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to update this post's privacy.")

    if request.method == 'POST':
        privacy = request.POST.get('privacy')

        # Validate the privacy choice
        valid_choices = [choice[0] for choice in Post.PRIVACY_CHOICES]
        if privacy in valid_choices:
            post.privacy = privacy
            post.save(update_fields=['privacy'])
            logger.info(f"Post {pk} privacy updated to {privacy}")
        else:
            logger.warning(f"Invalid privacy choice: {privacy}")

        return redirect('forum:post_detail', pk=post.pk)

    return HttpResponseForbidden("Method not allowed.")


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if user can view this post
    if not can_user_view_post(request.user, post):
        return HttpResponseForbidden("You do not have permission to view this post.")

    comments = post.comments.filter(parent__isnull=True)

    if request.method == "POST":
        # Check if user is suspended
        if request.user.is_authenticated:
            try:
                if request.user.profile.is_suspended:
                    from django.contrib import messages
                    messages.error(
                        request, f"Your account has been suspended. Reason: {request.user.profile.suspension_reason}")
                    return redirect('forum:post_detail', pk=post.pk)
            except:
                pass

        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent_comment = Comment.objects.get(
                id=parent_id) if parent_id else None
            Comment.objects.create(
                post=post,
                author=request.user,
                content=form.cleaned_data['content'],
                parent=parent_comment
            )
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'forum/post_detail.html', {'post': post, 'comments': comments, 'form': form, 'is_moderator': is_moderator(request.user)})


@login_required
def post_create(request):
    # Check if user is suspended
    try:
        if request.user.profile.is_suspended:
            from django.contrib import messages
            messages.error(
                request, f"Your account has been suspended. Reason: {request.user.profile.suspension_reason}")
            return redirect('forum:post_list')
    except:
        pass

    if request.method == 'POST':
        logger.info(f"POST request received from user {request.user.id}")
        logger.debug(f"FILES in request: {list(request.FILES.keys())}")

        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info(
                f"Form is valid, saving post for user {request.user.id}")
            logger.debug(f"Form cleaned data: {form.cleaned_data.keys()}")

            post = form.save(commit=False)
            post.author = request.user
            logger.debug(f"Image field before save: {post.image}")

            post.save()
            logger.info(f"Post saved successfully with ID {post.pk}")
            logger.info(f"Image path in database: {post.image}")

            return redirect('forum:post_detail', pk=post.pk)
        else:
            logger.warning(f"Form validation failed. Errors: {form.errors}")
    else:
        form = PostForm()
    return render(request, 'forum/post_create.html', {'form': form})


def post_list(request):
    posts = Post.objects.filter(tag='general').order_by('-created_at')
    posts = get_viewable_posts(request.user, posts)
    return render(request, 'forum/post_list.html', {'posts': posts})


def food_list(request):
    posts = Post.objects.filter(tag='food').order_by('-created_at')
    posts = get_viewable_posts(request.user, posts)
    return render(request, 'forum/food_list.html', {'posts': posts})


def leaderboard_list(request):
    posts = Post.objects.filter(tag='leaderboard').order_by('-created_at')
    posts = get_viewable_posts(request.user, posts)
    return render(request, 'forum/leaderboard_list.html', {'posts': posts})


def cio_list(request):
    posts = Post.objects.filter(tag='cio_leaders').order_by('-created_at')
    posts = get_viewable_posts(request.user, posts)
    return render(request, 'forum/cio_list.html', {'posts': posts})


@login_required
def post_edit_moderation(request, pk):
    """Allow moderators to edit posts flagged as inappropriate"""
    if not is_moderator(request.user):
        return HttpResponseForbidden("You do not have permission to moderate content.")

    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.is_flagged_inappropriate = False
            post.moderation_note = request.POST.get('moderation_note', '')
            post.save()
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'forum/post_moderation_edit.html', {'form': form, 'post': post})


@login_required
def post_flag_inappropriate(request, pk):
    """Allow moderators to flag posts as inappropriate"""
    if not is_moderator(request.user):
        return HttpResponseForbidden("You do not have permission to moderate content.")

    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        post.is_flagged_inappropriate = True
        post.moderation_note = request.POST.get('moderation_note', '')
        post.save()
        return redirect('forum:post_detail', pk=post.pk)

    return render(request, 'forum/post_flag_inappropriate.html', {'post': post})


@login_required
def post_remove_moderation(request, pk):
    """Allow moderators to remove posts completely"""
    if not is_moderator(request.user):
        return HttpResponseForbidden("You do not have permission to moderate content.")

    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('forum:post_list')

    return render(request, 'forum/post_remove_moderation.html', {'post': post})


@login_required
def comment_edit_moderation(request, pk):
    """Allow moderators to edit comments flagged as inappropriate"""
    if not is_moderator(request.user):
        return HttpResponseForbidden("You do not have permission to moderate content.")

    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_flagged_inappropriate = False
            comment.moderation_note = request.POST.get('moderation_note', '')
            comment.save()
            return redirect('forum:post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'forum/comment_moderation_edit.html', {'form': form, 'comment': comment})


@login_required
def comment_flag_inappropriate(request, pk):
    """Allow moderators to flag comments as inappropriate"""
    if not is_moderator(request.user):
        return HttpResponseForbidden("You do not have permission to moderate content.")

    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        comment.is_flagged_inappropriate = True
        comment.moderation_note = request.POST.get('moderation_note', '')
        comment.save()
        return redirect('forum:post_detail', pk=comment.post.pk)

    return render(request, 'forum/comment_flag_inappropriate.html', {'comment': comment})


@login_required
def comment_remove_moderation(request, pk):
    """Allow moderators to remove comments completely"""
    if not is_moderator(request.user):
        return HttpResponseForbidden("You do not have permission to moderate content.")

    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        comment.delete()
        return redirect('forum:post_detail', pk=comment.post.pk)

    return render(request, 'forum/comment_remove_moderation.html', {'comment': comment})


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    is_mod = is_moderator(request.user)

    if comment.author != request.user and not is_mod:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    if request.method == 'POST':
        comment.delete()

    return redirect('forum:post_detail', pk=comment.post.pk)


@login_required
def flagged_post_notes(request, post_id):
    """View and edit moderation notes for a flagged post"""
    if not is_moderator(request.user):
        return redirect('app-home')

    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        post.moderation_note = request.POST.get('moderation_note', '')
        post.save()
        from django.contrib import messages
        messages.success(request, 'Moderation note updated successfully.')
        return redirect('users:flagged_content')

    return render(request, 'forum/flagged_post_notes.html', {'post': post})


@login_required
def flagged_comment_notes(request, comment_id):
    """View and edit moderation notes for a flagged comment"""
    if not is_moderator(request.user):
        return redirect('app-home')

    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == 'POST':
        comment.moderation_note = request.POST.get('moderation_note', '')
        comment.save()
        from django.contrib import messages
        messages.success(request, 'Moderation note updated successfully.')
        return redirect('users:flagged_content')

    return render(request, 'forum/flagged_comment_notes.html', {'comment': comment})
