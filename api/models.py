from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    bvn = models.CharField(max_length=50, blank=True)
    nin = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, unique=True)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    profile_picture = models.URLField(blank=True)
    public_key = models.TextField(blank=True)
    pin_set = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('transfer', 'Transfer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    description = models.TextField(blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_account = models.CharField(max_length=20, blank=True)
    recipient_bank = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency}"

class Card(models.Model):
    CARD_TYPES = (
        ('debit', 'Debit Card'),
        ('credit', 'Credit Card'),
    )
    
    CARD_BRANDS = (
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('verve', 'Verve'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=20)  # Masked number for display
    card_type = models.CharField(max_length=10, choices=CARD_TYPES)
    card_brand = models.CharField(max_length=20, choices=CARD_BRANDS)
    expiry_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.card_brand} {self.card_type} ending in {self.card_number[-4:]}"

class Message(models.Model):
    MESSAGE_TYPES = (
        ('notification', 'Notification'),
        ('alert', 'Alert'),
        ('promotion', 'Promotion'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
