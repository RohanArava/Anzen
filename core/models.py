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
