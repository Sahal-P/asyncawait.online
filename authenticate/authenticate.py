import jwt, datetime
from account.models import User
from rest_framework import exceptions
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from decouple import config

from rest_framework.authentication import get_authorization_header, BaseAuthentication


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # token = request.COOKIES.get("access_token")
        auth = get_authorization_header(request).split()
        if auth and len(auth)==2:
            token = auth[1].decode(config("HEADER_ENCODED"))
            user = get_user(token)
            return (user, None)
        raise exceptions.AuthenticationFailed("unauthenticated")


def create_access_token(id):
    secret = config("ACCESS_SECRET")
    return jwt.encode(
        {
            "user_id": id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=config("ACCESS_TOKEN_TIME", cast=int)),
            "iat": datetime.datetime.utcnow(),
        },
        secret,
        algorithm=config("JWT_ALGORITHM"),
    )


def decode_access_token(token):
    secret = config("ACCESS_SECRET")
    try:
        payload = jwt.decode(token, secret, algorithms=config("JWT_ALGORITHM"))

        return payload["user_id"]
    except Exception as e:
        print(e)
        raise exceptions.AuthenticationFailed("unauthenticated")


def decode_refresh_token(token):
    secret = config("REFRESH_SECRET")
    try:
        payload = jwt.decode(token, secret, algorithms=config("JWT_ALGORITHM"))

        return payload["user_id"]
    except Exception as e:
        print(e)
        raise exceptions.AuthenticationFailed("unauthenticated")


def create_refresh_token(id):
    secret = config("REFRESH_SECRET")
    return jwt.encode(
        {
            "user_id": id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=config("REFRESH_TOKEN_TIME", cast=int)),
            "iat": datetime.datetime.utcnow(),
        },
        secret,
        algorithm=config("JWT_ALGORITHM"),
    )


def get_user(token):
    id = decode_access_token(token)
    try:
        user = User.objects.get(pk=id)
        return user
    except:
        raise exceptions.AuthenticationFailed("unauthenticated")


def send_email(email, token, mail_type):
    if mail_type == "rest_password":
        url = config("RESET_EMAIL_URL") + token
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
