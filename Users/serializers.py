from rest_framework import serializers
from .models import UserModel


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