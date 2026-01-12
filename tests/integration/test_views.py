"""
Integration tests for view endpoints.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboardView:
    """Test dashboard view access control."""
    
    def test_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_authenticated_access(self, authenticated_client):
        """Authenticated users should access dashboard."""
        response = authenticated_client.get(reverse('dashboard'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestChatView:
    """Test chat endpoint with mocked AI service."""
    
    def test_chat_requires_login(self, client):
        """Chat should require authentication."""
        response = client.post(reverse('chat_api'), {'message': 'Hello'})
        assert response.status_code == 302
    
    def test_chat_empty_message(self, authenticated_client):
        """Empty message should return error."""
        response = authenticated_client.post(
            reverse('chat_api'),
            {'message': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        # Should return error in JSON (from our view implementation)
        assert b'I\'m here to listen' in response.content


@pytest.mark.django_db
class TestPHQ9View:
    """Test PHQ-9 assessment flow."""
    
    def test_phq9_form_renders(self, authenticated_client):
        """PHQ-9 form page should render for authenticated users."""
        response = authenticated_client.get(reverse('phq9'))
        assert response.status_code == 200
        assert b'q1' in response.content  # First question field
