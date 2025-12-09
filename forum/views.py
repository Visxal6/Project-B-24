
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post, Comment
from .forms import PostForm, CommentForm
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


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_mod = is_moderator(request.user)

    if post.author != request.user and not is_mod:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    if request.method == 'POST':
        post.delete()
        return redirect('forum:post_list')
    return render(request, 'forum/post_confirm_delete.html', {'post': post, 'is_moderator_action': is_mod})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
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
    return render(request, 'forum/post_list.html', {'posts': posts})


def food_list(request):
    posts = Post.objects.filter(tag='food').order_by('-created_at')
    return render(request, 'forum/food_list.html', {'posts': posts})


def leaderboard_list(request):
    posts = Post.objects.filter(tag='leaderboard').order_by('-created_at')
    return render(request, 'forum/leaderboard_list.html', {'posts': posts})


def cio_list(request):
    posts = Post.objects.filter(tag='cio_leaders').order_by('-created_at')
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
