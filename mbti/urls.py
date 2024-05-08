from django.urls import path
from MBTI.views import *
from MBTI import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', home ,name = 'home'),
    path('mbti_test/', mbti_test ,name = 'mbti_test'),
    path('mbti_result/', mbti_result ,name = 'mbti_result'),
    path('share_result/<int:id>', share_result ,name = 'share_result'),
    
    
    path('article/', article ,name = 'article'),
    path('article_writing/', article_writing ,name = 'article_writing'),
    path('article_history/', article_history ,name = 'article_history'),
    path('search/', search_posts, name='search_posts'),
    
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    
    path('about/', about ,name = 'about'),
    path('<str:mbti_type>/', views.mbti_detail, name='mbti_detail'),

 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)