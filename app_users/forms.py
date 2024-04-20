from django import forms
from django.contrib.auth.forms import UserCreationForm

from app_users.models import User, Profile


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name",)
        
        

class ExtendedProfileForm(forms.ModelForm):
    prefix = "extended"

    class Meta:
        model = Profile
        fields = ("first_name", "last_name","address", "phone","profile_picture",)
        labels = {
            "address": "ที่อยู่",
            "phone": "เบอร์โทรศัพท์",
        }
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}