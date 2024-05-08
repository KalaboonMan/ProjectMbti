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
    Point,MBTI, description,careers = calculate(all_answers,gender)
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
        'careers': careers,
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
    Point,MBTI,description,careers = calculate(all_answers,gender)
    full_url = request.build_absolute_uri()
    context = {
        'careers': careers,
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
        'INTJ': 'เป็นตัวของตัวเอง, เป็นผู้คิดค้น, ช่างคิดวิเคราะห์ และมุ่งมั่น มีความสามารถพิเศษในการแปลงทฤษฎีให้อยู่ในรูปของแผนการปฏิบัติที่เป็นรูปธรรม ให้ความเคารพและความสำคัญในความรู้, ความสามารถ และโครงสร้างของสิ่งต่างๆ เป็นนักคิดในระยะยาว มีมาตรฐานที่สูงทั้งการกระทำของตนเองและของผู้อื่น เป็นผู้นำโดยธรรมชาติแต่จะเป็นผู้ตามได้ถ้าเชื่อใจผู้นำคนนั้นๆ',
        'INTP': 'เป็นคนมีเหตุผล, เป็นผู้คิดริเริ่ม และนักคิดอย่างสร้างสรรค์ อาจเป็นคนที่ตื่นเต้นมากๆเกี่ยวกับทฤษฎีและไอเดีย มีความสามารถสูงมากๆในการทำให้ทฤษฎีเป็นสิ่งที่เข้าใจได้ง่ายๆ ให้ความสำคัญและความเคารพต่อความรู้, ความสามารถ และความมีเหตุผล เป็นคนเงียบและสงวนท่าที ยากที่จะเข้าหา ไม่มีความสนใจในทั้งการเป็นผู้นำและผู้ตาม',
        'ENTJ': 'เป็นคนแน่วแน่และกล้าพูดกล้าทำ ต้องการเป็นผู้นำ มีความสามารถในการเข้าใจปัญหาเกี่ยวกับในองค์กรที่ยากๆและการสร้างการแก้ปัญหาที่เป็นรูปธรรม ฉลาดและมีความรู้กว้างขวาง โดยทั่วไปจะเป็นคนที่ถนัดด้านการพูดในที่สาธารณะ ให้ความสำคัญและความเคารพในความรู้และความสามารถ จะมีความอดทนน้อยถ้าต้องทนอยู่กับความไร้ประสิทธิภาพหรือความไม่เป็นระเบียบ',
        'ENTP': 'มีความคิดสร้างสรรค์ มีความคิดริเริ่มและแก้ปัญหาได้เก่ง มีสติปัญญาที่ดี มีความเก่งในหลายๆสิ่งหลายๆอย่าง ชอบการอภิปรายถึงปัญหา อาจเป็นคนที่เก่งในการเอาชนะหรือเอาเปรียบผู้อื่นทางด้านการแข่งขัน มีความตื่นเต้นเกี่ยวกับไอเดียและโปรเจ็กต์ใหม่ๆ โดยทั่วไปจะเป็นคนแน่วแน่และกล้าพูด มีความสามารถในการเข้าใจแนวคิดและประยุกต์ตรรกะเพื่อหาแนวทางการแก้ไขปัญหา',
        'INFJ': 'มีพลังอย่างเงียบๆ, เป็นผู้คิดริเริ่ม และไวต่อความรู้สึก มีแนวโน้มที่จะติดแน่นอยู่กับงานจนกว่ามันจะเสร็จ ค่อนข้างรับรู้เรื่องต่างๆเกี่ยวกับคนอื่นๆได้ง่ายและยังห่วงในสิ่งที่คนรอบข้างรู้สึก มีค่านิยมส่วนตัวซึ่งจะปฏิบัติตามอย่างเคร่งครัด ได้รับความเคารพและชื่นชมจากผู้อื่นอย่างมากในความอุตสาหะของพวกเขาที่จะทำแต่สิ่งที่ถูกต้อง ชอบเป็นตัวของตัวเองมากกว่าที่จะเป็นคนนำหรือทำตามผู้อื่น',
        'INFP': 'เป็นคนเงียบๆ, ชอบครุ่นคิด และยึดมั่นในอุดมการณ์ มีความสนใจในการให้บริการหรือทำประโยชน์แก่มนุษยชาติ มีระบบค่านิยมส่วนตัวซึ่งจะพยายามปฏิบัติตนให้สอดคล้องกับมันอยู่ตลอดเวลา มีความซื่อสัตย์อย่างมาก เป็นคนยืดหยุ่นได้ เป็นคนสบายๆเว้นแต่ว่าค่านิยมส่วนตัวจะถูกปฏิบัติในเชิงลบ โดยทั่วไปจะเป็นนักเขียนที่มีพรสวรรค์ มีความสามารถในการมองเห็นความเป็นไปได้ มีความสนใจในการเข้าใจและช่วยเหลือคนอื่นๆ',
        'ENFJ': 'เป็นที่รู้จักของผู้คนและไวต่อความรู้สึก มีทักษะเกี่ยวกับคนที่ดี สนใจไปที่โลกภายนอก มีความห่วงใยในสิ่งที่คนอื่นคิดและรู้สึก โดยทั่วไปจะไม่ชอบการอยู่คนเดียว มีประสิทธิภาพในการจัดการเกี่ยวกับปัญหาของคนและการเป็นผู้นำในการสนทนากลุ่มเป็นอย่างมาก ชอบการบริการหรือทำประโยชน์แก่ผู้อื่น และมักจะยกความต้องการของคนอื่นให้สำคัญกว่าความต้องการของตัวเอง',
        'ENFP': 'เป็นคนกระตือรือร้น, ยึดมั่นในอุดมการณ์ และมีความคิดสร้างสรรค์ สามารถทำอะไรได้แทบจะทุกสิ่งที่มันทำให้พวกเขาสนใจ มีทักษะเกี่ยวกับคนที่ดี ต้องการใช้ชีวิตให้สอดคล้องกับค่านิยมในใจ ตื่นเต้นกับไอเดียใหม่ๆแต่จะเบื่อกับรายละเอียด เป็นคนเปิดใจกว้างและมีความยืดหยุ่นสูง มีขอบเขตอย่างกว้างขวางในสิ่งที่สนใจและที่มีความสามารถ',
        'ISTJ': 'เอาจริงเอาจังและค่อนข้างเงียบ สนใจในความปลอดภัยและการใช้ชีวิตอย่างสงบสุข เป็นคนที่ละเอียด, มีความรับผิดชอบ, ไว้ใจและพึ่งพาได้ เป็นอย่างมาก มีความสามารถในการใช้สมาธิจดจ่อกับอะไรบางอย่าง โดยส่วนมากจะให้การสนับสนุนและส่งเสริมวัฒนธรรมประเพณีและสถาบันต่างๆ เป็นคนมีระเบียบและขยันอย่างมาก พวกเขาทำงานอย่างเหน็ดเหนื่อยและสม่ำเสมอเพื่อเข้าถึงเป้าหมายที่ได้กำหนดไว้แล้ว สามารถจัดการงานอะไรก็ตามให้เสร็จสรรพได้ภายในเวลาไม่นานถ้าหากได้ตั้งใจไว้แล้วว่าจะทำ',
        'ISFJ': 'เป็นคนเงียบๆ, ใจดี และมีธรรมในใจ สามารถเป็นที่พึ่งพาในการทำสิ่งต่างๆได้ โดยทั่วไปจะให้ความสำคัญกับความต้องการของผู้อื่นมากกว่าความต้องการของตนเอง เป็นคนมั่นคงและเป็นนักปฏิบัติ ให้ความสำคัญความปลอดภัยและประเพณี ภายในใจเต็มไปด้วยการเฝ้าสังเกตคนรอบตัว เป็นคนที่รับรู้ความรู้สึกของผู้อื่นได้อย่างดี ชอบการบริการหรือการทำประโยชน์ให้กับผู้อื่น',
        'ESTJ': 'เป็นนักปฏิบัติ, สนใจในจารีตประเพณี และมีระบบระเบียบ ชอบกิจกรรมที่ใช้ร่างกาย เช่น เล่นกีฬา ไม่สนใจในทฤษฎีหรือสิ่งที่เป็นนามธรรมยกเว้นจะเห็นว่ามันสามารถนำมาปฏิบัติจริงได้ มีวิสัยทัศน์ที่ชัดเจนในเรื่องสิ่งต่างๆควรจะเป็น เป็นคนซื่อสัตย์และขยัน การมีภาระไม่ใช่ปัญหาหรือเรื่องน่าเบื่อ มีความามารถเด่นในการเป็นคนจัดหรือดูแลกิจกรรม เป็น “พลเมืองดี” ที่ให้ความสำคัญในความปลอดภัยและการใช้ชีวิตอย่างสงบสุข',
        'ESFJ': 'เป็นคนใจดี, อบอุ่น, เป็นที่รู้จัก และมีธรรมในใจ มีแนวโน้มที่จะให้ความสำคัญกับความต้องการของผู้อื่นมากกว่าความต้องการของตัวเอง มีความรับผิดชอบสูงต่องานและหน้าที่ ให้ความสำคัญกับประเพณีและความปลอดภัย สนใจในการบริการหรือการทำประโยชน์ให้กับผู้อื่น ต้องการเสริมแรงทางบวก (Positive Reinforcement) เพื่อให้ตนเองรู้สึกดี',
        'ISTP': 'เป็นคนเงียบๆและสงวนท่าที สนใจในคำถามเกี่ยวกับการทำงานของสิ่งต่างๆว่า “อย่างไร” และ “ทำไม” มีความสามารถเกี่ยวกับเครื่องจักรกล เป็นพวกชอบการเสี่ยงที่อาศัยอยู่ในโลกของปัจจุบัน โดยส่วนมากจะสนใจและมีพรสวรรค์ในกีฬาประเภทเอ็กซ์ตรีม อาจไม่เคารพในกฎระเบียบถ้ามันช่วยให้เขาทำอะไรสักอย่างสำเร็จ อยู่อย่างสันโดษและเป็นนักคิดวิเคราะห์ เก่งในด้านการหาวิธีในการแก้ปัญหาเป็นอย่างมาก',
        'ISFP': 'เป็นคนเงียบๆ, เอาจริงเอาจัง, อ่อนไหวต่อความรู้สึกของผู้อื่น และใจดี ไม่ชอบความขัดแย้งและการทำสิ่งต่างๆซึ่งอาจนำพาไปสู่ความขัดแย้ง เป็นคนซื่อสัตย์และเชื่อถือได้ มีความสามารถในการประเมินหรือเห็นค่าในสุนทรียภาพที่ดีทางด้านความงามหรือศิลปะ ไม่ชอบการเป็นผู้นำหรือการควบคุมผู้อื่น ยืดหยุ่นได้และเปิดใจกว้าง มักจะเป็นคนที่มีความคิดสร้างสรรค์และเป็นผู้ริเริ่ม ชอบอยู่กับปัจจุบัน',
        'ESTP': 'เป็นมิตร, ยืดหยุ่นได้ และมุ่งเน้นไปยังการปฏิบัติ ชอบทำอะไรที่ให้ความบันเทิง เป็นนักปฏิบัติที่สนใจผลลัพธ์ในปัจจุบัน ใช้ชีวิตโดยมองไปที่วันนี้เป็นหลัก เป็นพวกที่ชอบการเสี่ยงซึ่งชื่นชอบการใช้ชีวิตอย่างเร่งรีบ ไม่มีความอดทนต่อคำอธิบายยาวๆ อาจไม่เคารพในกฎระเบียบถ้ามันช่วยให้เขาทำอะไรสักอย่างสำเร็จ มีทักษะที่ดีในเรื่องเกี่ยวกับคน',
        'ESFP': 'มุ่งเน้นไปยังคนอื่นๆ เป็นคนรักสนุก ทำสิ่งต่างๆให้เป็นเรื่องที่สนุกมากขึ้นสำหรับคนอื่นๆโดยใช้ความสนุกสนานของตนเอง ชอบอยู่กับปัจจุบัน ชอบประสบการณ์การได้ทำอะไรใหม่ๆ ไม่ชอบทฤษฎีและบทวิเคราะห์ที่ไม่น่าสนใจหรือไม่เกี่ยวกับคน ชอบการบริการหรือทำประโยชน์แก่ผู้อื่น ชอบการเป็นจุดสนใจในสถานการณ์ทางสังคมต่างๆ มีสามัญสำนึกที่ดี',
    }
    
    mbti_careers = {
        'INTJ': 'เดี๋ยวบอก',
        'INTP': 'Your description here for INTP...',
        'ENTJ': 'Your description here for ENTJ...',
        'ENTP': 'Your description here for ENTP...',
        'INFJ': 'Your description here for INFJ...',
        'INFP': 'Your description here for INFP...',
        'ENFJ': 'Your description here for ENFJ...',
        'ENFP': 'Your description here for ENFP...',
        'ISTJ': 'Your description here for ISTJ...',
        'ISFJ': 'เดี๋ยวบอก',
        'ESTJ': 'Your description here for ESTJ...',
        'ESFJ': 'Your description here for ESFJ...',
        'ISTP': 'Your description here for ISTP...',
        'ISFP': 'Your description here for ISFP...',
        'ESTP': 'Your description here for ESTP...',
        'ESFP': 'Your description here for ESFP...',
    }

    description = mbti_descriptions.get(MBTI, 'No description available.')
    careers = mbti_careers.get(MBTI, 'No careers listed.')

    return Point, MBTI, description, careers


    
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