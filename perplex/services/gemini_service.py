"""
Google Gemini AI Service for MindMate-AI

Provides:
    - Text generation (chat, recommendations, quizzes)
    - Multimodal content extraction (prescription OCR)
    - Automatic fallback from Gemini 3 to Gemini 2.5 models
"""
import os
import logging
from google import genai

from perplex.services.base import BaseService, ServiceHealthError, retry_with_backoff

logger = logging.getLogger(__name__)

_gemini_instance = None


class GeminiService(BaseService):
    """
    Google Gemini AI service with lazy initialization and model fallback.
    
    Models:
        - flash: gemini-3-flash (fast) → fallback: gemini-2.5-flash
        - pro: gemini-3-pro-preview (complex) → fallback: gemini-2.5-pro
    """
    
    MODELS = {
        "flash": "gemini-3-flash",
        "flash_fallback": "gemini-2.5-flash",
        "pro": "gemini-3-pro-preview",
        "pro_fallback": "gemini-2.5-pro",
    }
    
    HELP_URL = "https://ai.google.dev/"
    
    def __init__(self):
        """Initialize Gemini client. Raises MissingConfigError if GEMINI_API_KEY not set."""
        api_key = self._validate_env_var("GEMINI_API_KEY", self.HELP_URL)
        self.client = genai.Client(api_key=api_key)
        logger.info("GeminiService initialized")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def generate_content(self, prompt: str, model_type: str = "flash", **kwargs) -> str:
        """
        Generate text content using Gemini models with automatic fallback.
        
        Args:
            prompt: The text prompt to send to the model
            model_type: "flash" (fast) or "pro" (complex reasoning)
        
        Returns:
            Generated text response
        """
        primary_model = self.MODELS.get(model_type, self.MODELS["flash"])
        fallback_model = self.MODELS.get(f"{model_type}_fallback")
        
        try:
            response = self.client.models.generate_content(
                model=primary_model, contents=prompt, **kwargs
            )
            return response.text
        except Exception as e:
            if fallback_model and "not found" in str(e).lower():
                logger.warning(f"Model {primary_model} not available, using {fallback_model}")
                response = self.client.models.generate_content(
                    model=fallback_model, contents=prompt, **kwargs
                )
                return response.text
            raise
    
    @retry_with_backoff(max_retries=2, base_delay=2.0)
    def extract_prescription(self, image_data: bytes, mime_type: str) -> str:
        """
        Extract prescription information from an image using multimodal Gemini Pro.
        
        Args:
            image_data: Raw image bytes (JPEG, PNG, or PDF)
            mime_type: MIME type (e.g., "image/jpeg", "application/pdf")
        
        Returns:
            HTML-formatted extracted prescription data
        """
        prompt = '''Analyze this prescription image and extract key information.
        
OUTPUT FORMAT: Clean HTML using <h3>, <ul>, <li>, <strong> tags only.

EXTRACT:
1. Patient Details (name, age, gender if visible)
2. Prescribing Doctor (name, credentials)
3. Diagnosis/Condition
4. Date of prescription
5. Medications: Drug name, Dosage, Frequency, Duration
6. Special Instructions

RULES:
- Extract ONLY critical medical information
- Ignore logos, watermarks, barcodes
- If unclear, mark as "[unclear]"
- If NOT a prescription: "This does not appear to be a medical prescription."
'''
        
        primary = self.MODELS["pro"]
        fallback = self.MODELS["pro_fallback"]
        contents = [prompt, genai.types.Part.from_bytes(data=image_data, mime_type=mime_type)]
        
        try:
            response = self.client.models.generate_content(model=primary, contents=contents)
            return response.text
        except Exception as e:
            if "not found" in str(e).lower():
                response = self.client.models.generate_content(model=fallback, contents=contents)
                return response.text
            raise
    
    def health_check(self) -> bool:
        """Verify Gemini API connectivity by listing available models."""
        try:
            # list() iterates the generator to verify connectivity
            models = list(self.client.models.list(config={"page_size": 1}))
            if not models:
                # It's possible to have no models, but unlikely. 
                # If we can list, we are connected.
                pass 
                
            # We can't easily check for specific models without paging through all, 
            # so just successful connection is enough for health check.
            logger.info(f"✓ Gemini AI: Connected")
            return True
        except Exception as e:
            raise ServiceHealthError("Gemini AI", str(e))


def get_gemini_service() -> GeminiService:
    """Get or create the singleton GeminiService instance."""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiService()
    return _gemini_instance
