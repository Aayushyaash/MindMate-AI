"""
Backward compatibility re-exports.
DEPRECATED: Import from perplex.services instead.
"""
from perplex.services import get_elevenlabs_service, get_twilio_service

# Deprecated aliases - will be removed in future version
def ElevenLabsService():
    import warnings
    warnings.warn(
        "ElevenLabsService() is deprecated. Use get_elevenlabs_service() from perplex.services",
        DeprecationWarning
    )
    return get_elevenlabs_service()

def TwilioService():
    import warnings
    warnings.warn(
        "TwilioService() is deprecated. Use get_twilio_service() from perplex.services",
        DeprecationWarning
    )
    return get_twilio_service()