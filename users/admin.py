from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    ordering = []
    list_display = ("email", )
