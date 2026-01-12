"""
Cloudflare AI Service for MindMate-AI

Provides:
    - Sentiment analysis using DistilBERT model
    - Depression score calculation from audio transcripts
    - Journal entry sentiment scoring
"""
import os
import logging
import requests

from perplex.services.base import BaseService, ServiceHealthError, retry_with_backoff

logger = logging.getLogger(__name__)

_cloudflare_instance = None


class CloudflareService(BaseService):
    """
    Cloudflare Workers AI service for sentiment analysis.
    
    Model: @cf/huggingface/distilbert-sst-2-int8 (DistilBERT for sentiment)
    
    Returns sentiment scores:
        - positive: 0.0 to 1.0
        - negative: 0.0 to 1.0
    """
    
    MODEL = "@cf/huggingface/distilbert-sst-2-int8"
    HELP_URL = "https://dash.cloudflare.com/profile/api-tokens"
    
    # Keywords that boost depression score
    DEPRESSION_KEYWORDS = [
        'sad', 'depressed', 'hopeless', 'worthless', 'suffer',
        "can't feel", 'pain', 'tired', 'exhausted', 'give up',
        'alone', 'empty', 'numb', 'anxious', 'worried'
    ]
    
    def __init__(self):
        """Initialize Cloudflare client with API credentials."""
        self.api_token = self._validate_env_var("CLOUDFLARE_API_TOKEN", self.HELP_URL)
        self.account_id = self._validate_env_var(
            "CLOUDFLARE_ACCOUNT_ID", 
            "https://dash.cloudflare.com/"
        )
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/"
        logger.info("CloudflareService initialized")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze text sentiment using Cloudflare's DistilBERT model.
        
        Args:
            text: Text to analyze (journal entry, transcript, etc.)
        
        Returns:
            dict with keys:
                - positive: float (0.0 to 1.0)
                - negative: float (0.0 to 1.0)
        
        Example:
            result = service.analyze_sentiment("I feel great today!")
            # {"positive": 0.95, "negative": 0.05}
        """
        response = requests.post(
            f"{self.base_url}{self.MODEL}",
            headers={"Authorization": f"Bearer {self.api_token}"},
            json={"text": text},
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json().get("result", [])
        
        positive_score = 0.0
        negative_score = 0.0
        
        for item in result:
            label = item.get("label", "").upper()
            score = item.get("score", 0.0)
            if label == "POSITIVE":
                positive_score = score
            elif label == "NEGATIVE":
                negative_score = score
        
        return {
            "positive": positive_score,
            "negative": negative_score
        }
    
    def calculate_depression_score(self, text: str) -> dict:
        """
        Calculate depression score from text (0-25 scale).
        
        Processing:
            1. Get sentiment scores from Cloudflare API
            2. Apply non-linear scaling: base_score = negative^1.5 * 25
            3. Boost score for depression keywords (+2 each, max 25)
        
        Args:
            text: Audio transcript or text to analyze
        
        Returns:
            dict with keys:
                - depression_score: int (0-25)
                - confidence: float (0.0 to 1.0)
                - processed_text: str (cleaned input)
                - raw_result: dict (original sentiment scores)
        
        Example:
            result = service.calculate_depression_score("I feel so tired and hopeless")
            # {"depression_score": 18, "confidence": 0.85, ...}
        """
        try:
            sentiment = self.analyze_sentiment(text)
            negative_score = sentiment.get("negative", 0.0)
            
            # Non-linear scaling: higher negative scores increase exponentially
            base_score = (negative_score ** 1.5) * 25
            
            # Boost for depression keywords
            text_lower = text.lower()
            keyword_count = sum(1 for kw in self.DEPRESSION_KEYWORDS if kw in text_lower)
            keyword_boost = keyword_count * 2
            
            # Final score (capped at 25)
            final_score = min(int(base_score + keyword_boost), 25)
            
            # Confidence based on text length and sentiment clarity
            confidence = min(1.0, abs(sentiment["positive"] - sentiment["negative"]) + 0.3)
            
            return {
                "depression_score": final_score,
                "confidence": round(confidence, 2),
                "processed_text": text[:500],  # Truncate for storage
                "raw_result": sentiment
            }
        except Exception as e:
            logger.error(f"Depression score calculation failed: {e}")
            return {
                "depression_score": 0,
                "confidence": 0.0,
                "processed_text": text[:500],
                "raw_result": {"error": str(e)}
            }
    
    def health_check(self) -> bool:
        """Verify Cloudflare API connectivity with lightweight inference."""
        try:
            result = self.analyze_sentiment("test")
            if "positive" not in result or "negative" not in result:
                raise ServiceHealthError("Cloudflare AI", "Invalid response format")
            logger.info("✓ Cloudflare AI: Connected (distilbert-sst-2-int8)")
            return True
        except Exception as e:
            raise ServiceHealthError("Cloudflare AI", str(e))


def get_cloudflare_service() -> CloudflareService:
    """Get or create the singleton CloudflareService instance."""
    global _cloudflare_instance
    if _cloudflare_instance is None:
        _cloudflare_instance = CloudflareService()
    return _cloudflare_instance
