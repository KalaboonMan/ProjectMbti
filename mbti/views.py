from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
import re

def home(request):
    return render(request, 'mbti/home.html')

@login_required(login_url='/users/login')
def mbti_test(request):
    Question_Answers = []
    Question_all = Question.objects.all()
    for Q in Question_all:
        A = Answer.objects.filter(question=Q)
        Question_Answers.append({
            "Question" : Q,
            "Answer" : A
        })
    context = {
        "Question" : Question_Answers,
    }
    return render(request, 'mbti/mbti_test.html', context)

@login_required(login_url='/users/login')
def mbti_result(request):
    gender = "Male"
    text = "1A,2B,3A,4B,5A,7A,8B,9A,10A,11A,12B,13B,14A,15B,16A,17A,18B,19A,20A,21B,22A,23B,24A,25A,25C,26B,27A,28B,29A,30A,31B,32A,33B,34A,35A,36B,37A,38B,39A,40B,41A,42B,43B,44B,45A,46A,47B,48B,49A,50B"
    all_answer = text.split(',')
    Point = {'E' : 0, 'I' : 0, 'S' : 0, 'N' : 0, 'T' : 0, 'F' : 0, 'J' : 0, 'P' : 0}
    for a in all_answer:
        answer = Answer.objects.get(code=a)
        codepoint = CodePoint.objects.get(code=answer)
        dimension = codepoint.dimension
        Point[dimension.letter] += codepoint.point
    MBTI = ""
    if Point['E'] > Point['I']:
        MBTI += 'E'
    elif Point['E'] < Point['I']:
        MBTI += 'I'
    else:
        MBTI += 'I'
    
    if Point['S'] > Point['N']:
        MBTI += 'S'
    elif Point['S'] < Point['N']:
        MBTI += 'N'
    else:
        MBTI += 'N'

    if Point['T'] > Point['F']:
        MBTI += 'T'
    elif Point['T'] < Point['F']:
        MBTI += 'F'
    elif Point['T'] > Point['F'] and gender == "Male":
        MBTI += 'T'
    elif Point['T'] > Point['F'] and gender == "Female":
        MBTI += 'F'

    if Point['J'] > Point['P']:
        MBTI += 'J'
    elif Point['J'] < Point['P']:
        MBTI += 'P'
    else:
        MBTI += 'P'

    context = {
        "Point" : Point,
        "MBTI" : MBTI
    }
    return render(request, 'mbti/mbti_result.html',context)




















    
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