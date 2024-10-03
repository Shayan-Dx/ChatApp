import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

from .models import UserModel


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return None
        try:
            token = authorization_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], verify_signature=False)
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()

        profile_id = payload.get('profile_id')
        user = UserModel.objects.filter(profile_id=profile_id).first()

        if user:
            user.is_authenticated = True
            return user, payload
        else:
            raise AuthenticationFailed('User not found')

    def authenticate_header(self, request):
        return 'Bearer'
    
    def decode_jwt(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
        
def get_user_from_payload(payload):
    from Users.models import UserModel
    profile_id = payload.get('profile_id')  # Using profile_id in the token payload
    if not profile_id:
        raise AuthenticationFailed('Token payload does not contain a profile_id.')

    try:
        user = UserModel.objects.get(profile_id=profile_id)
    except UserModel.DoesNotExist:
        raise AuthenticationFailed('User not found for given token payload.')

    return user