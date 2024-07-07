import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

from .models import UserModel


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return None
        try:
            # header = 'Token xxxxxxxxxxxxxxxxxxxxxxxx'
            token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()

        # Get the user from the database
        username_or_phone_number = payload.get('phone_number')
        user = UserModel.objects.filter(phone_number=username_or_phone_number).first()

        if user:
            # You can set a custom attribute to indicate authentication status
            user.is_authenticated = True
            return user, payload
        else:
            raise AuthenticationFailed('User not found')

    def authenticate_header(self, request):
        return 'Bearer'