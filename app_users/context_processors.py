
def user_display_name(request):
    if not request.user.is_authenticated:
        return {'user_display_name': None}

    # เข้าถึงโปรไฟล์และตรวจสอบว่ามีชื่อและนามสกุลหรือไม่
    try:
        profile = request.user.profile
        if profile.first_name and profile.last_name:
            return {'user_display_name': f"{profile.first_name} {profile.last_name}"}
        else:
            return {'user_display_name': request.user.username}
    except:
        return {'user_display_name': request.user.username}
