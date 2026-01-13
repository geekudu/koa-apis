from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')


class MemberProfileSerializer(serializers.ModelSerializer):
    """Serializer for member profile updates (excludes sensitive fields)"""
    class Meta:
        model = Member
        fields = [
            'name', 'email', 'photo', 'KOALM_number', 'IOA_LM_number',
            'working_hospital_name', 'working_hospital_district', 'designation',
            'communication_address', 'address1_place_post', 'district', 'pincode', 
            'state', 'district_club_name', 'mobile_number', 'whatsapp_number',
            'landline_hospital', 'landline_residence', 'date_of_birth', 
            'registration_date', 'blood_group', 'tcmc_reg_no', 
            'ima_life_membership_status', 'mbbs_college', 'mbbs_year',
            'pg_diploma_college', 'pg_diploma_year', 'pg_degree_college', 
            'pg_degree_year', 'awards_honours', 'spouse_name'
        ]
        read_only_fields = ['KOALM_number']


class PublicMemberSerializer(serializers.ModelSerializer):
    """Serializer for public member profile (limited fields for QR/badge)"""
    class Meta:
        model = Member
        fields = [
            'name', 'KOALM_number', 'photo', 'date_of_birth', 'email',
            'mobile_number', 'IOA_LM_number', 'district_club_name',
            'working_hospital_name', 'blood_group'
        ]

