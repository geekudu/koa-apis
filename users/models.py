from django.db import models
from django.contrib.auth.models import User
import random
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    KOALM_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    communication_address = models.TextField(null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district_club_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    photo = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'members'


class OTP(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otps'
        ordering = ['-created_at']

    @classmethod
    def generate_otp(cls, member):
        """Generate a new 6-digit OTP for a member"""
        # Invalidate previous unused OTPs
        cls.objects.filter(member=member, is_used=False).update(is_used=True)
        
        # Generate new OTP
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        otp = cls.objects.create(
            member=member,
            code=code,
            expires_at=expires_at
        )
        return otp

    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and timezone.now() < self.expires_at