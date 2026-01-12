"""
Twilio Voice Service for MindMate-AI

Provides:
    - Outbound call initiation
    - Call status tracking
    - Phone number validation
"""
import os
import logging
from twilio.rest import Client

from perplex.services.base import BaseService, ServiceHealthError

logger = logging.getLogger(__name__)

_twilio_instance = None


class TwilioService(BaseService):
    """
    Twilio Voice API service for phone call management.
    
    Workflow:
        1. initiate_call() → Twilio calls user's phone
        2. Twilio requests TwiML from our webhook
        3. TwiML connects call to WebSocket (→ ElevenLabs)
        4. get_call_status() / get_call_details() for tracking
    """
    
    HELP_URL = "https://console.twilio.com/"
    
    def __init__(self):
        """Initialize Twilio client with API credentials."""
        account_sid = self._validate_env_var("TWILIO_ACCOUNT_SID", self.HELP_URL)
        auth_token = self._validate_env_var("TWILIO_AUTH_TOKEN", self.HELP_URL)
        self.from_number = self._validate_env_var("TWILIO_PHONE_NUMBER", self.HELP_URL)
        
        self.client = Client(account_sid, auth_token)
        logger.info("TwilioService initialized")
    
    def initiate_call(self, to_number: str, twiml_url: str) -> str:
        """
        Initiate an outbound call to a user.
        
        Args:
            to_number: Destination phone number (E.164 format: +1234567890)
            twiml_url: URL that returns TwiML instructions for the call
        
        Returns:
            Call SID (unique identifier for tracking)
        
        Example:
            call_sid = service.initiate_call(
                to_number="+11234567890",
                twiml_url="https://example.com/voice/twiml/123/"
            )
        """
        call = self.client.calls.create(
            to=to_number,
            from_=self.from_number,
            url=twiml_url,
            method='POST',
            status_callback_method='POST',
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            timeout=60,
            record=False
        )
        logger.info(f"Call initiated: {call.sid} to {to_number}")
        return call.sid
    
    def get_call_details(self, call_sid: str) -> dict:
        """
        Get detailed information about a call.
        
        Args:
            call_sid: Twilio Call SID
        
        Returns:
            dict with: status, duration, start_time, end_time, direction
        """
        call = self.client.calls(call_sid).fetch()
        return {
            "status": call.status,
            "duration": call.duration,
            "start_time": call.start_time,
            "end_time": call.end_time,
            "direction": call.direction,
            "from": call.from_,
            "to": call.to
        }
    
    def get_call_status(self, call_sid: str) -> str:
        """
        Get current status of a call.
        
        Returns one of: queued, ringing, in-progress, completed, 
                        busy, failed, no-answer, canceled
        """
        call = self.client.calls(call_sid).fetch()
        return call.status
    
    def hang_up_call(self, call_sid: str) -> bool:
        """
        Hang up an active call.
        
        Returns:
            True if call was successfully terminated
        """
        try:
            self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} terminated")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up call {call_sid}: {e}")
            return False
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate a phone number using Twilio Lookup API.
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self.client.lookups.v2.phone_numbers(phone_number).fetch()
            return True
        except Exception:
            return False
    
    def health_check(self) -> bool:
        """Verify Twilio API connectivity by fetching account info."""
        try:
            account = self.client.api.accounts(self.client.account_sid).fetch()
            if account.status != 'active':
                raise ServiceHealthError("Twilio", f"Account status: {account.status}")
            logger.info("✓ Twilio: Connected (voice API ready)")
            return True
        except Exception as e:
            raise ServiceHealthError("Twilio", str(e))


def get_twilio_service() -> TwilioService:
    """Get or create the singleton TwilioService instance."""
    global _twilio_instance
    if _twilio_instance is None:
        _twilio_instance = TwilioService()
    return _twilio_instance
