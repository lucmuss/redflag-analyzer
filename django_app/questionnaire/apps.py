from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.conf import settings
import logging
import os
import json

logger = logging.getLogger(__name__)


class QuestionnaireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'questionnaire'

    def ready(self):
        # Importiere Signals für automatische Weight-Updates
        import questionnaire.signals

        # Registriere post_migrate für Seed-Import
        post_migrate.connect(self._post_migrate_handler, sender=self)

        # Berechne globale Gewichte beim Serverstart (auskommentiert - verursacht Startup-Hang)
        # TODO: In post_migrate oder middleware verschieben
        # try:
        #     import sys
        #     if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
        #         logger.info('🔄 Berechne globale Gewichte beim Serverstart...')
        #         call_command('update_global_weights', verbosity=0)
        #         logger.info('✅ Globale Gewichte aktualisiert')
        # except Exception as e:
        #     logger.warning(f'⚠️ Globale Gewichte konnten nicht beim Start berechnet werden: {e}')

    def _post_migrate_handler(self, sender, **kwargs):
        """Importiere Fragen nach Migration, wenn leer."""
        from .models import Question  # Lazy import

        if Question.objects.count() > 0:
            return  # Fragen bereits vorhanden

        try:
            seed_file = os.path.join(settings.BASE_DIR, '..', 'seed_data', 'questions.json')
            if not os.path.exists(seed_file):
                logger.warning(f'⚠️ Seed-Datei nicht gefunden: {seed_file}')
                return

            with open(seed_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)

            questions_created = 0
            for q in questions_data:
                Question.objects.create(
                    key=q['key'],
                    category=q['category'],
                    text_de=q['text_de'],
                    text_en=q['text_en'],
                    calculated_weight=float(q.get('initial_weight', 3.0))
                )
                questions_created += 1

            logger.info(f'✅ {questions_created} Fragen aus seed_data importiert')

        except Exception as e:
            logger.error(f'❌ Fehler beim Importieren der Fragen: {e}')
