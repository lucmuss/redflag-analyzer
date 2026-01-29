"""
Management Command zum Seeden der Test-User mit Bewertungen aus JSON
Verwendung: python manage.py seed_test_users [--dry-run] [--limit=N]
"""
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from questionnaire.models import Question, WeightResponse

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Test Users from seed_data/users.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=int(os.environ.get('SEED_TEST_USERS_LIMIT', 24)),
            help=f'Maximum number of users to seed (default: {int(os.environ.get("SEED_TEST_USERS_LIMIT", 24))})',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        # Pfad zur JSON-Datei (prüfe verschiedene Orte)
        possible_paths = [
            Path('/app/users.json'),  # Für Render deployment
            Path('/app/seed_data/users.json'),  # Für lokal/docker-compose
        ]
        json_path = None
        for path in possible_paths:
            if path.exists():
                json_path = path
                break

        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'JSON file not found at {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        self.stdout.write(self.style.WARNING(f'Found {len(users_data)} test users in JSON'))

        # Limitiere die Anzahl der zu importierenden User
        limit = options.get('limit', 24)
        if limit < len(users_data):
            users_data = users_data[:limit]
            self.stdout.write(self.style.WARNING(f'🔢 Limiting to first {limit} users'))

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))

        # Sammle Statistiken
        created_users = 0
        updated_users = 0
        created_weight_responses = 0
        updated_weight_responses = 0

        for user_data in users_data:
            email = user_data['email']
            password = user_data['password']

            if dry_run:
                self.stdout.write(f'DRY RUN: Would process user {user_data.get("first_name", email)}')
                continue

            try:
                # Erstelle oder aktualisiere User
                user, user_created = User.objects.update_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0],
                        'first_name': user_data.get('first_name', ''),
                        'last_name': user_data.get('last_name', ''),
                        'is_staff': user_data.get('is_staff', False),
                        'is_active': user_data.get('is_active', True),
                    }
                )

                # Setze Passwort falls nötig
                if user_created or not user.has_usable_password():
                    user.set_password(password)
                    user.save()

                if user_created:
                    created_users += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Created user: {email}'))
                else:
                    updated_users += 1
                    self.stdout.write(self.style.WARNING(f'↻ Updated user: {email}'))

                # Erstelle oder aktualisiere UserProfile
                profile_defaults = {}
                if user_data.get('birth_date'):
                    from datetime import datetime
                    try:
                        profile_defaults['birthdate'] = datetime.strptime(user_data['birth_date'], '%Y-%m-%d').date()
                    except:
                        pass
                if user_data.get('country'):
                    profile_defaults['country'] = 'DE' if user_data['country'] == 'Deutschland' else user_data['country'][:2]
                if user_data.get('gender'):
                    profile_defaults['gender'] = user_data['gender']

                if profile_defaults:
                    UserProfile.objects.update_or_create(
                        user=user,
                        defaults=profile_defaults
                    )

                # Verarbeite ratings_answers (WeightResponse)
                ratings_answers = user_data.get('ratings_answers', {})
                for question_key, importance in ratings_answers.items():
                    try:
                        question = Question.objects.get(key=question_key, is_active=True)
                        weight_response, created = WeightResponse.objects.update_or_create(
                            user=user,
                            question=question,
                            defaults={'importance': importance}
                        )

                        if created:
                            created_weight_responses += 1
                        else:
                            updated_weight_responses += 1

                    except Question.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'⚠ Question not found: {question_key}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to process {email}: {e}'))

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Seeding complete!'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Users: Created {created_users}, Updated {updated_users}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Weight Responses: Created {created_weight_responses}, Updated {updated_weight_responses}'
            ))

            # Finale Statistiken
            total_users = User.objects.count()
            total_responses = WeightResponse.objects.count()
            completed_users = sum(1 for u in User.objects.all()
                                 if WeightResponse.has_completed_importance_questionnaire(u))

            self.stdout.write(self.style.SUCCESS(
                f'Total Users: {total_users} | Completed Questionnaires: {completed_users}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n🔍 Dry run complete - processed {len(users_data)} users'))