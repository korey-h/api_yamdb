from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser',
                                    'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),

    )


admin.site.register(User, MyUserAdmin)
