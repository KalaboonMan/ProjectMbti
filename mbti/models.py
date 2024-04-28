from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
# Create your models here.
 
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    text = models.TextField()

    def __str__(self):
        return self.text

class Dimension(models.Model):
    letter = models.CharField(max_length=1)
    name = models.CharField(max_length=100)
    detail_en = models.TextField()
    detail_th = models.TextField()

    def __str__(self):
        return self.name


class CodePoint(models.Model):
    code = models.ForeignKey(Answer, on_delete=models.CASCADE)
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    point = models.IntegerField()

    def __str__(self):
        return f'{self.code} - {self.point}'

class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=(('Male', 'ชาย'), ('Female', 'หญิง')))
    answers = models.TextField()
    

    def __str__(self):
        return f'{self.user.get_username()} gender: {self.gender} answers: {self.answers}'

