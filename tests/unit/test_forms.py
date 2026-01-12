"""
Unit tests for form validation.
"""
import pytest
from app.forms import PHQ9Form, JournalForm


class TestPHQ9Form:
    """Test PHQ-9 assessment form validation."""
    
    def test_valid_form_all_zeros(self):
        """All questions answered with 0 should be valid."""
        data = {f'q{i}': 0 for i in range(1, 10)}
        form = PHQ9Form(data=data)
        assert form.is_valid()
    
    def test_valid_form_all_threes(self):
        """All questions answered with 3 should be valid."""
        data = {f'q{i}': 3 for i in range(1, 10)}
        form = PHQ9Form(data=data)
        assert form.is_valid()
    
    def test_invalid_missing_all_fields(self):
        """Empty form should have 9 errors."""
        form = PHQ9Form(data={})
        assert not form.is_valid()
        assert len(form.errors) == 9
    
    def test_invalid_missing_one_field(self):
        """Missing one question should be invalid."""
        data = {f'q{i}': 0 for i in range(1, 9)}  # Missing q9
        form = PHQ9Form(data=data)
        assert not form.is_valid()
        assert 'q9' in form.errors


class TestJournalForm:
    """Test journal entry form validation."""
    
    def test_valid_content(self):
        """Non-empty content should be valid."""
        form = JournalForm(data={'content': 'Today was a good day.'})
        assert form.is_valid()
    
    def test_empty_content_invalid(self):
        """Empty content should be invalid."""
        form = JournalForm(data={'content': ''})
        assert not form.is_valid()
    
    def test_whitespace_only_invalid(self):
        """Whitespace-only content should be invalid."""
        form = JournalForm(data={'content': '   '})
        assert not form.is_valid()