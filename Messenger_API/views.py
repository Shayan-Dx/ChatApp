from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

from django.db.models import Q

from .models import MessageModel
from .serializers import MessageSerializer

from Users.models import UserModel
from Users.authentication import JWTAuthentication


class MessagePagination(PageNumberPagination):
    page_size = 20  # Number of messages per page
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = MessagePagination

    def get(self, request, profile_id):
        try:
            user = request.user
            other_user = UserModel.objects.get(profile_id=profile_id)
            query = request.query_params.get('query', None)
            order = request.query_params.get('order', 'timestamp')

            # Fetch all messages between the sender and the receiver
            messages = MessageModel.objects.filter(
                (Q(sender=user) & Q(receiver=other_user)) | (Q(sender=other_user) & Q(receiver=user))
            ).order_by(order)

            # Apply search filter if a query is provided
            if query:
                messages = messages.filter(content__icontains=query)

            # Apply pagination
            paginator = MessagePagination()
            paginated_messages = paginator.paginate_queryset(messages, request)
            serializer = MessageSerializer(paginated_messages, many=True)

            return paginator.get_paginated_response(serializer.data)

        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, profile_id):
        try:
            user = request.user
            receiver = UserModel.objects.get(profile_id=profile_id)

            if user == receiver:
                return Response({'error': 'You cannot message yourself'}, status=status.HTTP_400_BAD_REQUEST)

            data = request.data.copy()
            data['sender'] = user.id
            data['receiver'] = receiver.id

            serializer = MessageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
