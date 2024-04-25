from django.urls import path
from MBTI.views import *
from MBTI import views


urlpatterns = [
    path('', home ,name = 'home'),
    path('mbti_test/', mbti_test ,name = 'mbti_test'),
    path('mbti_result/', mbti_result ,name = 'mbti_result'),
    
    
    path('article/', article ,name = 'article'),
    path('article_writing/', article_writing ,name = 'article_writing'),
    path('article_history/', article_history ,name = 'article_history'),
    path('search/', search_posts, name='search_posts'),
    
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),

 
]
