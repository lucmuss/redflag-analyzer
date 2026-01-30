"""
Management Command zum Seeden der Questions aus JSON
Verwendung: python manage.py seed_questions
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from questionnaire.models import Question


class Command(BaseCommand):
    help = 'Seed Questions from seed_data/questions.json'

    def handle(self, *args, **options):
        # Pfad zur JSON-Datei (lokal oder Docker)
        possible_paths = [
            Path('seed_data/questions.json'),  # Container: In /app/seed_data/
            Path('../seed_data/questions.json'),  # Lokal: Relatativ zu django_app/
            Path('questions.json'),  # Fallback: Im aktuellen Verzeichnis
        ]

        json_path = None
        for path in possible_paths:
            if path.exists():
                json_path = path
                self.stdout.write(self.style.SUCCESS(f'Found questions file at {json_path}'))
                break

        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'JSON file not found in any expected location'))
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        created_count = 0
        updated_count = 0
        
        for q_data in questions_data:
            # Mapping von initial_weight zu calculated_weight
            defaults = {
                'category': q_data['category'],
                'calculated_weight': q_data.get('initial_weight', 3.0),
                'text_de': q_data['text_de'],
                'text_en': q_data['text_en'],
                'is_active': True
            }
            
            question, created = Question.objects.update_or_create(
                key=q_data['key'],
                defaults=defaults
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {question.key}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {question.key}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeding complete! Created: {created_count}, Updated: {updated_count}, Total: {Question.objects.count()}'
        ))
