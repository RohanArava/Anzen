import base64

from django.contrib import admin

from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_salt')

    def display_salt(self, obj):
        return base64.b64encode(obj.encryption_salt).decode()

    display_salt.short_description = "Encryption Salt (base64)"
