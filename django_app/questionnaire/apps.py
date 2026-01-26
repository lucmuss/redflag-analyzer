from django.apps import AppConfig
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class QuestionnaireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'questionnaire'
    
    def ready(self):
        # Importiere Signals für automatische Weight-Updates
        import questionnaire.signals
        
        # Berechne globale Gewichte beim Serverstart
        # Dies stellt sicher, dass calculated_weight immer aktuell ist
        try:
            # Verwende run_from_argv=False um nur einmal pro Prozess auszuführen
            # (nicht bei jedem reload im Development Mode)
            import sys
            if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
                logger.info('🔄 Berechne globale Gewichte beim Serverstart...')
                call_command('update_global_weights', verbosity=0)
                logger.info('✅ Globale Gewichte aktualisiert')
        except Exception as e:
            logger.warning(f'⚠️ Globale Gewichte konnten nicht beim Start berechnet werden: {e}')
