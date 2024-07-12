from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import UserModel, MessageModel
from .serializers import UserSerializer, MessageSerializer
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
                payload = {'phone_number': phone_number,
                           'profile_id': profile_id or f"user{user.pk}"}
                token = jwt.encode(
                    payload, settings.SECRET_KEY, algorithm='HS256')
                return Response({'user': serializer.data, 'token': token, 'status': 'Login Successful'})
            except UserModel.DoesNotExist:
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    payload = {'phone_number': phone_number,
                               'profile_id': profile_id or f"user{serializer.instance.pk}"}
                    token = jwt.encode(
                        payload, settings.SECRET_KEY, algorithm='HS256')
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

            return Response({'Profile': serializer.data, 'token': token, 'status': 'Profile Updated! Please Consider Using The New JWT Token.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, profile_id):
        try:
            user = request.user
            other_user = get_object_or_404(UserModel, profile_id=profile_id)

            if user == other_user:
                return Response({'error': 'Attention: You are messaging yourself'}, status=status.HTTP_400_BAD_REQUEST)

            messages = MessageModel.objects.filter(
                (Q(sender=user) & Q(receiver=other_user)) |
                (Q(sender=other_user) & Q(receiver=user))
            ).order_by('timestamp')

            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, profile_id):
        try:
            user = request.user
            receiver = get_object_or_404(UserModel, profile_id=profile_id)

            if user == receiver:
                return Response({'error': 'Attention: You are messaging yourself'}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'sender': user.id,
                'receiver': receiver.id,
                'content': request.data.get('content')
            }
            serializer = MessageSerializer(data=data)
            if serializer.is_valid():
                message = serializer.save()
                response_data = serializer.data
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UserModel.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
