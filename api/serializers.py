from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Transaction, Card, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'phone', 'bvn', 'nin', 'date_of_birth', 
            'address', 'occupation', 'account_number', 'account_balance',
            'profile_picture', 'public_key', 'pin_set'
        ]
        read_only_fields = ['account_balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'type', 'amount', 'currency', 'description',
            'recipient_name', 'recipient_account', 'recipient_bank',
            'status', 'reference', 'balance_after', 'category',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'reference', 'balance_after', 'created_at', 'updated_at']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id', 'user', 'card_number', 'card_type', 'card_brand',
            'expiry_date', 'status', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'user', 'title', 'content', 'type',
            'priority', 'read', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']
