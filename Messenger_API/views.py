from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.conf import settings

from .models import UserModel
from .serializers import UserSerializer
from .authentication import JWTAuthentication

import jwt

class VerifyPhoneNumberView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        profile_id = request.data.get('profile_id')

        if otp and otp.isdigit() and len(otp) == 5 and phone_number and phone_number.isdigit() and len(phone_number) == 11:
            try:
                user = UserModel.objects.get(phone_number=phone_number)
                serializer = UserSerializer(user)
                payload = {'phone_number': phone_number, 'profile_id': profile_id or f"user{user.pk}"}
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                return Response({'user': serializer.data, 'token': token, 'status': 'Login Successful'})
            except UserModel.DoesNotExist:
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    payload = {'phone_number': phone_number, 'profile_id': profile_id or f"user{serializer.instance.pk}"}
                    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                    return Response({'user': serializer.data, 'token': token, 'status': 'Account Has Been Created'})
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif not phone_number:
            return Response({'error': 'Phone Number field must NOT be blank'})
        elif not phone_number.isdigit():
            return Response({'error': 'Phone Number format is invalid'})
        elif len(phone_number) < 11 or len(phone_number) > 11:
            return Response({'error': 'Enter the correct format of phone number'})
        elif not otp:
            return Response({'error': 'OTP field must NOT be blank'})
        elif not otp.isdigit():
            return Response({'error': 'OTP format is invalid'})
        elif len(otp) < 5 or len(otp) > 5:
            return Response({'error': 'Enter the correct format of otp'})
        else:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({'Profile': serializer.data})

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            phone_number = user.phone_number
            profile_id = user.profile_id
            payload = {'phone_number': phone_number, 'profile_id': profile_id}
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({'Profile': serializer.data, 'token': token, 'status': 'Profile Updated! Please Consider Using The New JWT Token.)'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)