from .models import Profile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app_users.models import User

# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Profile)