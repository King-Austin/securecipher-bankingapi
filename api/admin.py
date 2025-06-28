from django.contrib import admin
from .models import UserProfile, Transaction, Card, Message

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'account_balance', 'phone', 'pin_set')
    search_fields = ('user__username', 'user__email', 'account_number', 'phone')
    list_filter = ('pin_set',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'type', 'amount', 'status', 'created_at')
    search_fields = ('reference', 'user__username', 'recipient_name', 'recipient_account')
    list_filter = ('type', 'status', 'created_at')
    date_hierarchy = 'created_at'

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_brand', 'card_type', 'card_number', 'status', 'expiry_date')
    search_fields = ('user__username', 'card_number')
    list_filter = ('card_brand', 'card_type', 'status')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'priority', 'read', 'created_at')
    search_fields = ('user__username', 'title', 'content')
    list_filter = ('type', 'priority', 'read', 'created_at')
    date_hierarchy = 'created_at'
