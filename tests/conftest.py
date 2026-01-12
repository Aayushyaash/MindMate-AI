"""
Shared pytest fixtures for MindMate-AI tests.

Provides:
    - User fixtures (regular, authenticated)
    - Mock service fixtures (Gemini, Cloudflare)
    - Database fixtures
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User


# =============================================================================
# USER FIXTURES
# =============================================================================

@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return a client logged in as test user."""
    client.login(username='testuser', password='testpass123')
    return client


# =============================================================================
# SERVICE MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_gemini_service():
    """Mock GeminiService for testing without API calls."""
    with patch('perplex.services.gemini_service.get_gemini_service') as mock:
        service = Mock()
        service.generate_content.return_value = "Mock AI response"
        service.extract_prescription.return_value = "<h3>Mock Prescription</h3>"
        service.health_check.return_value = True
        mock.return_value = service
        yield service


@pytest.fixture
def mock_cloudflare_service():
    """Mock CloudflareService for testing without API calls."""
    with patch('perplex.services.cloudflare_service.get_cloudflare_service') as mock:
        service = Mock()
        service.analyze_sentiment.return_value = {"positive": 0.7, "negative": 0.3}
        service.calculate_depression_score.return_value = {
            "depression_score": 5,
            "confidence": 0.8,
            "processed_text": "test",
            "raw_result": {"positive": 0.7, "negative": 0.3}
        }
        service.health_check.return_value = True
        mock.return_value = service
        yield service


@pytest.fixture
def mock_all_services(mock_gemini_service, mock_cloudflare_service):
    """Mock all AI services for full integration testing."""
    return {
        "gemini": mock_gemini_service,
        "cloudflare": mock_cloudflare_service
    }