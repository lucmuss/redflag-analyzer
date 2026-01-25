# Generated migration for Feedback app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_type', models.CharField(choices=[('bug', 'Bug Report'), ('feature', 'Feature Request'), ('improvement', 'Improvement Suggestion'), ('other', 'Other')], default='other', max_length=20)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('new', 'New'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('rejected', 'Rejected')], db_index=True, default='new', max_length=20)),
                ('admin_response', models.TextField(blank=True, null=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('responded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback_responses', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'feedbacks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['user', '-created_at'], name='feedbacks_user_id_7b9c8a_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['status', '-created_at'], name='feedbacks_status_6a3d4f_idx'),
        ),
    ]
