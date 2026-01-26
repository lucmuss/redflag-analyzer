"""
Management Command zum Hinzufügen kompakter Texte zu allen Questions
"""
from django.core.management.base import BaseCommand
from questionnaire.models import Question


class Command(BaseCommand):
    help = 'Fügt kompakte Texte zu allen Questions hinzu'

    # Mapping von question.key zu kompakten Texten
    SHORT_TEXTS = {
        'father_absence': {
            'de': 'Ohne biologischen Vater aufgewachsen',
            'en': 'Grew up without biological father'
        },
        'bad_father_relationship': {
            'de': 'Schlechte Vaterbeziehung',
            'en': 'Bad father relationship'
        },
        'dominant_mother': {
            'de': 'Dominante Mutter',
            'en': 'Dominant mother'
        },
        'feminist_blames_men': {
            'de': 'Feministin, macht Männer verantwortlich',
            'en': 'Feminist, blames men'
        },
        'single_mother_separated': {
            'de': 'Single Mutter (freiwillig getrennt)',
            'en': 'Single mother (voluntarily separated)'
        },
        'significantly_older': {
            'de': 'Deutlich älter (5+ Jahre)',
            'en': 'Significantly older (5+ years)'
        },
        'divorced_woman': {
            'de': 'Geschiedene Frau',
            'en': 'Divorced woman'
        },
        'high_bodycount': {
            'de': 'Hoher Bodycount',
            'en': 'High body count'
        },
        'early_sexual_experience': {
            'de': 'Frühes erstes Mal (12-16 Jahre)',
            'en': 'Early sexual experience (12-16)'
        },
        'party_girl_friends': {
            'de': 'Party Girl Freundinnen',
            'en': 'Party girl friends'
        },
        'social_media_active': {
            'de': 'Sehr aktiv auf Social Media',
            'en': 'Very active on social media'
        },
        'frequent_smartphone_use': {
            'de': 'Ständig am Smartphone',
            'en': 'Constantly on smartphone'
        },
        'cannot_relax': {
            'de': 'Kann nicht entspannen',
            'en': 'Cannot relax'
        },
        'bad_friend_circle': {
            'de': 'Moralisch schlechter Freundeskreis',
            'en': 'Morally bad friend circle'
        },
        'surrounded_by_men': {
            'de': 'Häufig von Männern umgeben',
            'en': 'Frequently surrounded by men'
        },
        'contact_with_ex': {
            'de': 'Regelmäßiger Kontakt zum Ex',
            'en': 'Regular contact with ex'
        },
        'toxic_ex': {
            'de': 'Toxischer/Badboy Ex',
            'en': 'Toxic/bad boy ex'
        },
        'career_priority': {
            'de': 'Karriere über Beziehung',
            'en': 'Career over relationship'
        },
        'masculine_energy': {
            'de': 'Maskuline Energie, dominant',
            'en': 'Masculine energy, dominant'
        },
        'strong_jealousy': {
            'de': 'Starke Eifersucht',
            'en': 'Strong jealousy'
        },
        'exaggerates_trivialities': {
            'de': 'Übertreibt Kleinigkeiten',
            'en': 'Exaggerates trivialities'
        },
        'frequent_nagging': {
            'de': 'Nörgelt häufig',
            'en': 'Nags frequently'
        },
        'heavily_tattooed': {
            'de': 'Stark tätowiert/gepierct',
            'en': 'Heavily tattooed/pierced'
        },
        'cosmetic_surgery': {
            'de': 'Schönheitsoperationen',
            'en': 'Cosmetic surgery'
        },
        'excessive_makeup': {
            'de': 'Übermäßig Make-Up',
            'en': 'Excessive makeup'
        },
        'short_hair': {
            'de': 'Kurze Haare (<10cm)',
            'en': 'Short hair (<10cm)'
        },
        'overweight': {
            'de': 'Stark übergewichtig',
            'en': 'Severely overweight'
        },
        'self_harm': {
            'de': 'Selbstverletzung',
            'en': 'Self-harm'
        },
        'talks_about_ex': {
            'de': 'Redet häufig über Ex',
            'en': 'Talks about ex frequently'
        },
        'drug_dependent': {
            'de': 'Drogen-/Medikamentenabhängig',
            'en': 'Drug/medication dependent'
        },
        'bad_with_money': {
            'de': 'Schlecht mit Geld',
            'en': 'Bad with money'
        },
        'spoiled_princess': {
            'de': 'Verwöhnt, wie Prinzessin',
            'en': 'Spoiled princess'
        },
        'early_baby_wish': {
            'de': 'Verfrühter Babywunsch',
            'en': 'Premature baby wish'
        },
        'lies_frequently': {
            'de': 'Lügt häufig',
            'en': 'Lies frequently'
        },
        'creates_insecurities': {
            'de': 'Ruft Unsicherheiten hervor',
            'en': 'Creates insecurities'
        },
        'she_is_the_prize': {
            'de': 'Sie ist der Preis, du nicht',
            'en': 'She is the prize, you are not'
        },
        'intimacy_as_reward': {
            'de': 'Intimität als Belohnung',
            'en': 'Intimacy as reward'
        },
        'public_humiliation': {
            'de': 'Stellt dich bloß',
            'en': 'Public humiliation'
        },
        'silent_treatment': {
            'de': 'Bestrafung mit Stille',
            'en': 'Silent treatment'
        },
        'no_responsibility': {
            'de': 'Keine Verantwortung',
            'en': 'No responsibility'
        },
        'trans_gender_fluid': {
            'de': 'Trans/Gender Fluid',
            'en': 'Trans/gender fluid'
        },
        'uses_gender_pronouns': {
            'de': 'Benutzt Gender-Pronomen',
            'en': 'Uses gender pronouns'
        },
        'dyed_hair': {
            'de': 'Unnatürlich gefärbte Haare',
            'en': 'Unnaturally dyed hair'
        },
        'ghosting_in_conflicts': {
            'de': 'Ghosting bei Konflikten',
            'en': 'Ghosting in conflicts'
        },
        'low_sex_drive': {
            'de': 'Niedriger Sexdrive',
            'en': 'Low sex drive'
        },
        'travels_alone': {
            'de': 'Reist viel alleine',
            'en': 'Travels alone frequently'
        },
        'long_dating_app_use': {
            'de': 'Lang auf Dating Apps',
            'en': 'Long on dating apps'
        },
        'thirst_traps': {
            'de': 'Postet Thirst Traps',
            'en': 'Posts thirst traps'
        },
        'long_term_single': {
            'de': 'Langzeit Single (4+ Jahre)',
            'en': 'Long-term single (4+ years)'
        },
        'fresh_single': {
            'de': 'Frischer Single (0-4 Monate)',
            'en': 'Fresh single (0-4 months)'
        },
        'many_short_relationships': {
            'de': 'Viele kurze Beziehungen',
            'en': 'Many short relationships'
        },
        'overreacts_to_problems': {
            'de': 'Überreagiert häufig',
            'en': 'Overreacts frequently'
        },
        'lacks_empathy': {
            'de': 'Wenig Empathie',
            'en': 'Lacks empathy'
        },
        'irritated_by_differing_opinions': {
            'de': 'Irritiert bei anderen Meinungen',
            'en': 'Irritated by differing opinions'
        },
        'one_sided_confidant': {
            'de': 'Einseitiger Vertrauter',
            'en': 'One-sided confidant'
        },
        'inconsistent_behavior': {
            'de': 'Inkonsistentes Verhalten',
            'en': 'Inconsistent behavior'
        },
        'cannot_handle_negative_emotions': {
            'de': 'Kann nicht mit neg. Gefühlen umgehen',
            'en': 'Cannot handle negative emotions'
        },
        'ignores_facts_logic': {
            'de': 'Ignoriert Fakten & Logik',
            'en': 'Ignores facts & logic'
        },
        'in_therapy': {
            'de': 'In psychologischer Therapie',
            'en': 'In psychological therapy'
        },
        'no_time_for_you': {
            'de': 'Häufig keine Zeit',
            'en': 'Often no time'
        },
        'gossips_about_others': {
            'de': 'Lästert häufig',
            'en': 'Gossips frequently'
        },
        'unreliable': {
            'de': 'Unzuverlässig',
            'en': 'Unreliable'
        },
        'low_self_confidence': {
            'de': 'Kein Selbstbewusstsein',
            'en': 'No self-confidence'
        },
        'low_intelligence_education': {
            'de': 'Mangelnde Intelligenz/Bildung',
            'en': 'Low intelligence/education'
        },
        'poor_communication': {
            'de': 'Schlechte Kommunikation',
            'en': 'Poor communication'
        },
    }

    def handle(self, *args, **kwargs):
        updated = 0
        not_found = 0
        
        for key, texts in self.SHORT_TEXTS.items():
            try:
                question = Question.objects.get(key=key)
                question.text_short_de = texts['de']
                question.text_short_en = texts['en']
                question.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Updated: {key}'))
            except Question.DoesNotExist:
                not_found += 1
                self.stdout.write(self.style.WARNING(f'✗ Not found: {key}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Updated {updated} questions'))
        if not_found > 0:
            self.stdout.write(self.style.WARNING(f'⚠ {not_found} questions not found'))
