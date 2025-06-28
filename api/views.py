from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from .models import UserProfile, Transaction, Card, Message
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    TransactionSerializer, 
    CardSerializer, 
    MessageSerializer
)
import random
import string
import uuid

# Authentication Views
@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user and create their profile"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
        
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create user with the provided data
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=request.data.get('password'),
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', '')
        )
        
        # Get phone number from request
        phone = request.data.get('phone', '')
        
        # Generate account number by stripping the leading zero from phone number
        # If phone number is provided and starts with zero, strip it, otherwise use random digits
        if phone and phone.startswith('0'):
            account_number = phone[1:]  # Remove leading zero
        elif phone:
            account_number = phone  # Use as is if no leading zero
        else:
            # Fallback to random number if no phone provided
            account_number = ''.join(random.choices(string.digits, k=10))
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            phone=phone,
            account_number=account_number,
            # Initial balance of 1000 NGN for testing
            account_balance=1000.00
        )
        
        # Generate authentication token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login_user(request):
    """Login a user and return their token"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        profile = UserProfile.objects.get(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile).data,
            'token': token.key
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST', 'OPTIONS'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout a user by deleting their token"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
        
    request.user.auth_token.delete()
    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_public_key(request):
    """Update the user's public key"""
    public_key = request.data.get('public_key')
    
    if not public_key:
        return Response({'error': 'Public key is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        profile.public_key = public_key
        profile.save()
        
        return Response({
            'message': 'Public key updated successfully',
            'profile': UserProfileSerializer(profile).data
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_pin(request):
    """Mark that the user has set their PIN (the PIN itself is stored client-side)"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        profile.pin_set = True
        profile.save()
        
        return Response({
            'message': 'PIN set successfully',
            'profile': UserProfileSerializer(profile).data
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

# User Profile ViewSet
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

# Transaction ViewSet and Views
class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transfer(request):
    """Create a new transfer transaction"""
    recipient_account = request.data.get('recipient_account')
    recipient_bank = request.data.get('recipient_bank')
    amount = request.data.get('amount')
    description = request.data.get('description', '')
    
    # Validate inputs
    if not all([recipient_account, recipient_bank, amount]):
        return Response({
            'error': 'Recipient account, bank, and amount are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = float(amount)
    except ValueError:
        return Response({'error': 'Amount must be a number'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get sender profile
    try:
        sender_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if sender has enough balance
    if sender_profile.account_balance < amount:
        return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Find recipient if it's within our system
    recipient_profile = None
    recipient_name = request.data.get('recipient_name', 'External Account')
    
    if recipient_bank.lower() == 'secure cipher bank':
        try:
            recipient_profile = UserProfile.objects.get(account_number=recipient_account)
            recipient_name = f"{recipient_profile.user.first_name} {recipient_profile.user.last_name}".strip()
            if not recipient_name:
                recipient_name = recipient_profile.user.username
        except UserProfile.DoesNotExist:
            return Response({'error': 'Recipient account not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate unique reference
    reference = f"TRF-{str(uuid.uuid4())[:8].upper()}"
    
    with transaction.atomic():
        # Deduct from sender
        sender_profile.account_balance -= amount
        sender_profile.save()
        
        # Create sender's transaction record
        sender_transaction = Transaction.objects.create(
            user=request.user,
            type='transfer',
            amount=amount,
            currency='NGN',
            description=description,
            recipient_name=recipient_name,
            recipient_account=recipient_account,
            recipient_bank=recipient_bank,
            status='completed',
            reference=reference,
            balance_after=sender_profile.account_balance,
            category='Transfer'
        )
        
        # If recipient is within our system, credit their account
        if recipient_profile:
            recipient_profile.account_balance += amount
            recipient_profile.save()
            
            # Create recipient's transaction record
            Transaction.objects.create(
                user=recipient_profile.user,
                type='credit',
                amount=amount,
                currency='NGN',
                description=description or f"Transfer from {request.user.username}",
                recipient_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                recipient_account=sender_profile.account_number,
                recipient_bank='Secure Cipher Bank',
                status='completed',
                reference=f"CR-{reference[4:]}",
                balance_after=recipient_profile.account_balance,
                category='Credit'
            )
    
    return Response({
        'message': 'Transfer completed successfully',
        'transaction': TransactionSerializer(sender_transaction).data
    }, status=status.HTTP_201_CREATED)

# Card ViewSet
class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Message ViewSet
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(user=self.request.user).order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_read(request, pk):
    """Mark a message as read"""
    try:
        message = Message.objects.get(pk=pk, user=request.user)
        message.read = True
        message.save()
        return Response(MessageSerializer(message).data)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_account(request, account_number):
    """Verify if an account number exists and return the account holder's name"""
    try:
        # Find the user profile with the given account number
        profile = UserProfile.objects.get(account_number=account_number)
        
        # Return the account holder's name
        return Response({
            'exists': True,
            'name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username,
            'bank': 'Secure Cipher Bank'
        }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'exists': False,
            'message': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)
