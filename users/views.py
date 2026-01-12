from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import HttpResponse
import os
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import white
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw
import qrcode
from .models import Member, OTP
from .serializers import MemberSerializer, MemberProfileSerializer, PublicMemberSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint for Django superuser authentication.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if user.is_superuser:
            login(request, user)
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_superuser': user.is_superuser
                }
            })
        else:
            return Response(
                {'error': 'Only superusers can access the admin portal'},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint.
    """
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([AllowAny])
def check_auth_view(request):
    """
    Check if user is authenticated.
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'is_superuser': request.user.is_superuser
            }
        })
    else:
        return Response({
            'authenticated': False
        })


class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing members with CRUD operations.
    Requires authentication.
    """
    queryset = Member.objects.all().order_by('-created_at')
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Member.objects.all().order_by('-created_at')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(KOALM_number__icontains=search) |
                Q(district__icontains=search) |
                Q(state__icontains=search) |
                Q(district_club_name__icontains=search)
            )
        return queryset


# Member Portal Endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def member_request_otp(request):
    """
    Generate and send OTP to member's email using KOALM_number.
    """
    koalm_number = request.data.get('KOALM_number')
    
    if not koalm_number:
        return Response(
            {'error': 'KOALM_number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        member = Member.objects.get(KOALM_number=koalm_number)
    except Member.DoesNotExist:
        return Response(
            {'error': 'Member not found with this KOALM number'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not member.email:
        return Response(
            {'error': 'Email not found for this member'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate OTP
    otp = OTP.generate_otp(member)
    
    # Send OTP via email
    try:
        email = EmailMessage(
            subject='KERALA ORTHOPAEDIC ASSOCIATION - Login OTP',
            body=f'Your login OTP is: {otp.code}\n\nThis OTP is valid for 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[member.email],
        )
        email.send(fail_silently=False)
    except Exception as e:
        return Response(
            {'error': f'Failed to send email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'success': True,
        'message': 'OTP sent to your email address'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def member_verify_otp(request):
    """
    Verify OTP and login member.
    """
    koalm_number = request.data.get('KOALM_number')
    otp_code = request.data.get('otp')
    
    if not koalm_number or not otp_code:
        return Response(
            {'error': 'KOALM_number and OTP are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        member = Member.objects.get(KOALM_number=koalm_number)
    except Member.DoesNotExist:
        return Response(
            {'error': 'Member not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get the latest unused OTP
    try:
        otp = OTP.objects.filter(member=member, code=otp_code, is_used=False).latest('created_at')
    except OTP.DoesNotExist:
        return Response(
            {'error': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify OTP
    if not otp.is_valid():
        return Response(
            {'error': 'OTP has expired or already used'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mark OTP as used
    otp.is_used = True
    otp.save()
    
    # Create or get user for member
    if not member.user:
        # Create a user account for the member
        username = f"member_{member.KOALM_number}"
        password = get_random_string(20)  # Generate a random 20-character password
        user = User.objects.create_user(
            username=username,
            email=member.email,
            password=password
        )
        member.user = user
        member.save()
    else:
        user = member.user
    
    # Login the user
    login(request, user)
    
    # Return member data
    serializer = MemberProfileSerializer(member)
    return Response({
        'success': True,
        'member': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_profile(request):
    """
    Get member's own profile.
    """
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        return Response(
            {'error': 'Member profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MemberProfileSerializer(member)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def member_update_profile(request):
    """
    Update member's own profile.
    """
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        return Response(
            {'error': 'Member profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MemberProfileSerializer(member, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'member': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def member_logout(request):
    """
    Logout member.
    """
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([AllowAny])
def public_member_profile(request, koalm_number):
    """
    Get public member profile by KOALM number (for QR code/badge access).
    No authentication required.
    """
    try:
        member = Member.objects.get(KOALM_number=koalm_number)
    except Member.DoesNotExist:
        return Response(
            {'error': 'Member not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = PublicMemberSerializer(member)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_badge(request):
    """
    Generate and download member badge PDF with photo, name, KOALM number, and QR code.
    """
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        return Response(
            {'error': 'Member profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get the PDF template path
    template_path = '/home/arun/koa-apis/koa.pdf'
    
    if not os.path.exists(template_path):
        return Response(
            {'error': 'Badge template not found'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Generate public profile URL
    public_url = f"https://koamember.vercel.app/public/{member.KOALM_number}/"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to bytes
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Read the template PDF
    template_pdf = PdfReader(open(template_path, 'rb'))
    template_page = template_pdf.pages[0]
    
    # Get page dimensions
    page_width = float(template_page.mediabox.width)
    page_height = float(template_page.mediabox.height)
    
    # Create overlay PDF with reportlab
    overlay_buffer = io.BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
    
    # Draw member photo if available (positioned in bottom-left box)
    # Adjust these coordinates based on your template: x, y, width, height
    photo_x = 20
    photo_y = page_height - 330  # Adjust based on template
    photo_width = 120
    photo_height = 130
    
    if member.photo:
        try:
            # Decode base64 photo
            photo_data = base64.b64decode(member.photo.split(',')[-1] if ',' in member.photo else member.photo)
            photo_img = Image.open(io.BytesIO(photo_data))
            
            # Border settings
            border_width = 5  # White border width in pixels
            border_radius = 10  # Border radius in pixels
            
            # Calculate inner dimensions (accounting for border)
            inner_width = photo_width - (border_width * 2)
            inner_height = photo_height - (border_width * 2)
            
            # Resize photo to fit inner area (maintain aspect ratio, then crop to exact size)
            photo_img.thumbnail((inner_width, inner_height), Image.Resampling.LANCZOS)
            
            # Create a new image with exact inner dimensions
            resized_photo = Image.new('RGB', (inner_width, inner_height), 'white')
            
            # Calculate centering position
            paste_x = (inner_width - photo_img.width) // 2
            paste_y = (inner_height - photo_img.height) // 2
            
            # Paste the resized photo onto the white background
            resized_photo.paste(photo_img, (paste_x, paste_y))
            
            # Create a mask for rounded corners
            mask = Image.new('L', (inner_width, inner_height), 0)
            draw_mask = ImageDraw.Draw(mask)
            # Draw rounded rectangle mask
            draw_mask.rounded_rectangle(
                [(0, 0), (inner_width, inner_height)],
                radius=border_radius,
                fill=255
            )
            
            # Apply the mask to create rounded corners for the photo
            rounded_photo = Image.new('RGBA', (inner_width, inner_height), (255, 255, 255, 0))
            rounded_photo.paste(resized_photo, (0, 0))
            # Apply rounded corner mask
            rounded_photo.putalpha(mask)
            
            # Create the final image with rounded white border
            # First create white background with rounded corners
            bordered_img = Image.new('RGBA', (photo_width, photo_height), (255, 255, 255, 0))
            
            # Create a mask for the outer rounded rectangle (white border)
            outer_mask = Image.new('L', (photo_width, photo_height), 0)
            draw_outer_mask = ImageDraw.Draw(outer_mask)
            # Draw rounded rectangle for the white border (outer radius)
            draw_outer_mask.rounded_rectangle(
                [(0, 0), (photo_width, photo_height)],
                radius=border_radius + border_width,  # Outer radius includes border
                fill=255
            )
            
            # Create white background with rounded corners
            white_bg = Image.new('RGBA', (photo_width, photo_height), (255, 255, 255, 255))
            white_bg.putalpha(outer_mask)
            bordered_img = Image.alpha_composite(bordered_img, white_bg)
            
            # Paste the rounded photo on top of the white border
            bordered_img.paste(rounded_photo, (border_width, border_width), rounded_photo)
            
            # Save the bordered image
            photo_buffer = io.BytesIO()
            bordered_img.save(photo_buffer, format='PNG')
            photo_buffer.seek(0)
            
            # Draw photo with white border and rounded corners
            c.drawImage(ImageReader(photo_buffer), photo_x, photo_y, width=photo_width, height=photo_height)
        except Exception as e:
            print(f"Error adding photo: {e}")
    
    # Add member name (positioned below photo)
    # Adjust coordinates based on template
    name_x = photo_x
    name_y = photo_y - 25
    
    if member.name:
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(255, 255, 255)
        # Center the text or adjust as needed
        text_width = c.stringWidth(member.name, "Helvetica-Bold", 16)
        c.drawString(name_x + (photo_width - text_width) / 2, name_y, member.name)
    
    # Add KOALM number (positioned below name)
    koalm_x = photo_x
    koalm_y = name_y - 22
    
    if member.KOALM_number:
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0, 0, 0)
        koalm_text = f"LA NO: {member.KOALM_number}"
        text_width = c.stringWidth(koalm_text, "Helvetica", 12)
        c.drawString(koalm_x + (photo_width - text_width) / 2, koalm_y, koalm_text)
    
    # Add QR code (positioned in bottom-right box)
    # Adjust coordinates based on template
    qr_size = 75
    qr_x = page_width - 100  # Adjust based on template
    qr_y = page_height - 350  # Adjust based on template
    
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
    
    c.showPage()
    c.save()
    
    # Merge overlay with template
    overlay_buffer.seek(0)
    overlay_pdf = PdfReader(overlay_buffer)
    overlay_page = overlay_pdf.pages[0]
    
    # Create final PDF
    final_buffer = io.BytesIO()
    writer = PdfWriter()
    
    # Merge overlay with template
    template_page.merge_page(overlay_page)
    writer.add_page(template_page)
    writer.write(final_buffer)
    final_buffer.seek(0)
    
    # Create HTTP response
    response = HttpResponse(final_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="KOA_Badge_{member.KOALM_number}.pdf"'
    
    return response
