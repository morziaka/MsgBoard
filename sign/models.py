from django.contrib.auth.models import User
from django.db import models

class OneTimeCode(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
