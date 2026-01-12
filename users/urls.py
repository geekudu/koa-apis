from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MemberViewSet, login_view, logout_view, check_auth_view,
    member_request_otp, member_verify_otp, member_profile,
    member_update_profile, member_logout, public_member_profile,
    download_badge
)

router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')

urlpatterns = [
    path('api/', include(router.urls)),
    # Admin portal endpoints
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/check/', check_auth_view, name='check-auth'),
    # Member portal endpoints
    path('api/member/request-otp/', member_request_otp, name='member-request-otp'),
    path('api/member/verify-otp/', member_verify_otp, name='member-verify-otp'),
    path('api/member/profile/', member_profile, name='member-profile'),
    path('api/member/profile/update/', member_update_profile, name='member-update-profile'),
    path('api/member/logout/', member_logout, name='member-logout'),
    path('api/member/badge/download/', download_badge, name='download-badge'),
    # Public member profile (for QR code/badge)
    path('api/public/member/<str:koalm_number>/', public_member_profile, name='public-member-profile'),
]

