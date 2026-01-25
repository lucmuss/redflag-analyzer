# Generated manually for UserBadge gamification

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_extended_registration'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('badge_key', models.CharField(db_index=True, help_text='Eindeutiger Badge-Identifier', max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='🏆', max_length=10)),
                ('points', models.IntegerField(default=0)),
                ('earned_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_badges',
                'ordering': ['-earned_at'],
            },
        ),
        migrations.AddIndex(
            model_name='userbadge',
            index=models.Index(fields=['user', 'badge_key'], name='user_badges_user_id_a8c0a3_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userbadge',
            unique_together={('user', 'badge_key')},
        ),
    ]
