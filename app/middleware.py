"""
Rate Limiting Middleware for MindMate-AI

Handles rate limit exceptions and returns JSON responses.
"""
from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited


class RateLimitMiddleware:
    """
    Middleware to handle rate limit exceeded errors gracefully.
    
    Returns JSON response instead of raising exception,
    which is better for AJAX/API endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """Convert Ratelimited exceptions to JSON responses."""
        if isinstance(exception, Ratelimited):
            return JsonResponse({
                'error': 'Rate limit exceeded. Please wait before trying again.',
                'retry_after': 60,
                'status': 'rate_limited'
            }, status=429)
        return None
