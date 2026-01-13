from django.db import models
from django.contrib.auth.models import User
import random
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # Basic Information
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    photo = models.TextField(null=True, blank=True)
    
    # Membership Numbers
    KOALM_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    IOA_LM_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Professional Information
    working_hospital_name = models.CharField(max_length=200, null=True, blank=True)
    working_hospital_district = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    tcmc_reg_no = models.CharField(max_length=100, null=True, blank=True)
    ima_life_membership_status = models.CharField(max_length=10, null=True, blank=True)  # Yes or No
    
    # Education
    mbbs_college = models.CharField(max_length=200, null=True, blank=True)
    mbbs_year = models.CharField(max_length=10, null=True, blank=True)
    pg_diploma_college = models.CharField(max_length=200, null=True, blank=True)
    pg_diploma_year = models.CharField(max_length=10, null=True, blank=True)
    pg_degree_college = models.CharField(max_length=200, null=True, blank=True)
    pg_degree_year = models.CharField(max_length=10, null=True, blank=True)
    awards_honours = models.TextField(null=True, blank=True)
    
    # Contact Information
    mobile_number = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=100, null=True, blank=True)
    landline_hospital = models.CharField(max_length=100, null=True, blank=True)
    landline_residence = models.CharField(max_length=100, null=True, blank=True)
    
    # Address Information
    communication_address = models.TextField(null=True, blank=True)  # House Name / No
    address1_place_post = models.TextField(null=True, blank=True)  # Place & Post office
    district = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district_club_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)  # Keep for backward compatibility
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)  # Date field
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    spouse_name = models.CharField(max_length=100, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

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