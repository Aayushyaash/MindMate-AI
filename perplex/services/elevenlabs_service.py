"""
ElevenLabs AI Service for MindMate-AI

Provides:
    - Signed WebSocket URLs for real-time voice AI
    - Agent configuration for conversation initialization
    - Fallback sentiment analysis for call transcripts
"""
import os
import logging
import requests

from perplex.services.base import BaseService, ServiceHealthError, retry_with_backoff

logger = logging.getLogger(__name__)

_elevenlabs_instance = None


class ElevenLabsService(BaseService):
    """
    ElevenLabs Conversational AI service.
    
    Used for real-time bidirectional voice conversations:
        1. Get signed WebSocket URL
        2. Connect Twilio audio stream to ElevenLabs
        3. AI agent responds in real-time
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    HELP_URL = "https://elevenlabs.io/"
    
    # Keywords for local sentiment analysis fallback
    POSITIVE_KEYWORDS = ['happy', 'good', 'great', 'better', 'hope', 'thank', 'appreciate']
    NEGATIVE_KEYWORDS = ['sad', 'bad', 'worse', 'hopeless', 'anxious', 'stressed', 'worried']
    
    def __init__(self):
        """Initialize ElevenLabs client with API credentials."""
        self.api_key = self._validate_env_var("ELEVENLABS_API_KEY", self.HELP_URL)
        self.agent_id = self._validate_env_var(
            "ELEVENLABS_AGENT_ID",
            "https://elevenlabs.io/app/conversational-ai"
        )
        logger.info("ElevenLabsService initialized")
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    def get_signed_url(self) -> str:
        """
        Get a signed WebSocket URL for conversation.
        
        Returns:
            Signed WebSocket URL (valid for limited time)
        
        Used by:
            MediaStreamConsumer.setup_elevenlabs() to establish WebSocket connection
        """
        url = f"{self.BASE_URL}/convai/conversation/get_signed_url"
        response = requests.get(
            url,
            params={"agent_id": self.agent_id},
            headers={"xi-api-key": self.api_key},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("signed_url")
    
    def create_agent_config(self, custom_prompt: str = None, first_message: str = None) -> dict:
        """
        Create agent configuration for WebSocket initialization.
        
        Args:
            custom_prompt: Override default agent prompt (optional)
            first_message: Custom greeting message (optional)
        
        Returns:
            Configuration dict to send after WebSocket connect
        """
        config = {
            "type": "conversation_initiation_client_data",
        }
        
        if custom_prompt or first_message:
            config["conversation_config_override"] = {}
            if custom_prompt:
                config["conversation_config_override"]["agent"] = {
                    "prompt": {"prompt": custom_prompt}
                }
            if first_message:
                config["conversation_config_override"]["agent"] = {
                    **config["conversation_config_override"].get("agent", {}),
                    "first_message": first_message
                }
        
        return config
    
    def analyze_sentiment(self, transcript: str) -> dict:
        """
        Analyze sentiment of call transcript (local keyword-based fallback).
        
        This is a simple local analysis, not an API call.
        Used when Cloudflare API is not needed for voice call sentiment.
        
        Args:
            transcript: Full call transcript text
        
        Returns:
            dict with sentiment scores (0.0 to 1.0 scale)
        """
        text_lower = transcript.lower()
        
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text_lower)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text_lower)
        
        total = positive_count + negative_count or 1
        
        return {
            "positive_score": round(positive_count / total, 2),
            "negative_score": round(negative_count / total, 2),
            "analysis_type": "keyword_based"
        }
    
    def health_check(self) -> bool:
        """Verify ElevenLabs API connectivity by getting a signed URL."""
        try:
            url = self.get_signed_url()
            if not url:
                raise ServiceHealthError("ElevenLabs", "Empty signed URL returned")
            logger.info("✓ ElevenLabs: Connected (conversational AI ready)")
            return True
        except Exception as e:
            raise ServiceHealthError("ElevenLabs", str(e))


def get_elevenlabs_service() -> ElevenLabsService:
    """Get or create the singleton ElevenLabsService instance."""
    global _elevenlabs_instance
    if _elevenlabs_instance is None:
        _elevenlabs_instance = ElevenLabsService()
    return _elevenlabs_instance