import jwt, datetime
from account.models import User
from rest_framework import exceptions
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings

from rest_framework.authentication import get_authorization_header, BaseAuthentication


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("access_token")
        if token:
            user = get_user(token)
            return (user, None)
        raise exceptions.AuthenticationFailed("unauthenticated")


class AdminAuthPermission(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        token = auth[1].decode("utf-8")
        token = request.COOKIES.get("admin_access_token")
        print(request)
        # if auth and len(auth)==2:
        if token:
            # token = auth[1].decode('utf-8')
            user = get_user(token)
            return (user, None)

        raise exceptions.AuthenticationFailed("unauthenticated")


def create_access_token(id, admin=False):
    if admin:
        secret = "admin_secret"
    else:
        secret = "access_secret"
    return jwt.encode(
        {
            "user_id": id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
        },
        secret,
        algorithm="HS256",
    )


def decode_access_token(token, admin=False):
    if admin:
        secret = "admin_secret"
    else:
        secret = "access_secret"
    try:
        payload = jwt.decode(token, secret, algorithms="HS256")

        return payload["user_id"]
    except Exception as e:
        print(e)
        raise exceptions.AuthenticationFailed("unauthenticated")


def decode_refresh_token(token, admin=False):
    if admin:
        secret = "admin_refresh"
    else:
        secret = "refresh_secret"
    try:
        payload = jwt.decode(token, secret, algorithms="HS256")

        return payload["user_id"]
    except Exception as e:
        print(e)
        raise exceptions.AuthenticationFailed("unauthenticated")


def create_refresh_token(id, admin=False):
    if admin:
        secret = "admin_refresh"
    else:
        secret = "refresh_secret"
    return jwt.encode(
        {
            "user_id": id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        },
        secret,
        algorithm="HS256",
    )


def get_user(token, is_admin=False):
    id = decode_access_token(token, is_admin)
    try:
        user = User.objects.get(pk=id)
        return user
    except:
        raise exceptions.AuthenticationFailed("unauthenticated")


def send_email(email, token, mail_type):
    if mail_type == "rest_password":
        url = "http://localhost:3001/reset/" + token
        context = {"url": url}
        template = get_template("email.html").render(context)
        msg = EmailMultiAlternatives(
            "Custom Subject",
            "test",  # This is the text context, just send None or Send a string message
            "settings.EMAIL_HOST_USER",
            [email],
        )
        msg.attach_alternative(template, "text/html")
        msg.send(fail_silently=False)
    if mail_type == "text_mail":
        send_mail(
            "test mail", "hi", "settings.EMAIL_HOST_USER", [email], fail_silently=False
        )
