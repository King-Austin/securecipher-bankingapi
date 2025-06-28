from django.utils.deprecation import MiddlewareMixin

class CorsFixMiddleware(MiddlewareMixin):
    """
    Custom middleware to ensure CORS headers are added to all responses
    This helps with edge cases where django-cors-headers might not catch all responses
    """
    def process_response(self, request, response):
        # Check if the origin is in the request
        origin = request.META.get('HTTP_ORIGIN')
        
        # If CORS headers are not already set and we have an origin
        if origin and 'Access-Control-Allow-Origin' not in response:
            # Check if the origin is in our allowed origins or matches regex
            # This is a simple check - django-cors-headers does more sophisticated checking
            from django.conf import settings
            
            # For simplicity, we'll allow any origin in development
            # In production, you would check against your allowed origins
            if settings.DEBUG:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Request-With'
                
        return response
