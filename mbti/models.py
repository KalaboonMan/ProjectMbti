from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
# Create your models here.
 
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    