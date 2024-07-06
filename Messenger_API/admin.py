from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdminView(admin.ModelAdmin):
    list_display = ["phone_number"]
    search_fields = ["phone_number"]