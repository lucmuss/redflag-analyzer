# Generated migration for adding short text fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0004_update_scale_to_1_5'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='text_short_de',
            field=models.CharField(blank=True, help_text='Kompakte deutsche Version', max_length=100),
        ),
        migrations.AddField(
            model_name='question',
            name='text_short_en',
            field=models.CharField(blank=True, help_text='Short English version', max_length=100),
        ),
    ]
