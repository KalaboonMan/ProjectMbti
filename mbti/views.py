from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from app_users.models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from diffusers import DiffusionPipeline
from io import BytesIO
import os
from django.contrib.auth import get_user_model

pipe = DiffusionPipeline.from_pretrained("Ojimi/anime-kawai-diffusion")
pipe = pipe.to("cpu")


    
def home(request):
    return render(request, 'mbti/home.html')

def about(request):
    return render(request, 'mbti/about.html')

@login_required(login_url='/users/login')
def mbti_test(request):
    if request.method == 'POST':
        gender_form = GenderForm(request.POST)
        if gender_form.is_valid():
            gender = gender_form.cleaned_data['gender']
            mbti_answers = []

            for question in Question.objects.all():
                if question.id == 25:
                    # รับคำตอบข้อ 25 เป็นรายการ
                    answers_25 = request.POST.getlist('answers_25')
                    if len(answers_25) > 2:
                        # หากเลือกเกินกำหนด ให้แสดงข้อผิดพลาด
                        context = {
                            'gender_form': gender_form,
                            'questions': Question.objects.prefetch_related('answer_set').all(),
                            'error_message_25': 'กรุณาเลือกคำตอบไม่เกิน 2 ข้อสำหรับคำถามที่ 25',
                        }
                        return render(request, 'mbti/mbti_test.html', context)
                    # รวมคำตอบข้อ 25 เข้ากับคำตอบอื่นๆ
                    mbti_answers.extend(answers_25)
                else:
                    # รับคำตอบคำถามอื่นๆ
                    answer_code = request.POST.get(f'question_{question.id}')
                    if answer_code:
                        mbti_answers.append(answer_code)
            
            # บันทึกคำตอบ
            UserAnswer.objects.update_or_create(
                user=request.user,
                defaults={'gender': gender, 'answers': ','.join(mbti_answers)}
            )
            return redirect('mbti_result')

    else:
        # คำถามและฟอร์มเพศสำหรับ GET request
        gender_form = GenderForm()
        questions = Question.objects.prefetch_related('answer_set').all()

    return render(request, 'mbti/mbti_test.html', {
        'gender_form': gender_form,
        'questions': questions
    })
    
    

@login_required(login_url='/users/login')
def mbti_result(request):
    try:
        user_answers = UserAnswer.objects.filter(user=request.user).latest('id')
    except UserAnswer.DoesNotExist:
        # If no answers exist, inform the user to take the test
        return render(request, 'mbti/mbti_result.html', {
            'message': 'โปรดทำแบบทดสอบก่อน'
        })
    gender = user_answers.gender
    all_answers = user_answers.answers.split(',')
    Point,MBTI, description = calculate(all_answers,gender)
    if request.method == 'POST' :
        
      
        prompt_2 = request.POST.get('career')
        prompt_3 = request.POST.get('hair')
        prompt_4 = request.POST.get('skin')
        prompt = gender +","+prompt_2+","+prompt_3+","+prompt_4+","+'career'+","+'solo'+","+'cute'+","+'full body'
        
       

        image = pipe(prompt, negative_prompt="lowres, bad anatomy, inappropriate content, explicit, suggestive").images[0]
        img_io = BytesIO()
        image.save(img_io, format='JPEG')
        image_filename = f'{request.user.username}.jpg'

        image_path = os.path.join('media/ai_image', image_filename)
        image.save(image_path)

        user_answers.image_path = image_path
        user_answers.save()
        return redirect('mbti_result')
    # ตั้งค่าจุดเริ่มต้นสำหรับการคำนวณคะแนน

    full_url = request.build_absolute_uri()
    user = request.user
    full_url = full_url.split('mbti_result')[0] +'share_result/'+ str(user.id)
    context = {
        "Point": Point,
        "MBTI": MBTI,
        'description': description,
        'full_url': full_url,
    }

    return render(request, 'mbti/mbti_result.html', context)
def share_result(request,id):
    User = get_user_model()
    user = User.objects.get(pk = id)
    user = UserAnswer.objects.filter(user=user).latest('id')
    gender = user.gender
    all_answers = user.answers.split(',')
    Point,MBTI,description = calculate(all_answers,gender)
    full_url = request.build_absolute_uri()
    context = {
        'description': description,
        'full_url': full_url,
        'user' : user.user.username,
        "Point": Point,
        "MBTI": MBTI,
    }
    return render(request, 'mbti/share_result.html', context)




def calculate(answer,gender):
    Point = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}

    # วนลูปผ่านคำตอบทั้งหมดเพื่อคำนวณคะแนน
    for answer_code in answer:
        answer = Answer.objects.get(code=answer_code)
        codepoints = CodePoint.objects.filter(code=answer)

        for codepoint in codepoints:
            dimension = codepoint.dimension
            Point[dimension.letter] += codepoint.point

    # สร้างตัวย่อ MBTI จากคะแนนที่คำนวณได้
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
    elif Point['T'] == Point['F'] and gender == "Male":
        MBTI += 'T'
    elif Point['T'] == Point['F'] and gender == "Female":
        MBTI += 'F'

    if Point['J'] > Point['P']:
        MBTI += 'J'
    elif Point['J'] < Point['P']:
        MBTI += 'P'
    else:
        MBTI += 'P'

    mbti_descriptions = {
        'INTJ': 'Your description here for INTJ...',
        'INTP': 'Your description here for INTP...',
        'ENTJ': 'Your description here for ENTJ...',
        'ENTP': 'Your description here for ENTP...',
        'INFJ': 'Your description here for INFJ...',
        'INFP': 'Your description here for INFP...',
        'ENFJ': 'Your description here for ENFJ...',
        'ENFP': 'Your description here for ENFP...',
        'ISTJ': 'Your description here for ISTJ...',
        'ISFJ': 'Your description here for ISFJ...',
        'ESTJ': 'Your description here for ESTJ...',
        'ESFJ': 'Your description here for ESFJ...',
        'ISTP': 'Your description here for ISTP...',
        'ISFP': 'Your description here for ISFP...',
        'ESTP': 'Your description here for ESTP...',
        'ESFP': 'Your description here for ESFP...',
    }

    description = mbti_descriptions.get(MBTI, 'No description available.')

    return Point, MBTI, description


    
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