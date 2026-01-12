"""
Django settings for MindMate-AI Demo Project.

This is a DEMO/DEVELOPMENT project - not intended for production use.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Demo project settings - always in debug mode
SECRET_KEY = 'demo-project-secret-key-not-for-production'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Allow all hosts for demo

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Perplex config (first for startup checks)
    'perplex.apps.PerplexConfig',
    
    # Third-party apps
    'allauth',
    'allauth.account',
    'widget_tweaks',
    'channels',
    
    # Project apps
    'app',
    'accounts.apps.AccountsConfig',
    'voice_calls',
    'games',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'app.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'perplex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'perplex.wsgi.application'

# Database - SQLite for demo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Simplified password validation for demo
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static and Media files
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
LOGIN_REDIRECT_URL = 'complete-profile'
LOGOUT_REDIRECT_URL = '/'

# Email - Console for demo (no real email sending)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = 'none'

# =============================================================================
# API KEYS (from .env file)
# =============================================================================

# AI SERVICES CONFIGURATION
# =============================================================================

# Voice calls feature toggle
# Set to True to enable ElevenLabs + Twilio integration
VOICE_CALLS_ENABLED = os.getenv('VOICE_CALLS_ENABLED', 'False').lower() == 'true'

# Skip API health checks at startup (development only!)
# WARNING: Never set True in production
SKIP_HEALTH_CHECKS = os.getenv('SKIP_HEALTH_CHECKS', 'False').lower() == 'true'

# Rate limiting toggle (default disabled)
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'

# Celery beat interval for checking scheduled calls (seconds)
VOICE_CALL_CHECK_INTERVAL = int(os.getenv('VOICE_CALL_CHECK_INTERVAL', '60'))

# Google Gemini AI - for chatbot and quiz generation
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Cloudflare AI - for sentiment analysis
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')

# Twilio - for voice calls
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# ElevenLabs - for AI voice
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

# Ngrok - for voice call webhooks
NGROK_URL = os.getenv('NGROK_URL', '')

# =============================================================================
# CHANNELS & CELERY (Redis)
# =============================================================================

ASGI_APPLICATION = 'perplex.asgi.application'

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60