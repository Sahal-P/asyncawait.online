from django.urls import path
from . import views
from .views import (
    RegisterApiView,
    LoginApiView,
    RefreshAPIView,
    LogOutAPIView,
    ResetAPIView,
    ForgotAPIView,
    TwoFactorAPIView,
    CreateProfileApiView,
)

urlpatterns = [
    path("register", RegisterApiView.as_view(), name="register"),
    path("create-profile", CreateProfileApiView.as_view(), name="create-profile"),
    path("login", LoginApiView.as_view(), name="login"),
    path("refresh-token", RefreshAPIView.as_view()),
    path("logout", LogOutAPIView.as_view(), name="logout"),
    path("reset", ResetAPIView.as_view()),
    path("forgot", ForgotAPIView.as_view()),
    path("tf-auth", TwoFactorAPIView.as_view()),
]
