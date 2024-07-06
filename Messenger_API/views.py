from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import jwt

class VerifyPhoneNumberView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if otp and otp.isdigit() and len(otp) == 5 and phone_number and phone_number.isdigit() and len(phone_number) == 11:
            try:
                user = User.objects.get(phone_number=phone_number)
                serializer = UserSerializer(user)
                token = jwt.encode({'phone_number': phone_number}, 'secret_key', algorithm='HS256')
                return Response({'user': serializer.data, 'token': token, 'status': 'Login Succesful'})
            except User.DoesNotExist:
                new_user = User.objects.create(phone_number=phone_number)
                serializer = UserSerializer(new_user)
                token = jwt.encode({'phone_number': phone_number}, 'secret_key', algorithm='HS256')
                return Response({'user': serializer.data, 'token': token, 'status': 'Account Has Been Created'})
        elif not phone_number:
            return Response({'error': 'Phone Number field must NOT be blank'})
        elif not phone_number.isdigit():
            return Response({'error': 'Phone Number format is invalid'})
        elif len(phone_number) < 11:
            return Response({'error': 'Phone Number MUST be eleven (11) digits'})
        elif not otp:
            return Response({'error': 'OTP field must NOT be blank'})
        elif not otp.isdigit():
            return Response({'error': 'OTP format is invalid'})
        elif len(otp) < 5:
            return Response({'error': 'OTP MUST be five (5) digits'})
        else:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
