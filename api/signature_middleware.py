import json
import base64
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class CryptographicSignatureMiddleware(MiddlewareMixin):
    """
    Middleware to verify cryptographic signatures on sensitive API requests.
    This ensures that requests are coming from the authenticated user and haven't been tampered with.
    """
    
    # Define which endpoints require cryptographic signatures
    SIGNATURE_REQUIRED_ENDPOINTS = [
        '/api/transactions/verify-account/',
        '/api/transactions/transfer/',
        '/api/auth/update-public-key/',
        '/api/profiles/',  # Profile updates
        '/api/cards/',     # Card management
    ]
    
    # Methods that require signatures
    SIGNATURE_REQUIRED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def process_request(self, request):
        """Process incoming request and verify signature if required"""
        
        # Skip signature verification for certain conditions
        if not self._requires_signature(request):
            return None
            
        # Check if user is authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required for signed requests'
            }, status=401)
        
        # Extract signature from headers
        signature = request.META.get('HTTP_X_SIGNATURE')
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        
        if not signature or not timestamp:
            return JsonResponse({
                'error': 'Missing cryptographic signature or timestamp',
                'details': 'Sensitive operations require digital signature verification'
            }, status=400)
        
        # Verify the signature
        try:
            if not self._verify_signature(request, signature, timestamp):
                return JsonResponse({
                    'error': 'Invalid cryptographic signature',
                    'details': 'Request signature verification failed'
                }, status=403)
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return JsonResponse({
                'error': 'Signature verification failed',
                'details': 'Unable to verify request authenticity'
            }, status=500)
        
        return None
    
    def _requires_signature(self, request):
        """Check if the request requires a cryptographic signature"""
        
        # Skip for non-sensitive methods
        if request.method not in self.SIGNATURE_REQUIRED_METHODS:
            return False
        
        # Check if the endpoint requires signature
        path = request.path
        for endpoint in self.SIGNATURE_REQUIRED_ENDPOINTS:
            if path.startswith(endpoint):
                return True
        
        return False
    
    def _verify_signature(self, request, signature_b64, timestamp):
        """Verify the cryptographic signature"""
        
        try:
            # Get user's public key
            profile = UserProfile.objects.get(user=request.user)
            if not profile.public_key:
                logger.warning(f"No public key found for user {request.user.username}")
                return False
            
            # Decode the signature
            signature = base64.b64decode(signature_b64)
            
            # Reconstruct the signed data
            request_data = self._get_request_data(request)
            data_to_verify = {
                'method': request.method,
                'path': request.path,
                'data': request_data,
                'timestamp': timestamp,
                'user_id': str(request.user.id)
            }
            
            # Convert to JSON string for verification
            data_string = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
            
            # Load the public key
            public_key_bytes = base64.b64decode(profile.public_key)
            public_key = serialization.load_der_public_key(public_key_bytes)
            
            # Verify the signature
            public_key.verify(
                signature,
                data_string.encode('utf-8'),
                ec.ECDSA(hashes.SHA384())
            )
            
            logger.info(f"Signature verified successfully for user {request.user.username}")
            return True
            
        except InvalidSignature:
            logger.warning(f"Invalid signature for user {request.user.username}")
            return False
        except UserProfile.DoesNotExist:
            logger.error(f"User profile not found for {request.user.username}")
            return False
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False
    
    def _get_request_data(self, request):
        """Extract and parse request data"""
        try:
            if hasattr(request, '_body'):
                body = request._body
            else:
                body = request.body
            
            if body:
                return json.loads(body.decode('utf-8'))
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
