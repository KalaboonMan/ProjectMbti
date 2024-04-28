from django import forms
from .models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text']
        
class GenderForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['gender']
        



