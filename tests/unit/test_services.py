"""
Unit tests for AI service modules.
Tests lazy singleton pattern and health checks with mocked APIs.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGeminiService:
    """Test GeminiService implementation."""
    
    def test_singleton_pattern(self):
        """get_gemini_service should return same instance."""
        with patch('perplex.services.gemini_service.genai') as mock_genai:
            mock_genai.Client.return_value = Mock()
            
            # Reset singleton
            import perplex.services.gemini_service as gs
            gs._gemini_instance = None
            
            with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
                service1 = gs.get_gemini_service()
                service2 = gs.get_gemini_service()
                assert service1 is service2
    
    def test_missing_api_key_raises_error(self):
        """Missing GEMINI_API_KEY should raise MissingConfigError."""
        import perplex.services.gemini_service as gs
        gs._gemini_instance = None
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                gs.get_gemini_service()
            assert 'GEMINI_API_KEY' in str(exc_info.value)


class TestCloudflareService:
    """Test CloudflareService implementation."""
    
    def test_depression_score_calculation(self):
        """Test depression score calculation logic."""
        with patch('perplex.services.cloudflare_service.requests') as mock_requests:
            mock_response = Mock()
            mock_response.json.return_value = {
                "result": [
                    {"label": "NEGATIVE", "score": 0.8},
                    {"label": "POSITIVE", "score": 0.2}
                ]
            }
            mock_response.raise_for_status = Mock()
            mock_requests.post.return_value = mock_response
            
            import perplex.services.cloudflare_service as cs
            cs._cloudflare_instance = None
            
            with patch.dict('os.environ', {
                'CLOUDFLARE_API_TOKEN': 'test_token',
                'CLOUDFLARE_ACCOUNT_ID': 'test_account'
            }):
                service = cs.get_cloudflare_service()
                result = service.calculate_depression_score("I feel sad")
                
                assert 'depression_score' in result
                assert 0 <= result['depression_score'] <= 25
                assert 'confidence' in result


class TestHealthCheck:
    """Test health check system."""
    
    def test_skip_health_checks_setting(self):
        """SKIP_HEALTH_CHECKS=True should skip all checks."""
        from perplex.services.health_check import validate_all_services
        
        with patch('perplex.services.health_check.settings') as mock_settings:
            mock_settings.SKIP_HEALTH_CHECKS = True
            # Should not raise any exception
            validate_all_services()
