from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user', 'KOALM_number')


class MemberProfileSerializer(serializers.ModelSerializer):
    """Serializer for member profile updates (excludes sensitive fields)"""
    class Meta:
        model = Member
        fields = ['name', 'email', 'address', 'communication_address', 
                  'district', 'pincode', 'state', 'district_club_name', 'photo', 'KOALM_number']
        read_only_fields = ['KOALM_number']


class PublicMemberSerializer(serializers.ModelSerializer):
    """Serializer for public member profile (limited fields for QR/badge)"""
    class Meta:
        model = Member
        fields = ['name', 'KOALM_number', 'photo', 'district', 'district_club_name']

