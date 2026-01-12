"""
Django App Configuration for perplex project.
Runs health checks on startup.
"""
import sys
import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class PerplexConfig(AppConfig):
    """Main project configuration with startup health checks."""
    
    name = 'perplex'
    
    def ready(self):
        """
        Called when Django starts.
        Runs API health checks unless skipped or in migration/shell mode.
        """
        # Skip during migrations, shell, or test runs
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'shell', 'test']):
            return
        
        # Only run for server commands
        if not any(cmd in sys.argv for cmd in ['runserver', 'daphne', 'gunicorn', 'uvicorn']):
            return
        
        # Import here to avoid circular imports
        from perplex.services.health_check import validate_all_services
        
        logger.info("=" * 50)
        logger.info("MindMate-AI Starting...")
        logger.info("=" * 50)
        
        try:
            validate_all_services()
        except Exception as e:
            logger.error(str(e))
            raise
        
        logger.info("=" * 50)
        logger.info("Startup complete!")
        logger.info("=" * 50)
