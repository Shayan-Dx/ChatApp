import jwt
from rest_framework import serializers
from .models import UserModel, MessageModel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['phone_number', 'profile_id', 'first_name', 'last_name', 'profile_picture']

    def create(self, validated_data):
        instance = super().create(validated_data)
        if 'profile_id' in validated_data:
            instance.profile_id = validated_data['profile_id']
        else:
            instance.profile_id = f"user{instance.pk}"
        instance.save()
        return instance
    
class MessageSerializer(serializers.ModelSerializer):
    sender_profile_id = serializers.CharField(source='sender.profile_id', read_only=True)
    receiver_profile_id = serializers.CharField(source='receiver.profile_id', read_only=True)
    sender = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), write_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), write_only=True)

    class Meta:
        model = MessageModel
        fields = ['sender', 'receiver', 'content', 'timestamp', 'attachment', 'sender_profile_id', 'receiver_profile_id']