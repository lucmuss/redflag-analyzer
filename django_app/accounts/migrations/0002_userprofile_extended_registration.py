# Generated manually for extended registration fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='relationship_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('in_relationship', 'In einer Beziehung'), ('married', 'Verheiratet'), ('divorced', 'Geschieden'), ('complicated', 'Es ist kompliziert')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='previous_relationships_count',
            field=models.CharField(blank=True, choices=[('0', 'Keine'), ('1-3', '1-3'), ('4-7', '4-7'), ('8+', '8+')], help_text='Anzahl bisheriger Beziehungen', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_relationship_duration',
            field=models.IntegerField(blank=True, help_text='Dauer in Monaten', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='referral_source',
            field=models.CharField(blank=True, choices=[('google', 'Google Suche'), ('social_media', 'Social Media'), ('friend', 'Freund/Bekannter'), ('advertisement', 'Werbung'), ('other', 'Sonstiges')], help_text='Wie hast du von uns erfahren?', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='education',
            field=models.CharField(blank=True, choices=[('hauptschule', 'Hauptschule'), ('realschule', 'Realschule'), ('abitur', 'Abitur'), ('bachelor', 'Bachelor'), ('master', 'Master'), ('phd', 'PhD/Doktor')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, help_text='Wohnort (Stadt)', max_length=100, null=True),
        ),
    ]
