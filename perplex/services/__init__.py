"""
MindMate-AI Centralized Services
Exports lazy singleton getters for all AI services
"""
from perplex.services.gemini_service import get_gemini_service
from perplex.services.cloudflare_service import get_cloudflare_service
from perplex.services.elevenlabs_service import get_elevenlabs_service
from perplex.services.twilio_service import get_twilio_service

__all__ = [
    'get_gemini_service',
    'get_cloudflare_service', 
    'get_elevenlabs_service',
    'get_twilio_service',
]
