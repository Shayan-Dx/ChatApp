from django.contrib import admin
from .models import UserModel


@admin.register(UserModel)
class UserAdminView(admin.ModelAdmin):
    list_display = ["pk", "phone_number", "profile_id", "first_name", "last_name", "profile_picture"]
    search_fields = ["phone_number", "profile_id"]