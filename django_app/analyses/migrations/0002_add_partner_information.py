# Generated migration for partner information in Analysis

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='partner_name',
            field=models.CharField(blank=True, help_text='Name der analysierten Partnerin', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='analysis',
            name='partner_age',
            field=models.IntegerField(blank=True, help_text='Alter der Partnerin', null=True, validators=[django.core.validators.MinValueValidator(18), django.core.validators.MaxValueValidator(120)]),
        ),
    ]
