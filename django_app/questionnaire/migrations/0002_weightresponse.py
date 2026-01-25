# Generated migration for WeightResponse model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questionnaire', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importance', models.IntegerField(help_text="User's importance rating (1-10)", validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weight_responses', to='questionnaire.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weight_responses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'weight_responses',
                'ordering': ['question__category', 'question__key'],
            },
        ),
        migrations.AddIndex(
            model_name='weightresponse',
            index=models.Index(fields=['user', 'question'], name='weight_resp_user_id_cd5e8f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='weightresponse',
            unique_together={('user', 'question')},
        ),
    ]
