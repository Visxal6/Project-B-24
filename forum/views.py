
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
            Q(privacy='friends_only', author__friendships__friend=user) |  # Friends' posts
            Q(privacy='cio_wide', author__friendships__friend__in=user_cio_friends)  # CIO-wide posts from same CIOs
        ).distinct()
    except Profile.DoesNotExist:
        # If user has no profile, only show public posts
        return posts_queryset.filter(privacy='public')


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    if request.method == 'POST':
        logger.info(f"Deleting post {pk} with image: {post.image.name if post.image else 'None'}")
        post.delete()
        logger.info(f"Post {pk} successfully deleted")
        return redirect('forum:post_list')
    return render(request, 'forum/post_confirm_delete.html', {'post': post})

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
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent_comment = Comment.objects.get(id=parent_id) if parent_id else None
            Comment.objects.create(
                post=post,
                author=request.user,
                content=form.cleaned_data['content'],
                parent=parent_comment
            )
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'forum/post_detail.html', { 'post': post , 'comments': comments , 'form': form })



@login_required
def post_create(request):
    if request.method == 'POST':
        logger.info(f"POST request received from user {request.user.id}")
        logger.debug(f"FILES in request: {list(request.FILES.keys())}")
        
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info(f"Form is valid, saving post for user {request.user.id}")
            logger.debug(f"Form cleaned data: {form.cleaned_data.keys()}")
            
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            logger.info(f"Post saved successfully with ID {post.pk}")
            
            # Handle multiple images
            images = request.FILES.getlist('images')
            if images:
                from .models import PostImage
                for image in images:
                    PostImage.objects.create(post=post, image=image)
                logger.info(f"Saved {len(images)} images for post {post.pk}")
            
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
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    
    if request.method == 'POST':
        comment.delete()
    
    return redirect('forum:post_detail', pk=comment.post.pk)