from rest_framework import serializers

from .models import MessageModel

from Users.models import UserModel



class MessageSerializer(serializers.ModelSerializer):
    sender_profile_id = serializers.CharField(source='sender.profile_id', read_only=True)
    receiver_profile_id = serializers.CharField(source='receiver.profile_id', read_only=True)
    sender = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), write_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), write_only=True)

    class Meta:
        model = MessageModel
        fields = ['sender', 'receiver', 'content', 'timestamp', 'attachment', 'sender_profile_id', 'receiver_profile_id']