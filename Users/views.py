from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

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

                # Use the existing profile ID from the user if available
                payload = {
                    'phone_number': phone_number,
                    'profile_id': user.profile_id  # Use the user's stored profile_id
                }

                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                return Response({'user': serializer.data, 'token': token, 'status': 'Login Successful'})

            except UserModel.DoesNotExist:
                # If the user doesn't exist, create a new account
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()

                    # Use the provided custom profile ID, or generate a new one
                    payload = {
                        'phone_number': phone_number,
                        'profile_id': profile_id or f"user{serializer.instance.pk}"
                    }

                    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                    return Response({'user': serializer.data, 'token': token, 'status': 'Account Has Been Created'})
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif not phone_number:
            return Response({'error': 'Phone Number field must NOT be blank'})
        elif not phone_number.isdigit():
            return Response({'error': 'Phone Number format is invalid'})
        elif len(phone_number) != 11:
            return Response({'error': 'Enter the correct format of phone number'})
        elif not otp:
            return Response({'error': 'OTP field must NOT be blank'})
        elif not otp.isdigit():
            return Response({'error': 'OTP format is invalid'})
        elif len(otp) != 5:
            return Response({'error': 'Enter the correct format of OTP'})
        else:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
            return Response({'Profile': serializer.data, 'token': token, 'status': 'Profile Updated! Please consider using the new JWT token.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            query = request.data.get('query')

            if not query:
                return Response({'error': 'Query field must not be blank'}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            if query.isdigit() and len(query) == 11:
                user = UserModel.objects.filter(phone_number=query).first()
            else:
                user = UserModel.objects.filter(profile_id=query).first()

            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)