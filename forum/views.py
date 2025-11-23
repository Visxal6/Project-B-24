
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post, Comment
from .forms import PostForm, CommentForm
import logging

logger = logging.getLogger(__name__)

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    if request.method == 'POST':
        post.delete()
        return redirect('forum:post_list')
    return render(request, 'forum/post_confirm_delete.html', {'post': post})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
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
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    
    if request.method == 'POST':
        comment.delete()
    
    return redirect('forum:post_detail', pk=comment.post.pk)