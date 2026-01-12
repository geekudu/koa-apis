from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'KOALM_number', 'district', 'state', 'created_at')
    list_filter = ('district', 'state', 'created_at')
    search_fields = ('name', 'email', 'KOALM_number')
    readonly_fields = ('created_at', 'updated_at')
