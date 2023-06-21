from django.urls import path
from . import views
from .views import (
    RegisterApiView,
    LoginApiView,
    UserAPIView,
    RefreshAPIView,
    LogOutAPIView,
    ResetAPIView,
    ForgotAPIView,
    AdminLgoinAPIView,
    AdminLogOutAPIView,
    TwoFactorAPIView,
    LoginWithPhoneAPIView,
    AdminLoginApiView,
    UsersAPIView,
)

urlpatterns = [
    path("register", RegisterApiView.as_view()),
    path("login", LoginApiView.as_view()),
    path("admin-login", AdminLoginApiView.as_view()),
    path("get-user", UserAPIView.as_view()),
    path("get-users", UsersAPIView.as_view()),
    path("refresh-token", RefreshAPIView.as_view()),
    path("logout", LogOutAPIView.as_view()),
    path("reset", ResetAPIView.as_view()),
    path("forgot", ForgotAPIView.as_view()),
    path("admin", AdminLgoinAPIView.as_view()),
    path("admin-logout", AdminLogOutAPIView.as_view()),
    path("tf-auth", TwoFactorAPIView.as_view()),
    path("login-phone", LoginWithPhoneAPIView.as_view()),
]
