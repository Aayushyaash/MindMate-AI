"""
Startup Health Check System for MindMate-AI

Validates all AI service API keys at application startup.
Core services block startup on failure; optional services only warn.
"""
import logging
from django.conf import settings

from perplex.services.gemini_service import get_gemini_service
from perplex.services.cloudflare_service import get_cloudflare_service
from perplex.services.elevenlabs_service import get_elevenlabs_service
from perplex.services.twilio_service import get_twilio_service
from perplex.services.base import MissingConfigError, ServiceHealthError

logger = logging.getLogger(__name__)


class ServiceConfigurationError(Exception):
    """
    Raised when one or more services fail health checks at startup.
    
    Contains formatted error message with all failures and help URLs.
    """
    def __init__(self, failures: list):
        self.failures = failures
        message = self._format_message()
        super().__init__(message)
    
    def _format_message(self) -> str:
        lines = [
            "",
            "❌ STARTUP FAILED - Invalid API Configuration:",
            ""
        ]
        for failure in self.failures:
            lines.append(f"{failure['service']}: {failure['error']}")
            lines.append(f"  → Get credentials: {failure['help_url']}")
            lines.append("")
        return "\n".join(lines)


# Core services - required for app to function
CORE_SERVICES = [
    (get_gemini_service, "Gemini AI", "https://ai.google.dev/"),
    (get_cloudflare_service, "Cloudflare AI", "https://dash.cloudflare.com/profile/api-tokens"),
]

# Optional services - only validated if VOICE_CALLS_ENABLED=True
OPTIONAL_SERVICES = [
    (get_elevenlabs_service, "ElevenLabs", "https://elevenlabs.io/"),
    (get_twilio_service, "Twilio", "https://console.twilio.com/"),
]


def validate_all_services():
    """
    Validate all AI services at startup.
    
    Behavior:
        - If SKIP_HEALTH_CHECKS=True: Skip all checks (with warning)
        - CORE_SERVICES: Always validated, failures block startup
        - OPTIONAL_SERVICES: Only if VOICE_CALLS_ENABLED=True, failures warn only
    
    Raises:
        ServiceConfigurationError: If any core service fails
    """
    # Check if health checks should be skipped
    if getattr(settings, 'SKIP_HEALTH_CHECKS', False):
        logger.warning("⚠️ SKIP_HEALTH_CHECKS=True - API validation skipped")
        logger.warning("   Set SKIP_HEALTH_CHECKS=False for production!")
        return
    
    core_failures = []
    optional_warnings = []
    
    # Validate core services (required)
    logger.info("Validating core services...")
    for getter, name, help_url in CORE_SERVICES:
        try:
            service = getter()
            service.health_check()
        except MissingConfigError as e:
            core_failures.append({
                "service": e.env_var,
                "error": "Missing environment variable",
                "help_url": e.help_url
            })
        except ServiceHealthError as e:
            core_failures.append({
                "service": name,
                "error": e.details,
                "help_url": help_url
            })
        except Exception as e:
            core_failures.append({
                "service": name,
                "error": str(e),
                "help_url": help_url
            })
    
    # Validate optional services (if enabled)
    voice_enabled = getattr(settings, 'VOICE_CALLS_ENABLED', False)
    if voice_enabled:
        logger.info("Validating voice services (VOICE_CALLS_ENABLED=True)...")
        for getter, name, help_url in OPTIONAL_SERVICES:
            try:
                service = getter()
                service.health_check()
            except (MissingConfigError, ServiceHealthError, Exception) as e:
                optional_warnings.append({
                    "service": name,
                    "error": str(e),
                    "help_url": help_url
                })
    else:
        logger.warning("⚠️ Voice calls disabled (VOICE_CALLS_ENABLED=False)")
    
    # Report optional service warnings
    for warning in optional_warnings:
        logger.warning(
            f"⚠️ {warning['service']}: {warning['error']}\n"
            f"   → {warning['help_url']}"
        )
    
    # Raise error if any core service failed
    if core_failures:
        raise ServiceConfigurationError(core_failures)
    
    logger.info("✓ All required services validated successfully")
