from django.urls import include, path
from MBTI.views import *
from app_users import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register", views.register, name="register"),
    path("register/thankyou", views.register_thankyou, name="register_thankyou"),
    path("activate/<str:uidb64>/<str:token>", views.activate, name="activate"),
    path("profile", views.profile, name="profile"),
    path("edit_profile", views.edit_profile,name = "edit_profile")
]
