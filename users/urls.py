from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path("", views.Users.as_view()),
    path("me/", views.Me.as_view()),
    path("change-password/", views.ChangePassword.as_view()),
    path("log-in/", views.LogIn.as_view()), # 쿠키 이용한
    path("log-out/", views.LogOut.as_view()),
    path("token-login", obtain_auth_token), # 토큰을 이용한
    path("jwt-login", views.JWTLogIn.as_view()),  # jwt를 이용한
    path("@<str:username>/", views.PublicUser.as_view()),
]