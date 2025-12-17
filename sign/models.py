from datetime import datetime
from django.contrib.auth.models import User


from django.db import models
from django.utils import timezone

User._meta.get_field('email')._unique = True

class OneTimeCode(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = timezone.timedelta(minutes=5)  # OTP valid for 5 minutes
        return timezone.now() > (self.created_at + expiration_time)


