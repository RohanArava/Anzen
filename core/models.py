from django.db import models
from django.contrib.auth.models import User
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encryption_salt = models.BinaryField()

    def __str__(self):
        return f"Profile for {self.user.username}"

    @staticmethod
    def generate_salt(length=16):
        return os.urandom(length)


class TOTPEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='totp_entries')
    account_name = models.CharField(max_length=100)  # e.g., alice@example.com
    issuer = models.CharField(max_length=100, blank=True)  # e.g., Google, GitHub
    encrypted_secret = models.BinaryField()
    digits = models.PositiveSmallIntegerField(default=6)  # usually 6 or 8
    period = models.PositiveSmallIntegerField(default=30)  # default 30s
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issuer or 'Unknown'} ({self.account_name})"
