from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from app_users.forms import *
from app_users.models import *
from app_users.utils.activation_token_generator import activation_token_generator
from .models import Profile

# Create your views here.


def register(request: HttpRequest):
    # POST
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Register and wait for activation
            user: User = form.save(commit=False)
            user.is_active = False
            user.save()

            # Build email body
            context = {
                "protocol": request.scheme,
                "host": request.get_host(),
                "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
                "token": activation_token_generator.make_token(user),
            }
            email_body = render_to_string(
                "app_users/activate_email.html", context=context
            )

            # Send email
            email = EmailMessage(
                to=[user.email],
                subject="Activate account หน่อยนะคะ/ครับ",
                body=email_body,
            )
            email.send()

            # Change redirect to register thank you
            return HttpResponseRedirect(reverse("register_thankyou"))
    else:
        form = RegisterForm()

    # GET
    context = {"form": form}
    return render(request, "app_users/register.html", context)


def register_thankyou(request: HttpRequest):
    return render(request, "app_users/register_thankyou.html")


def activate(request: HttpRequest, uidb64: str, token: str):
    title = "Activate account เรียบร้อย"
    content = "คุณสามารถเข้าสู่ระบบได้เลย"
    id = urlsafe_base64_decode(uidb64).decode()
    try:
        user = User.objects.get(id=id)
        if not activation_token_generator.check_token(user, token):
            raise Exception("Check token false")
        user.is_active = True
        user.save()
    except:
        print("Activate ไม่ผ่าน")
        title = "Activate account ไม่ผ่าน"
        content = "เป็นไปได้ว่าลิ้งค์ไม่ถูกต้อง หรือหมดอายุไปแล้ว"

    context = {"title": title, "content": content}
    return render(request, "app_users/activate.html", context)


@login_required
def edit_profile(request: HttpRequest):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        extended_form = ExtendedProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid() and extended_form.is_valid():
            form.save()
            extended_form.save() # บันทึกข้อมูลโปรไฟล์รวมถึงรูปภาพ
            #messages.success(request, "Your profile was successfully updated.")
            return HttpResponseRedirect(reverse("profile"))

    else:
        form = UserProfileForm(instance=user)
        extended_form = ExtendedProfileForm(instance=profile)

    is_saved = request.COOKIES.get("is_saved") == "1"
    flash_message = "บันทึกเรียบร้อย" if is_saved else None
    context = {
        "form": form,
        "extended_form": extended_form,
        "flash_message": flash_message,
        
    }
    
    response = render(request, "app_users/edit_profile.html",context)
    if is_saved:
        response.delete_cookie("is_saved")
    return response


@login_required
def profile(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # จัดการกรณีที่ไม่มีโปรไฟล์อยู่
        # คุณสามารถเปลี่ยนเส้นทางไปยังหน้าสำหรับการสร้างโปรไฟล์หรือแสดงข้อผิดพลาด
        return redirect('edit_profile')  # แทนที่ 'create_profile' ด้วยชื่อ URL จริงของคุณสำหรับการสร้างโปรไฟล์

    context = {'profile': user_profile}
    return render(request, 'app_users/profile.html', context)


@login_required
def user_profile(request):
    # ตรวจสอบว่าผู้ใช้ได้ล็อกอินแล้วหรือยัง
    if not request.user.is_authenticated:
        return redirect('login_url')  # สมมุติว่า 'login_url' เป็น URL สำหรับหน้าล็อกอิน

    # ดึงโปรไฟล์ของผู้ใช้ที่ล็อกอิน
    profile = Profile.objects.get(user=request.user)
    
    # ดึงฟอร์มโปรไฟล์ของผู้ใช้และปรับปรุงข้อมูลถ้าฟอร์มถูกส่ง
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # สมมุติว่า 'profile' เป็น URL สำหรับหน้าโปรไฟล์
    else:
        form = UserProfileForm(instance=profile)

    # ส่งโปรไฟล์และฟอร์มไปยัง template
    context = {'profile': profile, 'form': form}
    return render(request, 'app_users/profile.html', context)
