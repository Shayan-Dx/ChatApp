from django.contrib import admin
from .models import UserModel, MessageModel


@admin.register(UserModel)
class UserAdminView(admin.ModelAdmin):
    list_display = ["pk", "phone_number", "profile_id", "first_name", "last_name", "profile_picture"]
    search_fields = ["phone_number", "profile_id"]
    
@admin.register(MessageModel)
class MessageAdminView(admin.ModelAdmin):
    list_display = ["sender", "receiver", "content", "timestamp"]