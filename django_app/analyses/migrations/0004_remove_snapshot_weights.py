# Generated migration to remove snapshot_weights field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0003_analysis_partner_country_alter_analysis_partner_age_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysis',
            name='snapshot_weights',
        ),
    ]
