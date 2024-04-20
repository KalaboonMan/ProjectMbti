from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *

def home(request):
    return render(request, 'mbti/home.html')

    
def article(request):
    posts = Post.objects.all().order_by('-created_at')  # โพสต์ล่าสุดก่อน
    return render(request, 'mbti/article.html', {'posts': posts})

@login_required
def article_writing(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return redirect('/article')
    else:
        form = PostForm()
    return render(request, 'mbti/article_writing.html', {'form': form})

@login_required
def article_history(request):
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'mbti/article_history.html', {'posts': user_posts})

def search_posts(request):
    query = request.GET.get('query', '')
    if query:
        posts = Post.objects.filter(text__icontains=query)
    else:
        posts = Post.objects.none()
    
    return render(request, 'mbti/article.html', {'posts': posts})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, user=request.user)
    post.delete()
    return redirect('article_history')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('article_history')
    else:
        form = PostForm(instance=post)
    return render(request, 'mbti/edit_post.html', {'form': form})





