from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'cards', views.CardViewSet, basename='card')
router.register(r'messages', views.MessageViewSet, basename='message')

# Define URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/update-public-key/', views.update_public_key, name='update-public-key'),
    path('auth/set-pin/', views.set_pin, name='set-pin'),
    
    # Transaction endpoints
    path('transactions/transfer/', views.create_transfer, name='transfer'),
    path('transactions/verify-account/<str:account_number>/', views.verify_account, name='verify-account'),
    
    # Message endpoints
    path('messages/<int:pk>/read/', views.mark_message_read, name='mark-message-read'),
]
