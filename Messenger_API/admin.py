from django.contrib import admin
from .models import MessageModel

    
@admin.register(MessageModel)
class MessageAdminView(admin.ModelAdmin):
    list_display = ["sender", "receiver", "content", "timestamp"]